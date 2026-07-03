from __future__ import annotations

from contextlib import redirect_stdout
from dataclasses import dataclass, replace
import io
import math
import random
from typing import Any, Literal


from services.disinfection_facilities import DisinfectionFacility, load_disinfection_facilities
from services.experiments.clustering.risk_clustering_v2 import risk_clustering_v2
from services.experiments.absorb_unvisited_reopt import absorb_unvisited_reopt
from services.osrm_client import OsrmPoint, build_osrm_duration_matrix


# NOTE: The optimizer uses risk_clustering_v2 for team buckets, then ALNS per
# team to maximize covered risk within the route-time limit.

RiskLevel = Literal["warning", "high", "critical"]

TEAM_COLORS = ["#1565C0", "#8E24AA", "#00897B", "#EF6C00", "#5E35B1", "#2E7D32"]
DEFAULT_DEPOT_NAME = "공통 방역 출발지"
DEFAULT_DEPOT_LAT = 37.1995
DEFAULT_DEPOT_LNG = 126.8310
DEFAULT_FARM_SERVICE_MINUTES = 90
MIN_FARM_SERVICE_MINUTES = 60
BASE_LIVESTOCK_COUNT = 10_000
BASE_FARM_SERVICE_MINUTES = 90
ADDITIONAL_MINUTES_PER_10K_LIVESTOCK = 35
SERVICE_ROUNDING_MINUTES = 10
RANDOM_SEED = 42
DEPOT_ID = "depot"


def _round_up_minutes(value: float, unit: int = SERVICE_ROUNDING_MINUTES) -> int:
    return int(math.ceil((value - 1e-9) / unit) * unit)


def calculate_farm_service_minutes(livestock_count: int | float | None) -> int:
    """Estimate regular surveillance time from interview-based field guidance.

    The interview baseline is 1-2 hours for routine farm surveillance, about
    90 minutes for 10,000 poultry, then 30-40 more minutes per additional
    10,000. Unknown livestock counts use the 10,000-head baseline to avoid
    underestimating dispatch workload.
    """
    count = max(0.0, float(livestock_count or 0))
    if count <= 0:
        return DEFAULT_FARM_SERVICE_MINUTES
    if count <= BASE_LIVESTOCK_COUNT:
        scaled = MIN_FARM_SERVICE_MINUTES + (count / BASE_LIVESTOCK_COUNT) * (
            BASE_FARM_SERVICE_MINUTES - MIN_FARM_SERVICE_MINUTES
        )
        return _round_up_minutes(scaled)

    extra_units = math.ceil((count - BASE_LIVESTOCK_COUNT) / BASE_LIVESTOCK_COUNT)
    return BASE_FARM_SERVICE_MINUTES + int(extra_units * ADDITIONAL_MINUTES_PER_10K_LIVESTOCK)


@dataclass(frozen=True)
class DispatchFarm:
    id: str
    name: str
    lat: float
    lng: float
    risk_score: float
    risk_level: RiskLevel
    code: str = ""
    livestock_type: str = "미상"
    livestock_count: int = 0
    livestock_unit: str = "두"
    estimated_duration_minutes: int = DEFAULT_FARM_SERVICE_MINUTES
    address: str = ""
    xai_factors: list[dict[str, Any]] | None = None
    last_updated_at: str = ""


@dataclass(frozen=True)
class DispatchOptions:
    team_count: int
    max_route_minutes: int = 8 * 60
    farm_service_minutes: int = DEFAULT_FARM_SERVICE_MINUTES
    disinfect_service_minutes: int = 8
    search_time_limit_seconds: int = 10
    allow_unassigned: bool = True
    depot_name: str = DEFAULT_DEPOT_NAME
    depot_lat: float = DEFAULT_DEPOT_LAT
    depot_lng: float = DEFAULT_DEPOT_LNG


def farm_from_dict(data: dict[str, Any]) -> DispatchFarm:
    livestock_count = int(data.get("livestockCount", data.get("livestock_count", 0)) or 0)
    return DispatchFarm(
        id=str(data["id"]),
        code=str(data.get("code") or data.get("farmCode") or data["id"]),
        name=str(data.get("name") or data["id"]),
        lat=float(data["lat"]),
        lng=float(data["lng"]),
        risk_score=float(data.get("riskScore", data.get("risk_score", 0))),
        risk_level=data.get("riskLevel", data.get("risk_level", "warning")),
        livestock_type=str(data.get("livestockType", data.get("livestock_type", "미상"))),
        livestock_count=livestock_count,
        livestock_unit=str(data.get("livestockUnit", data.get("livestock_unit", "두"))),
        estimated_duration_minutes=calculate_farm_service_minutes(livestock_count),
        address=str(data.get("address", "")),
        xai_factors=list(data.get("xaiFactors", data.get("xai_factors", [])) or []),
        last_updated_at=str(data.get("lastUpdatedAt", data.get("last_updated_at", ""))),
    )


def farm_to_response(farm: DispatchFarm) -> dict[str, Any]:
    return {
        "id": farm.id,
        "code": farm.code,
        "name": farm.name,
        "lat": farm.lat,
        "lng": farm.lng,
        "riskScore": farm.risk_score,
        "riskLevel": farm.risk_level,
        "livestockType": farm.livestock_type,
        "livestockCount": farm.livestock_count,
        "livestockUnit": farm.livestock_unit,
        "estimatedDurationMinutes": farm.estimated_duration_minutes,
        "address": farm.address,
        "xaiFactors": farm.xai_factors or [],
        "lastUpdatedAt": farm.last_updated_at,
    }


@dataclass(frozen=True)
class AlnsContext:
    max_time: int
    disinfect_service_minutes: int
    time_matrix: dict[str, dict[str, int]]
    farm_map: dict[str, DispatchFarm]
    disinfection_map: dict[str, DisinfectionFacility]


def _service_minutes(farm: DispatchFarm, options: DispatchOptions) -> int:
    return farm.estimated_duration_minutes or options.farm_service_minutes


def _travel_time(ctx: AlnsContext, from_id: str, to_id: str) -> int:
    return ctx.time_matrix[from_id][to_id]


def _best_disinfection_for_leg(
    current_farm_id: str,
    next_node_id: str,
    ctx: AlnsContext,
) -> DisinfectionFacility:
    return min(
        ctx.disinfection_map.values(),
        key=lambda facility: (
            _travel_time(ctx, current_farm_id, facility.id)
            + _travel_time(ctx, facility.id, next_node_id)
        ),
    )


def _leg_minutes(
    ctx: AlnsContext,
    options: DispatchOptions,
    from_id: str,
    to_id: str,
) -> int:
    if from_id not in ctx.farm_map:
        return _travel_time(ctx, from_id, to_id)

    hub = _best_disinfection_for_leg(from_id, to_id, ctx)
    return (
        _service_minutes(ctx.farm_map[from_id], options)
        + _travel_time(ctx, from_id, hub.id)
        + ctx.disinfect_service_minutes
        + _travel_time(ctx, hub.id, to_id)
    )


def route_minutes(route: list[str], ctx: AlnsContext, options: DispatchOptions) -> int:
    return sum(_leg_minutes(ctx, options, route[index], route[index + 1]) for index in range(len(route) - 1))


def route_risk(route: list[str], ctx: AlnsContext) -> float:
    return round(sum(ctx.farm_map[node_id].risk_score for node_id in route if node_id in ctx.farm_map), 3)


def _insertion_delta(route: list[str], candidate: str, pos: int, ctx: AlnsContext, options: DispatchOptions) -> int:
    before = route_minutes(route, ctx, options)
    trial = route[:pos] + [candidate] + route[pos:]
    return route_minutes(trial, ctx, options) - before


def _best_feasible_insert(
    route: list[str],
    candidate: str,
    ctx: AlnsContext,
    options: DispatchOptions,
) -> tuple[int | None, int]:
    best_pos: int | None = None
    best_delta = math.inf
    for pos in range(1, len(route)):
        delta = _insertion_delta(route, candidate, pos, ctx, options)
        trial = route[:pos] + [candidate] + route[pos:]
        if delta < best_delta and route_minutes(trial, ctx, options) <= ctx.max_time:
            best_delta = delta
            best_pos = pos
    return best_pos, int(best_delta) if best_pos is not None else 0


def greedy_route(farm_ids: list[str], ctx: AlnsContext, options: DispatchOptions) -> list[str]:
    unvisited = list(farm_ids)
    route = [DEPOT_ID, DEPOT_ID]
    while unvisited:
        best_farm: str | None = None
        best_score = -1.0
        best_pos: int | None = None
        for farm_id in unvisited:
            pos, delta = _best_feasible_insert(route, farm_id, ctx, options)
            if pos is None:
                continue
            score = ctx.farm_map[farm_id].risk_score / max(delta, 1)
            if score > best_score:
                best_farm = farm_id
                best_score = score
                best_pos = pos
        if best_farm is None or best_pos is None:
            break
        route = route[:best_pos] + [best_farm] + route[best_pos:]
        unvisited.remove(best_farm)
    return route


def _destroy_by_risk(route: list[str], n: int, ctx: AlnsContext) -> tuple[list[str], list[str]]:
    farms = [node_id for node_id in route if node_id in ctx.farm_map]
    by_risk = sorted(farms, key=lambda node_id: ctx.farm_map[node_id].risk_score)
    pool = by_risk[: max(1, len(by_risk) // 2)]
    removed = random.sample(pool, min(n, len(pool)))
    return [node_id for node_id in route if node_id not in removed], removed


def _destroy_by_cost(
    route: list[str],
    n: int,
    ctx: AlnsContext,
    options: DispatchOptions,
) -> tuple[list[str], list[str]]:
    farms = [node_id for node_id in route if node_id in ctx.farm_map]
    if len(farms) < 2:
        return _destroy_by_risk(route, n, ctx)

    efficiencies: list[tuple[str, float]] = []
    current_minutes = route_minutes(route, ctx, options)
    for farm_id in farms:
        trial = [node_id for node_id in route if node_id != farm_id]
        saved = current_minutes - route_minutes(trial, ctx, options)
        efficiency = ctx.farm_map[farm_id].risk_score / max(saved, 1)
        efficiencies.append((farm_id, efficiency))

    efficiencies.sort(key=lambda item: item[1])
    pool = [farm_id for farm_id, _ in efficiencies[: max(1, len(efficiencies) // 2)]]
    removed = random.sample(pool, min(n, len(pool)))
    return [node_id for node_id in route if node_id not in removed], removed


def _destroy_random(route: list[str], n: int, ctx: AlnsContext) -> tuple[list[str], list[str]]:
    farms = [node_id for node_id in route if node_id in ctx.farm_map]
    removed = random.sample(farms, min(n, len(farms)))
    return [node_id for node_id in route if node_id not in removed], removed


def _insert_candidates(
    route: list[str],
    candidates: list[str],
    ctx: AlnsContext,
    options: DispatchOptions,
) -> list[str]:
    current = route[:]
    for candidate in candidates:
        pos, _ = _best_feasible_insert(current, candidate, ctx, options)
        if pos is not None:
            current = current[:pos] + [candidate] + current[pos:]
    return current


def _repair_by_efficiency(
    route: list[str],
    candidates: list[str],
    ctx: AlnsContext,
    options: DispatchOptions,
) -> list[str]:
    ordered = sorted(
        candidates,
        key=lambda farm_id: ctx.farm_map[farm_id].risk_score
        / max(_service_minutes(ctx.farm_map[farm_id], options), 1),
        reverse=True,
    )
    return _insert_candidates(route, ordered, ctx, options)


def _repair_by_risk(
    route: list[str],
    candidates: list[str],
    ctx: AlnsContext,
    options: DispatchOptions,
) -> list[str]:
    ordered = sorted(candidates, key=lambda farm_id: ctx.farm_map[farm_id].risk_score, reverse=True)
    return _insert_candidates(route, ordered, ctx, options)


def _roulette(weights: list[float]) -> int:
    total = sum(weights)
    threshold = random.uniform(0, total)
    cumulative = 0.0
    for index, weight in enumerate(weights):
        cumulative += weight
        if threshold <= cumulative:
            return index
    return len(weights) - 1


def alns_improve(
    route: list[str],
    all_farm_ids: list[str],
    ctx: AlnsContext,
    options: DispatchOptions,
    max_iter: int = 500,
    destroy_count: int = 2,
) -> list[str]:
    destroy_weights = [1.0, 1.0, 1.0]
    repair_weights = [1.0, 1.0]
    destroy_counts = [0, 0, 0]
    repair_counts = [0, 0]
    best_route = route[:]
    best_risk = route_risk(best_route, ctx)
    no_improvement = 0

    for _ in range(max_iter):
        if no_improvement >= 50:
            break
        farms_in = [node_id for node_id in best_route if node_id in ctx.farm_map]
        if not farms_in:
            break

        destroy_index = _roulette(destroy_weights)
        repair_index = _roulette(repair_weights)
        actual_destroy = min(destroy_count, len(farms_in))

        if destroy_index == 0:
            destroyed_route, _ = _destroy_by_risk(best_route, actual_destroy, ctx)
        elif destroy_index == 1:
            destroyed_route, _ = _destroy_by_cost(best_route, actual_destroy, ctx, options)
        else:
            destroyed_route, _ = _destroy_random(best_route, actual_destroy, ctx)

        visited = {node_id for node_id in destroyed_route if node_id in ctx.farm_map}
        candidates = [farm_id for farm_id in all_farm_ids if farm_id not in visited]
        repaired_route = (
            _repair_by_efficiency(destroyed_route, candidates, ctx, options)
            if repair_index == 0
            else _repair_by_risk(destroyed_route, candidates, ctx, options)
        )

        trial_risk = route_risk(repaired_route, ctx)
        score = 0
        if trial_risk > best_risk:
            best_route = repaired_route[:]
            best_risk = trial_risk
            no_improvement = 0
            score = 3
        else:
            no_improvement += 1

        destroy_counts[destroy_index] += 1
        repair_counts[repair_index] += 1
        destroy_weights[destroy_index] = max(
            0.01,
            destroy_weights[destroy_index] * 0.9 + (score / max(destroy_counts[destroy_index], 1)) * 0.1,
        )
        repair_weights[repair_index] = max(
            0.01,
            repair_weights[repair_index] * 0.9 + (score / max(repair_counts[repair_index], 1)) * 0.1,
        )

    return best_route


def _cluster_farms_for_teams(farms: list[DispatchFarm], team_count: int, options: DispatchOptions) -> list[list[DispatchFarm]]:
    cluster_count = max(1, min(team_count, len(farms)))
    farm_by_id = {farm.id: farm for farm in farms}
    clustering_input = [
        {
            "id": farm.id,
            "lat": farm.lat,
            "lon": farm.lng,
            "risk": farm.risk_score,
            "service_min": _service_minutes(farm, options),
        }
        for farm in farms
    ]
    with redirect_stdout(io.StringIO()):
        clusters, _ = risk_clustering_v2(clustering_input, cluster_count)

    buckets: list[list[DispatchFarm]] = [[] for _ in range(cluster_count)]
    for index in range(cluster_count):
        buckets[index] = [farm_by_id[item["id"]] for item in clusters[index]]
    return buckets


async def _build_context(farms: list[DispatchFarm], options: DispatchOptions) -> AlnsContext:
    facilities = {facility.id: facility for facility in load_disinfection_facilities()}
    facilities = {facility.id: facility for facility in load_disinfection_facilities()}
    node_points = {DEPOT_ID: OsrmPoint(options.depot_lat, options.depot_lng)}
    node_points.update({farm.id: OsrmPoint(farm.lat, farm.lng) for farm in farms})
    node_points.update({facility.id: facility.point for facility in facilities.values()})

    node_ids = list(node_points)
    matrix = await build_osrm_duration_matrix(list(node_points.values()))
    time_matrix = {
        from_id: {to_id: matrix[from_index][to_index] for to_index, to_id in enumerate(node_ids)}
        for from_index, from_id in enumerate(node_ids)
    }
    return AlnsContext(
        max_time=options.max_route_minutes,
        disinfect_service_minutes=options.disinfect_service_minutes,
        time_matrix=time_matrix,
        farm_map={farm.id: farm for farm in farms},
        disinfection_map=facilities,
    )


def _hub_response(hub: DisinfectionFacility) -> dict[str, Any]:
    return {
        "id": hub.id,
        "name": hub.name,
        "lat": hub.lat,
        "lng": hub.lng,
        "address": hub.address,
        "phone": hub.phone,
        "operatingHours": hub.operating_hours,
    }


async def solve_dispatch(farms: list[DispatchFarm], options: DispatchOptions) -> dict[str, Any]:
    if not farms:
        return {
            "teams": [],
            "unassignedFarms": [],
            "selectedFarmCount": 0,
            "teamCount": options.team_count,
            "totalDurationMinutes": 0,
        }
    if options.team_count < 1:
        raise ValueError("team_count must be at least 1")

    random.seed(RANDOM_SEED)
    ctx = await _build_context(farms, options)
    team_buckets = _cluster_farms_for_teams(farms, options.team_count, options)
    
     # ── 로그: 입력 ──────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"[DISPATCH] 입력: 농장 {len(farms)}개, 팀 {options.team_count}개")
    for farm in sorted(farms, key=lambda f: f.risk_score, reverse=True):
        print(f"  {farm.name}({farm.id}): 위험도 {farm.risk_score:.3f}, "
              f"처리 {_service_minutes(farm, options)}분")
    print(f"\n[CLUSTER] 팀별 배정 결과")
    for i, bucket in enumerate(team_buckets):
        svc = sum(_service_minutes(f, options) for f in bucket)
        names = [f"{f.name}({f.risk_score:.2f})" for f in bucket]
        print(f"  팀{i+1}: {len(bucket)}개 | 처리시간합 {svc}분 | {names}")
    # ────────────────────────────────────────────────────────────

    teams: list[dict[str, Any]] = []
    assigned_farm_ids: set[str] = set()
    total_duration = 0
    depot_response = {"name": options.depot_name, "lat": options.depot_lat, "lng": options.depot_lng}

    # for vehicle_id in range(options.team_count):
    #     bucket = team_buckets[vehicle_id] if vehicle_id < len(team_buckets) else []
    #     route = [DEPOT_ID, DEPOT_ID]
    #     if bucket:
    #         farm_ids = [farm.id for farm in bucket]
    #         route = greedy_route(farm_ids, ctx, options)
    #         route = alns_improve(route, farm_ids, ctx, options)

    #     stops: list[dict[str, Any]] = []
    #     for index, farm_id in enumerate([node_id for node_id in route if node_id in ctx.farm_map]):

    #----- 1단계: 팀별 ALNS 경로 생성
    print(f"\n[ALNS] 팀별 경로 최적화 시작")
    routes: list[list[str]] = []
    for vehicle_id in range(options.team_count):
        bucket = team_buckets[vehicle_id] if vehicle_id < len(team_buckets) else []
        route = [DEPOT_ID, DEPOT_ID]
        if bucket:
            farm_ids = [farm.id for farm in bucket]

            greedy = greedy_route(farm_ids, ctx, options)
            greedy_visited = [n for n in greedy if n in ctx.farm_map]
            print(f"  팀{vehicle_id+1} Greedy: 위험도 {route_risk(greedy, ctx):.3f}, "
                  f"{len(greedy_visited)}개, {route_minutes(greedy, ctx, options)}분 | "
                  f"{[ctx.farm_map[f].name for f in greedy_visited]}")

            route = alns_improve(greedy, farm_ids, ctx, options)
            alns_visited = [n for n in route if n in ctx.farm_map]
            alns_risk = route_risk(route, ctx)
            diff = round(alns_risk - route_risk(greedy, ctx), 3)
            diff_str = f"▲{diff}" if diff > 0 else ("개선 없음" if diff == 0 else f"▼{abs(diff)}")
            print(f"  팀{vehicle_id+1} ALNS:   위험도 {alns_risk:.3f}, "
                  f"{len(alns_visited)}개, {route_minutes(route, ctx, options)}분 | "
                  f"{diff_str} | {[ctx.farm_map[f].name for f in alns_visited]}")
        routes.append(route)

    # 2단계: 미처리 농장 흡수
    visited_before = {n for r in routes for n in r if n in ctx.farm_map}
    unvisited_before = [f for f in farms if f.id not in visited_before]
    print(f"\n[ABSORB] 흡수 전 미처리: {len(unvisited_before)}개")
    for f in sorted(unvisited_before, key=lambda x: x.risk_score, reverse=True):
        print(f"  - {f.name}({f.id}): 위험도 {f.risk_score:.3f}")
        
    all_farm_ids = [farm.id for farm in farms]
    routes, _ = absorb_unvisited_reopt(
        routes=routes,
        all_farm_ids=all_farm_ids,
        ctx=ctx,
        options=options,
        alns_improve_fn=alns_improve,
        route_minutes_fn=route_minutes,
        route_risk_fn=route_risk,
        best_feasible_insert_fn=_best_feasible_insert,
    )
    # 3단계: 결과 조립
    for vehicle_id in range(options.team_count):
        bucket = team_buckets[vehicle_id] if vehicle_id < len(team_buckets) else []
        route = routes[vehicle_id]
    # ------
        stops: list[dict[str, Any]] = []
        for index, farm_id in enumerate([node_id for node_id in route if node_id in ctx.farm_map]):
            farm = ctx.farm_map[farm_id]
            next_node_id = route[route.index(farm_id) + 1]
            disinfection_hub = _best_disinfection_for_leg(farm_id, next_node_id, ctx)
            assigned_farm_ids.add(farm_id)
            stops.append(
                {
                    "farm": farm_to_response(farm),
                    "disinfectionHub": _hub_response(disinfection_hub),
                    "order": index + 1,
                    "status": "plain",
                }
            )

        duration = route_minutes(route, ctx, options) if bucket else 0
        if duration > options.max_route_minutes and not options.allow_unassigned:
            raise RuntimeError("배차 제약조건을 만족하는 경로를 찾지 못했습니다.")
        total_duration += duration
        teams.append(
            {
                "id": f"team-{vehicle_id + 1}",
                "label": f"팀 {vehicle_id + 1}",
                "color": TEAM_COLORS[vehicle_id % len(TEAM_COLORS)],
                "depot": depot_response,
                "stops": stops,
                "totalDurationMinutes": duration,
            }
        )

    unassigned = [farm_to_response(farm) for farm in farms if farm.id not in assigned_farm_ids]
    if unassigned and not options.allow_unassigned:
        raise RuntimeError("배차 제약조건을 만족하는 경로를 찾지 못했습니다.")

    return {
        "teams": teams,
        "unassignedFarms": unassigned,
        "selectedFarmCount": len(farms),
        "teamCount": options.team_count,
        "totalDurationMinutes": total_duration,
    }


async def solve_emergency_dispatch(farms: list[DispatchFarm], options: DispatchOptions) -> dict[str, Any]:
    """비상모드 배차: 팀당 농장 1곳만 방문 후 소독 경유, 즉시 복귀한다.

    일반 solve_dispatch()의 ALNS 다중 농장 최적화 대신, 팀 수보다 농장이 많으면
    위험도 높은 농장부터 하나씩 배정하고 나머지는 unassignedFarms로 뺀다.
    """
    if not farms:
        return {
            "teams": [],
            "unassignedFarms": [],
            "selectedFarmCount": 0,
            "teamCount": options.team_count,
            "totalDurationMinutes": 0,
        }
    if options.team_count < 1:
        raise ValueError("team_count must be at least 1")

    ctx = await _build_context(farms, options)
    ordered_farms = sorted(farms, key=lambda f: f.risk_score, reverse=True)
    depot_response = {"name": options.depot_name, "lat": options.depot_lat, "lng": options.depot_lng}

    teams: list[dict[str, Any]] = []
    assigned_farm_ids: set[str] = set()
    total_duration = 0

    for vehicle_id in range(options.team_count):
        farm = ordered_farms[vehicle_id] if vehicle_id < len(ordered_farms) else None
        route = [DEPOT_ID, DEPOT_ID]
        stops: list[dict[str, Any]] = []
        if farm:
            route = [DEPOT_ID, farm.id, DEPOT_ID]
            disinfection_hub = _best_disinfection_for_leg(farm.id, DEPOT_ID, ctx)
            assigned_farm_ids.add(farm.id)
            stops.append(
                {
                    "farm": farm_to_response(farm),
                    "disinfectionHub": _hub_response(disinfection_hub),
                    "order": 1,
                    "status": "plain",
                }
            )
        duration = route_minutes(route, ctx, options) if farm else 0
        total_duration += duration
        teams.append(
            {
                "id": f"team-{vehicle_id + 1}",
                "label": f"팀 {vehicle_id + 1}",
                "color": TEAM_COLORS[vehicle_id % len(TEAM_COLORS)],
                "depot": depot_response,
                "stops": stops,
                "totalDurationMinutes": duration,
            }
        )

    unassigned = [farm_to_response(f) for f in farms if f.id not in assigned_farm_ids]
    if unassigned and not options.allow_unassigned:
        raise RuntimeError("팀 수보다 비상 대상 농장이 많아 배차 제약조건을 만족할 수 없습니다.")

    return {
        "teams": teams,
        "unassignedFarms": unassigned,
        "selectedFarmCount": len(farms),
        "teamCount": options.team_count,
        "totalDurationMinutes": total_duration,
    }


EMERGENCY_ZONE_RADIUS_KM = 3.0  # NaverMap.tsx의 EMERGENCY_RADII_METERS[0](3000m)와 반드시 일치


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return r * 2 * math.asin(math.sqrt(a))


def _merge_dispatch_results(parts: list[dict[str, Any]], total_team_count: int) -> dict[str, Any]:
    all_teams: list[dict[str, Any]] = []
    all_unassigned: list[dict[str, Any]] = []
    total_duration = 0
    total_selected = 0
    for part in parts:
        all_teams.extend(part["teams"])
        all_unassigned.extend(part["unassignedFarms"])
        total_duration += part["totalDurationMinutes"]
        total_selected += part["selectedFarmCount"]

    renumbered = [
        {**team, "id": f"team-{i + 1}", "label": f"팀 {i + 1}", "color": TEAM_COLORS[i % len(TEAM_COLORS)]}
        for i, team in enumerate(all_teams)
    ]
    return {
        "teams": renumbered,
        "unassignedFarms": all_unassigned,
        "selectedFarmCount": total_selected,
        "teamCount": total_team_count,
        "totalDurationMinutes": total_duration,
    }


async def solve_emergency_dispatch_zoned(
    farms: list[DispatchFarm], options: DispatchOptions, center_lat: float, center_lng: float,
) -> dict[str, Any]:
    """비상모드: 중심점 3km 이내는 팀당 농장 1곳, 밖은 일반 다중 농장 최적화.

    3km 이내 농장 수만큼 팀을 먼저 1:1로 확보하고(초과분은 위험도 낮은 순으로 미배정),
    남은 팀이 3km 밖 농장을 일반 ALNS로 처리한다(남은 팀이 없으면 밖 농장은 전부 미배정).
    """
    in_zone = [f for f in farms if _haversine_km(f.lat, f.lng, center_lat, center_lng) <= EMERGENCY_ZONE_RADIUS_KM]
    in_zone_ids = {f.id for f in in_zone}
    out_zone = [f for f in farms if f.id not in in_zone_ids]

    in_zone_team_count = min(len(in_zone), options.team_count)
    remaining_team_count = options.team_count - in_zone_team_count

    parts: list[dict[str, Any]] = []
    if in_zone_team_count > 0:
        parts.append(await solve_emergency_dispatch(in_zone, replace(options, team_count=in_zone_team_count)))
    if out_zone:
        if remaining_team_count > 0:
            parts.append(await solve_dispatch(out_zone, replace(options, team_count=remaining_team_count)))
        else:
            parts.append(
                {
                    "teams": [],
                    "unassignedFarms": [farm_to_response(f) for f in out_zone],
                    "selectedFarmCount": len(out_zone),
                    "teamCount": 0,
                    "totalDurationMinutes": 0,
                }
            )

    return _merge_dispatch_results(parts, options.team_count)
