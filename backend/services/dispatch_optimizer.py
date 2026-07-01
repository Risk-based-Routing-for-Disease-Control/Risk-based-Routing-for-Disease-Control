from __future__ import annotations

from contextlib import redirect_stdout
from dataclasses import dataclass
import io
import math
import random
from typing import Any, Literal

from services.disinfection_facilities import DisinfectionFacility, load_hwaseong_disinfection_facilities
from services.experiments.clustering.risk_clustering_v4 import risk_clustering_v4
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
        clusters, _ = risk_clustering_v4(clustering_input, cluster_count)

    buckets: list[list[DispatchFarm]] = [[] for _ in range(cluster_count)]
    for index in range(cluster_count):
        buckets[index] = [farm_by_id[item["id"]] for item in clusters[index]]
    return buckets


async def _build_context(farms: list[DispatchFarm], options: DispatchOptions) -> AlnsContext:
    facilities = {facility.id: facility for facility in load_hwaseong_disinfection_facilities()}
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
    teams: list[dict[str, Any]] = []
    assigned_farm_ids: set[str] = set()
    total_duration = 0
    depot_response = {"name": options.depot_name, "lat": options.depot_lat, "lng": options.depot_lng}

    for vehicle_id in range(options.team_count):
        bucket = team_buckets[vehicle_id] if vehicle_id < len(team_buckets) else []
        route = [DEPOT_ID, DEPOT_ID]
        if bucket:
            farm_ids = [farm.id for farm in bucket]
            route = greedy_route(farm_ids, ctx, options)
            route = alns_improve(route, farm_ids, ctx, options)

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
