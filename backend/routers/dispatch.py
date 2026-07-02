from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.databricks_client import get_farms_from_db
from services.db import get_cursor
from services.disinfection_facilities import load_disinfection_facilities
from services.dispatch_optimizer import DispatchOptions, farm_from_dict, solve_dispatch

router = APIRouter(tags=["dispatch"])


def _name_lookup_maps() -> tuple[dict[str, str], dict[str, str]]:
    """farm_id -> name, facility_id -> name 조회용 맵을 생성한다.

    dispatch_stops.name(비정규화 컬럼, 과거 버그 대응으로 추가됨)에 의존하지 않고
    조회 시점 최신 이름을 반영하기 위함.
    """
    farm_names = {str(f.get("id")): f.get("name", "") for f in get_farms_from_db()}
    facility_names = {f.id: f.name for f in load_disinfection_facilities()}
    return farm_names, facility_names


def _resolve_stop_name(row: dict, farm_names: dict[str, str], facility_names: dict[str, str]) -> str:
    if row["farm_id"] is not None:
        return farm_names.get(row["farm_id"], row.get("name") or row["farm_id"])
    if row["facility_id"] is not None:
        return facility_names.get(row["facility_id"], row.get("name") or row["facility_id"])
    return row.get("name") or ""


# ── 기존 엔드포인트 (DB 데이터 준비 전까지 유지) ──────────────────────────────

class DispatchSolveRequest(BaseModel):
    selectedFarmIds: list[str] = Field(default_factory=list)
    teamCount: int = Field(3, ge=1)
    farms: list[dict[str, Any]] | None = None
    depotName: str | None = None
    depotLat: float | None = None
    depotLng: float | None = None


@router.post("/dispatch/solve")
async def solve_dispatch_route(request: DispatchSolveRequest):
    source_farms = request.farms if request.farms is not None else get_farms_from_db()
    selected_ids = set(request.selectedFarmIds)
    selected = [
        farm_from_dict(farm)
        for farm in source_farms
        if not selected_ids or str(farm.get("id")) in selected_ids
    ]

    try:
        options_kwargs: dict[str, Any] = {"team_count": request.teamCount}
        if request.depotName is not None:
            options_kwargs["depot_name"] = request.depotName
        if request.depotLat is not None:
            options_kwargs["depot_lat"] = request.depotLat
        if request.depotLng is not None:
            options_kwargs["depot_lng"] = request.depotLng
        return await solve_dispatch(selected, DispatchOptions(**options_kwargs))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


# ── 신규 엔드포인트 (ERD v2 명세) ─────────────────────────────────────────────

class RouteAssignmentRequest(BaseModel):
    teamCount: int = Field(..., ge=1)
    farmIds: list[str]
    farms: list[dict[str, Any]] | None = None  # DB 전환 전 프론트 farm 객체 직접 수신용
    depotName: str = "공통 방역 출발지"
    depotLat: float = 37.1995
    depotLng: float = 126.8310
    maxRouteMinutes: int = 480
    disinfectServiceMinutes: int = 20
    allowUnassigned: bool = True


def _determine_status(teams: list, unassigned: list) -> str:
    if not teams and unassigned:
        return "FAILED"
    if unassigned:
        return "PARTIAL"
    return "SUCCESS"


def _build_stops_response(
    optimizer_stops: list[dict], disinfect_minutes: int
) -> tuple[list[dict], list[tuple]]:
    """optimizer 출력의 stops → 스펙 stops 변환.
    farm visit과 disinfection hub visit을 별도 stop으로 분리한다.
    반환: (stops_response, db_rows)  db_rows는 INSERT용 튜플 리스트.
    """
    stops_response: list[dict] = []
    db_rows: list[tuple] = []
    order = 1

    for s in optimizer_stops:
        farm = s["farm"]
        farm_row = (order, farm["id"], None, farm["estimatedDurationMinutes"], farm["name"])
        stops_response.append(
            {
                "stopOrder": order,
                "farmId": farm["id"],
                "facilityId": None,
                "name": farm["name"],
                "estimatedDuration": farm["estimatedDurationMinutes"],
                "status": "upcoming",
                "completedAt": None,
                "cancelledAt": None,
                "actualDurationMinutes": None,
            }
        )
        db_rows.append(farm_row)
        order += 1

        hub = s.get("disinfectionHub")
        if hub:
            hub_row = (order, None, hub["id"], disinfect_minutes, hub["name"])
            stops_response.append(
                {
                    "stopOrder": order,
                    "farmId": None,
                    "facilityId": hub["id"],
                    "name": hub["name"],
                    "estimatedDuration": disinfect_minutes,
                    "status": "upcoming",
                    "completedAt": None,
                    "cancelledAt": None,
                    "actualDurationMinutes": None,
                }
            )
            db_rows.append(hub_row)
            order += 1

    return stops_response, db_rows


@router.post("/route-assignment")
async def route_assignment(request: RouteAssignmentRequest):
    """배차 최적화 실행 후 결과를 DB에 저장하고 dispatchRunId를 반환한다."""
    source_farms = request.farms if request.farms else get_farms_from_db()
    id_set = set(request.farmIds)
    selected = [farm_from_dict(f) for f in source_farms if str(f.get("id")) in id_set]
    if not selected:
        raise HTTPException(status_code=400, detail="유효한 농장 ID가 없습니다.")

    options = DispatchOptions(
        team_count=request.teamCount,
        max_route_minutes=request.maxRouteMinutes,
        disinfect_service_minutes=request.disinfectServiceMinutes,
        allow_unassigned=request.allowUnassigned,
        depot_name=request.depotName,
        depot_lat=request.depotLat,
        depot_lng=request.depotLng,
    )
    try:
        result = await solve_dispatch(selected, options)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    dispatch_run_id = str(uuid.uuid4())
    status = _determine_status(result["teams"], result["unassignedFarms"])
    total_duration = result["totalDurationMinutes"]

    teams_response: list[dict] = []
    unassigned_response: list[dict] = []

    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO dispatch_runs
                (dispatch_run_id, team_count, depot_name, depot_lat, depot_lng,
                 max_route_minutes, disinfect_service_minutes, allow_unassigned,
                 status, total_duration_minutes, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """,
            (
                dispatch_run_id, request.teamCount, request.depotName,
                request.depotLat, request.depotLng, request.maxRouteMinutes,
                request.disinfectServiceMinutes, request.allowUnassigned,
                status, total_duration,
            ),
        )

        for team in result["teams"]:
            team_id = str(uuid.uuid4())
            team_no = int(team["id"].split("-")[1])
            cur.execute(
                """
                INSERT INTO dispatch_teams
                    (dispatch_team_id, dispatch_run_id, team_no, team_label, color, total_duration_minutes)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (team_id, dispatch_run_id, team_no, team["label"], team["color"], team["totalDurationMinutes"]),
            )

            stops_resp, db_rows = _build_stops_response(team["stops"], request.disinfectServiceMinutes)
            for stop_order, farm_id, facility_id, duration, name in db_rows:
                cur.execute(
                    """
                    INSERT INTO dispatch_stops
                        (dispatch_team_id, dispatch_run_id, stop_order, farm_id, facility_id,
                         planned_duration_minutes, name)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (team_id, dispatch_run_id, stop_order, farm_id, facility_id, duration, name),
                )

            teams_response.append(
                {
                    "teamId": team_id,
                    "teamNo": team_no,
                    "teamLabel": team["label"],
                    "color": team["color"],
                    "totalDuration": team["totalDurationMinutes"],
                    "stops": stops_resp,
                }
            )

        for farm in result["unassignedFarms"]:
            reason = "TIME_CONSTRAINT_EXCEEDED"
            cur.execute(
                "INSERT INTO dispatch_unassigned_farms (dispatch_run_id, farm_id, reason) VALUES (%s, %s, %s)",
                (dispatch_run_id, farm["id"], reason),
            )
            unassigned_response.append({"farmId": farm["id"], "reason": reason})

    return {
        "dispatchRunId": dispatch_run_id,
        "status": status,
        "totalEstimatedDuration": total_duration,
        "teams": teams_response,
        "unassignedFarms": unassigned_response,
    }


@router.get("/dispatch-runs/{dispatch_run_id}")
def get_dispatch_run(dispatch_run_id: str):
    """저장된 배차 결과를 재조회한다."""
    with get_cursor() as cur:
        cur.execute(
            "SELECT * FROM dispatch_runs WHERE dispatch_run_id = %s",
            (dispatch_run_id,),
        )
        run = cur.fetchone()
        if run is None:
            raise HTTPException(status_code=404, detail=f"배차 결과를 찾을 수 없습니다: {dispatch_run_id}")

        cur.execute(
            "SELECT * FROM dispatch_teams WHERE dispatch_run_id = %s ORDER BY team_no",
            (dispatch_run_id,),
        )
        teams = cur.fetchall()

        farm_names, facility_names = _name_lookup_maps()

        teams_response = []
        for team in teams:
            cur.execute(
                "SELECT * FROM dispatch_stops WHERE dispatch_team_id = %s ORDER BY stop_order",
                (team["dispatch_team_id"],),
            )
            stops = cur.fetchall()
            teams_response.append(
                {
                    "teamId": team["dispatch_team_id"],
                    "teamNo": team["team_no"],
                    "teamLabel": team["team_label"],
                    "color": team["color"],
                    "totalDuration": team["total_duration_minutes"],
                    "stops": [
                        {
                            "stopOrder": s["stop_order"],
                            "farmId": s["farm_id"],
                            "facilityId": s["facility_id"],
                            "name": _resolve_stop_name(s, farm_names, facility_names),
                            "estimatedDuration": s["planned_duration_minutes"],
                            "status": s["status"],
                            "completedAt": s["completed_at"].isoformat() if s["completed_at"] else None,
                            "cancelledAt": s["cancelled_at"].isoformat() if s["cancelled_at"] else None,
                            "actualDurationMinutes": s["actual_duration_minutes"],
                        }
                        for s in stops
                    ],
                }
            )

        cur.execute(
            "SELECT farm_id, reason FROM dispatch_unassigned_farms WHERE dispatch_run_id = %s",
            (dispatch_run_id,),
        )
        unassigned = [{"farmId": r["farm_id"], "reason": r["reason"]} for r in cur.fetchall()]

    return {
        "dispatchRunId": run["dispatch_run_id"],
        "status": run["status"],
        "totalEstimatedDuration": run["total_duration_minutes"],
        "teams": teams_response,
        "unassignedFarms": unassigned,
    }


class CompleteStopRequest(BaseModel):
    actualDurationMinutes: int = Field(..., ge=1, le=600)


def _stop_response(row: dict, farm_names: dict[str, str], facility_names: dict[str, str]) -> dict:
    return {
        "stopOrder": row["stop_order"],
        "farmId": row["farm_id"],
        "facilityId": row["facility_id"],
        "name": _resolve_stop_name(row, farm_names, facility_names),
        "estimatedDuration": row["planned_duration_minutes"],
        "status": row["status"],
        "completedAt": row["completed_at"].isoformat() if row["completed_at"] else None,
        "cancelledAt": row["cancelled_at"].isoformat() if row["cancelled_at"] else None,
        "actualDurationMinutes": row["actual_duration_minutes"],
    }


@router.patch("/dispatch-runs/{dispatch_run_id}/teams/{team_id}/stops/{farm_id}/complete")
def complete_stop(dispatch_run_id: str, team_id: str, farm_id: str, request: CompleteStopRequest):
    """모바일 필드 화면에서 농장 방문 완료 처리를 서버에 반영한다."""
    with get_cursor() as cur:
        cur.execute(
            """
            UPDATE dispatch_stops
            SET status = 'completed', completed_at = NOW(), cancelled_at = NULL,
                actual_duration_minutes = %s
            WHERE dispatch_run_id = %s AND dispatch_team_id = %s AND farm_id = %s
            RETURNING *
            """,
            (request.actualDurationMinutes, dispatch_run_id, team_id, farm_id),
        )
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="해당 방문 지점을 찾을 수 없습니다.")
    farm_names, facility_names = _name_lookup_maps()
    return _stop_response(row, farm_names, facility_names)


@router.patch("/dispatch-runs/{dispatch_run_id}/teams/{team_id}/stops/{farm_id}/cancel")
def cancel_stop(dispatch_run_id: str, team_id: str, farm_id: str):
    """완료 처리를 취소하고 다시 방문 예정 상태로 되돌린다."""
    with get_cursor() as cur:
        cur.execute(
            """
            UPDATE dispatch_stops
            SET status = 'upcoming', completed_at = NULL, actual_duration_minutes = NULL,
                cancelled_at = NOW()
            WHERE dispatch_run_id = %s AND dispatch_team_id = %s AND farm_id = %s
            RETURNING *
            """,
            (dispatch_run_id, team_id, farm_id),
        )
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="해당 방문 지점을 찾을 수 없습니다.")
    farm_names, facility_names = _name_lookup_maps()
    return _stop_response(row, farm_names, facility_names)
