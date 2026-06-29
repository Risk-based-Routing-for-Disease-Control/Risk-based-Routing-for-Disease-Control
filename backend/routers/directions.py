import hashlib
import json

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from services.db import get_cursor
from services.naver_client import NaverDirectionsError, get_multi_stop_route, get_route

router = APIRouter(tags=["directions"])


@router.get("/directions")
async def get_directions(
    start_lat: float = Query(...),
    start_lng: float = Query(...),
    goal_lat: float = Query(...),
    goal_lng: float = Query(...),
    waypoints: str | None = Query(
        None,
        description="경유지 좌표, 'lat,lng;lat,lng' 형식 (선택, 최대 5개)",
    ),
):
    """네이버 Directions 5 API로 자동차 경로를 조회해 프론트엔드 Polyline 형태로 변환한다."""
    start = f"{start_lng},{start_lat}"
    goal = f"{goal_lng},{goal_lat}"

    naver_waypoints = None
    if waypoints:
        try:
            naver_waypoints = "|".join(
                f"{float(lng):.6f},{float(lat):.6f}"
                for lat, lng in (chunk.split(",") for chunk in waypoints.split(";") if chunk)
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail="waypoints 형식이 올바르지 않습니다. 'lat,lng;lat,lng' 형식으로 입력하세요.",
            ) from exc

    try:
        result = await get_route(start=start, goal=goal, waypoints=naver_waypoints)
    except NaverDirectionsError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    path = [{"lat": point[1], "lng": point[0]} for point in result["path"]]

    return {
        "path": path,
        "distance": result["distance"],
        "duration": result["duration"],
    }


class RoutePoint(BaseModel):
    lat: float
    lng: float
    name: str | None = None


class MultiStopRouteRequest(BaseModel):
    points: list[RoutePoint] = Field(..., min_length=2, description="방문 순서대로 정렬된 좌표 리스트")


class LatLngPoint(BaseModel):
    lat: float
    lng: float


class RouteLeg(BaseModel):
    from_: RoutePoint = Field(..., alias="from")
    to: RoutePoint
    distance: float
    duration: float
    path: list[LatLngPoint]


class MultiStopRouteResponse(BaseModel):
    totalDistance: float
    totalDuration: float
    legs: list[RouteLeg]


@router.get("/routes")
async def get_routes(
    startLat: float = Query(...),
    startLng: float = Query(...),
    endLat: float = Query(...),
    endLng: float = Query(...),
):
    """경로 조회. directions_cache 히트 시 DB에서 반환, 미스 시 Naver API 호출 후 캐시 저장."""
    cache_key = hashlib.md5(f"{startLat},{startLng}:{endLat},{endLng}".encode()).hexdigest()

    with get_cursor() as cur:
        cur.execute(
            """
            SELECT rl.distance_meters, rl.duration_millis, rl.path_json, rl.provider
            FROM directions_cache dc
            JOIN route_legs rl ON dc.cache_key = rl.cache_key
            WHERE dc.cache_key = %s
            LIMIT 1
            """,
            (cache_key,),
        )
        cached = cur.fetchone()

    if cached:
        return {
            "distance": cached["distance_meters"],
            "duration": cached["duration_millis"],
            "path": cached["path_json"],
            "provider": cached["provider"],
            "cached": True,
        }

    start = f"{startLng},{startLat}"
    goal = f"{endLng},{endLat}"
    try:
        result = await get_route(start=start, goal=goal)
    except NaverDirectionsError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO directions_cache (cache_key, start_lat, start_lng, end_lat, end_lng, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            ON CONFLICT (cache_key) DO NOTHING
            """,
            (cache_key, startLat, startLng, endLat, endLng),
        )
        cur.execute(
            """
            INSERT INTO route_legs (cache_key, distance_meters, duration_millis, path_json, provider)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (cache_key, result["distance"], result["duration"], json.dumps(result["path"]), "naver"),
        )

    return {
        "distance": result["distance"],
        "duration": result["duration"],
        "path": result["path"],
        "provider": "naver",
        "cached": False,
    }


@router.post("/directions/multi", response_model=MultiStopRouteResponse)
async def get_multi_stop_directions(request: MultiStopRouteRequest):
    """여러 지점을 순서대로 방문하는 경로를 구간(레그)별 거리/시간과 함께 조회한다."""
    points = [point.model_dump() for point in request.points]

    try:
        result = await get_multi_stop_route(points)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except NaverDirectionsError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return result
