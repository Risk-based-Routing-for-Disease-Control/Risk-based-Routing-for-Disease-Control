from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Any

from services.disinfection_facilities import DisinfectionFacility, nearest_disinfection_facility
from services.dispatch_optimizer import (
    DEFAULT_FARM_SERVICE_MINUTES,
    DispatchFarm,
    DispatchOptions,
    TEAM_COLORS,
    farm_to_response,
)
from services.osrm_client import OsrmPoint, build_osrm_duration_matrix


RANDOM_SEED = 42
DEPOT_ID = "depot"


@dataclass
class AlnsContext:
    max_time: int
    time_matrix: dict[str, dict[str, int]]
    farm_map: dict[str, DispatchFarm]
    disinfection_map: dict[str, DisinfectionFacility]


def _travel_time(ctx: AlnsContext, from_id: str, to_id: str) -> int:
    return ctx.time_matrix[from_id][to_id]


def _service_minutes(farm: DispatchFarm) -> int:
    return farm.estimated_duration_minutes or DEFAULT_FARM_SERVICE_MINUTES


def calc_total_time(route: list[str], ctx: AlnsContext) -> tuple[float, float, float]:
    travel = sum(_travel_time(ctx, route[index], route[index + 1]) for index in range(len(route) - 1))
    service = sum(_service_minutes(ctx.farm_map[node_id]) for node_id in route if node_id in ctx.farm_map)
    return round(travel + service, 1), round(travel, 1), round(service, 1)


def calc_total_risk(route: list[str], ctx: AlnsContext) -> tuple[float, list[str]]:
    visited = [node_id for node_id in route if node_id in ctx.farm_map]
    return round(sum(ctx.farm_map[node_id].risk_score for node_id in visited), 3), visited


def calc_overhead(route: list[str], ctx: AlnsContext) -> float:
    overhead = 0
    for index in range(len(route) - 1):
        current_id = route[index]
        next_id = route[index + 1]
        if current_id in ctx.farm_map and next_id in ctx.farm_map:
            overhead += min(
                _travel_time(ctx, current_id, disinfection_id)
                + _travel_time(ctx, disinfection_id, next_id)
                - _travel_time(ctx, current_id, next_id)
                for disinfection_id in ctx.disinfection_map
            )
    return round(overhead, 1)


def time_with_dis(route: list[str], ctx: AlnsContext) -> float:
    total, _, _ = calc_total_time(route, ctx)
    return round(total + calc_overhead(route, ctx), 1)


def greedy_route(farm_ids: list[str], ctx: AlnsContext) -> list[str]:
    unvisited = list(farm_ids)
    route = [DEPOT_ID, DEPOT_ID]
    while unvisited:
        best_farm, best_score, best_pos = None, -1, None
        for farm_id in unvisited:
            for pos in range(1, len(route)):
                prev_id, next_id = route[pos - 1], route[pos]
                cost = (
                    _travel_time(ctx, prev_id, farm_id)
                    + _travel_time(ctx, farm_id, next_id)
                    - _travel_time(ctx, prev_id, next_id)
                    + _service_minutes(ctx.farm_map[farm_id])
                )
                trial = route[:pos] + [farm_id] + route[pos:]
                if time_with_dis(trial, ctx) > ctx.max_time:
                    continue
                score = ctx.farm_map[farm_id].risk_score / max(cost, 1)
                if score > best_score:
                    best_score, best_farm, best_pos = score, farm_id, pos
        if best_farm is None:
            break
        route = route[:best_pos] + [best_farm] + route[best_pos:]
        unvisited.remove(best_farm)
    return route


def destroy_by_risk(route: list[str], n: int, ctx: AlnsContext) -> tuple[list[str], list[str]]:
    farms = [node_id for node_id in route if node_id in ctx.farm_map]
    by_risk = sorted(farms, key=lambda node_id: ctx.farm_map[node_id].risk_score)
    pool = by_risk[: max(1, len(by_risk) // 2)]
    removed = random.sample(pool, min(n, len(pool)))
    new_route = route[:]
    for farm_id in removed:
        new_route.remove(farm_id)
    return new_route, removed


def destroy_by_cost(route: list[str], n: int, ctx: AlnsContext) -> tuple[list[str], list[str]]:
    farms = [node_id for node_id in route if node_id in ctx.farm_map]
    if len(farms) < 2:
        return destroy_by_risk(route, n, ctx)

    efficiencies: list[tuple[str, float]] = []
    for farm_id in route:
        if farm_id not in ctx.farm_map:
            continue
        index = route.index(farm_id)
        prev_id = route[index - 1]
        next_id = route[index + 1]
        move_cost = _travel_time(ctx, prev_id, farm_id) + _travel_time(ctx, farm_id, next_id)
        efficiency = ctx.farm_map[farm_id].risk_score / max(move_cost, 1)
        efficiencies.append((farm_id, efficiency))

    efficiencies.sort(key=lambda item: item[1])
    pool = [farm_id for farm_id, _ in efficiencies[: max(1, len(efficiencies) // 2)]]
    removed = random.sample(pool, min(n, len(pool)))
    new_route = route[:]
    for farm_id in removed:
        new_route.remove(farm_id)
    return new_route, removed


def destroy_random(route: list[str], n: int, ctx: AlnsContext) -> tuple[list[str], list[str]]:
    farms = [node_id for node_id in route if node_id in ctx.farm_map]
    removed = random.sample(farms, min(n, len(farms)))
    new_route = route[:]
    for farm_id in removed:
        new_route.remove(farm_id)
    return new_route, removed


def repair_by_efficiency(route: list[str], candidates: list[str], ctx: AlnsContext) -> list[str]:
    ordered = sorted(
        candidates,
        key=lambda farm_id: ctx.farm_map[farm_id].risk_score / max(_service_minutes(ctx.farm_map[farm_id]), 1),
        reverse=True,
    )
    return _insert_candidates(route, ordered, ctx)


def repair_by_risk(route: list[str], candidates: list[str], ctx: AlnsContext) -> list[str]:
    ordered = sorted(candidates, key=lambda farm_id: ctx.farm_map[farm_id].risk_score, reverse=True)
    return _insert_candidates(route, ordered, ctx)


def _insert_candidates(route: list[str], candidates: list[str], ctx: AlnsContext) -> list[str]:
    current = route[:]
    for candidate in candidates:
        best_pos, best_cost = None, float("inf")
        for pos in range(1, len(current)):
            prev_id, next_id = current[pos - 1], current[pos]
            cost = (
                _travel_time(ctx, prev_id, candidate)
                + _travel_time(ctx, candidate, next_id)
                - _travel_time(ctx, prev_id, next_id)
            )
            if cost < best_cost:
                best_cost, best_pos = cost, pos
        if best_pos is not None:
            trial = current[:best_pos] + [candidate] + current[best_pos:]
            if time_with_dis(trial, ctx) <= ctx.max_time:
                current = trial
    return current


def alns_improve(
    route: list[str],
    all_farm_ids: list[str],
    ctx: AlnsContext,
    max_iter: int = 500,
    destroy_count: int = 2,
) -> list[str]:
    decay = 0.1
    score_best = 3
    score_better = 2

    destroy_fns = [destroy_by_risk, destroy_by_cost, destroy_random]
    repair_fns = [repair_by_efficiency, repair_by_risk]
    destroy_weights = [1.0] * len(destroy_fns)
    repair_weights = [1.0] * len(repair_fns)
    destroy_counts = [0] * len(destroy_fns)
    repair_counts = [0] * len(repair_fns)

    best_route = route[:]
    best_risk, _ = calc_total_risk(best_route, ctx)
    no_improvement = 0

    for _ in range(max_iter):
        if no_improvement >= 50:
            break

        current_route = best_route[:]
        farms_in = [node_id for node_id in current_route if node_id in ctx.farm_map]
        if not farms_in:
            break

        destroy_index = _roulette(destroy_weights)
        repair_index = _roulette(repair_weights)
        actual_destroy = min(destroy_count, len(farms_in))
        destroyed_route, _ = destroy_fns[destroy_index](current_route, actual_destroy, ctx)

        visited = {node_id for node_id in destroyed_route if node_id in ctx.farm_map}
        candidates = [farm_id for farm_id in all_farm_ids if farm_id not in visited]
        repaired_route = repair_fns[repair_index](destroyed_route, candidates, ctx)

        trial_risk, _ = calc_total_risk(repaired_route, ctx)
        score = 0
        if trial_risk > best_risk:
            score = score_best
            best_risk = trial_risk
            best_route = repaired_route[:]
            no_improvement = 0
        elif trial_risk > calc_total_risk(current_route, ctx)[0]:
            score = score_better
            no_improvement += 1
        else:
            no_improvement += 1

        destroy_counts[destroy_index] += 1
        repair_counts[repair_index] += 1
        destroy_weights[destroy_index] = (
            destroy_weights[destroy_index] * (1 - decay)
            + (score / max(destroy_counts[destroy_index], 1)) * decay
        )
        repair_weights[repair_index] = (
            repair_weights[repair_index] * (1 - decay)
            + (score / max(repair_counts[repair_index], 1)) * decay
        )
        destroy_weights = [max(weight, 0.01) for weight in destroy_weights]
        repair_weights = [max(weight, 0.01) for weight in repair_weights]

    return best_route


def _roulette(weights: list[float]) -> int:
    total = sum(weights)
    threshold = random.uniform(0, total)
    cumulative = 0
    for index, weight in enumerate(weights):
        cumulative += weight
        if threshold <= cumulative:
            return index
    return len(weights) - 1


def _nearest_facility_by_farm(farms: list[DispatchFarm]) -> dict[str, DisinfectionFacility]:
    return {farm.id: nearest_disinfection_facility(farm.lat, farm.lng) for farm in farms}


async def _build_context(farms: list[DispatchFarm], options: DispatchOptions) -> AlnsContext:
    facility_by_farm_id = _nearest_facility_by_farm(farms)
    facilities = {facility.id: facility for facility in facility_by_farm_id.values()}
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
        time_matrix=time_matrix,
        farm_map={farm.id: farm for farm in farms},
        disinfection_map=facilities,
    )


def _split_farms_for_teams(farms: list[DispatchFarm], team_count: int) -> list[list[DispatchFarm]]:
    buckets: list[list[DispatchFarm]] = [[] for _ in range(max(1, min(team_count, len(farms))))]
    for index, farm in enumerate(sorted(farms, key=lambda item: item.risk_score, reverse=True)):
        buckets[index % len(buckets)].append(farm)
    return buckets


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
    facility_by_farm_id = _nearest_facility_by_farm(farms)
    depot_response = {"name": options.depot_name, "lat": options.depot_lat, "lng": options.depot_lng}
    teams: list[dict[str, Any]] = []
    assigned_farm_ids: set[str] = set()
    total_duration = 0

    team_buckets = _split_farms_for_teams(farms, options.team_count)
    for vehicle_id in range(options.team_count):
        bucket = team_buckets[vehicle_id] if vehicle_id < len(team_buckets) else []
        route = [DEPOT_ID, DEPOT_ID]
        if bucket:
            farm_ids = [farm.id for farm in bucket]
            route = greedy_route(farm_ids, ctx)
            route = alns_improve(route, farm_ids, ctx, max_iter=500, destroy_count=2)

        stops: list[dict[str, Any]] = []
        for farm_id in [node_id for node_id in route if node_id in ctx.farm_map]:
            farm = ctx.farm_map[farm_id]
            hub = facility_by_farm_id[farm_id]
            assigned_farm_ids.add(farm_id)
            stops.append(
                {
                    "farm": farm_to_response(farm),
                    "disinfectionHub": {
                        "id": hub.id,
                        "name": hub.name,
                        "lat": hub.lat,
                        "lng": hub.lng,
                    },
                    "order": len(stops) + 1,
                    "status": "plain",
                }
            )

        duration = int(time_with_dis(route, ctx)) if bucket else 0
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
    return {
        "teams": teams,
        "unassignedFarms": unassigned,
        "selectedFarmCount": len(farms),
        "teamCount": options.team_count,
        "totalDurationMinutes": total_duration,
    }
