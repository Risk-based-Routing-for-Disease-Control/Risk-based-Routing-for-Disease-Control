from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Literal

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from services.dispatch_constraints import (
    add_time_limit_dimension,
    allow_unassigned_farms,
    constrain_one_cluster_per_team,
    farm_arc_minutes_with_required_disinfection,
    minimize_total_and_longest_team_time,
)
from services.disinfection_facilities import DisinfectionFacility, nearest_disinfection_facility
from services.osrm_client import OsrmPoint, build_osrm_duration_matrix


# NOTE: The clustering, OR-Tools objective, and constraints in this module are
# temporary prototype logic for web integration/testing. Replace or recalibrate
# before production operations.

RiskLevel = Literal["warning", "high", "critical"]
NodeType = Literal["depot", "farm", "disinfection"]

TEAM_COLORS = ["#1565C0", "#8E24AA", "#00897B", "#EF6C00", "#5E35B1", "#2E7D32"]
DEFAULT_DEPOT_NAME = "공통 방역 출발지"
DEFAULT_DEPOT_LAT = 37.1995
DEFAULT_DEPOT_LNG = 126.8310
DEFAULT_FARM_SERVICE_MINUTES = 15
FARM_SERVICE_MINUTES_PER_LIVESTOCK = 0.0007


def calculate_farm_service_minutes(livestock_count: int | float | None) -> int:
    count = max(0.0, float(livestock_count or 0))
    return int(math.ceil(DEFAULT_FARM_SERVICE_MINUTES + count * FARM_SERVICE_MINUTES_PER_LIVESTOCK))


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
class DispatchNode:
    node_id: int
    node_type: NodeType
    lat: float
    lng: float
    service_minutes: int
    name: str
    farm: DispatchFarm | None = None
    cluster_id: int | None = None


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


def _distance2(farm: DispatchFarm, center: tuple[float, float]) -> float:
    return (farm.lat - center[0]) ** 2 + (farm.lng - center[1]) ** 2


def _cluster_farms(farms: list[DispatchFarm], team_count: int) -> dict[str, int]:
    cluster_count = min(team_count, len(farms))
    ordered = sorted(farms, key=lambda farm: farm.risk_score, reverse=True)
    centers = [(farm.lat, farm.lng) for farm in ordered[:cluster_count]]
    assignments: dict[str, int] = {}

    for _ in range(12):
        buckets: list[list[DispatchFarm]] = [[] for _ in range(cluster_count)]
        for farm in farms:
            cluster_id = min(range(cluster_count), key=lambda index: _distance2(farm, centers[index]))
            buckets[cluster_id].append(farm)
            assignments[farm.id] = cluster_id

        next_centers: list[tuple[float, float]] = []
        for index, bucket in enumerate(buckets):
            if not bucket:
                next_centers.append(centers[index])
                continue
            weight_sum = sum(1.0 + farm.risk_score for farm in bucket)
            next_centers.append(
                (
                    sum(farm.lat * (1.0 + farm.risk_score) for farm in bucket) / weight_sum,
                    sum(farm.lng * (1.0 + farm.risk_score) for farm in bucket) / weight_sum,
                )
            )
        if next_centers == centers:
            break
        centers = next_centers

    return assignments


def _build_nearest_disinfection_hubs(
    farms: list[DispatchFarm],
) -> dict[str, DisinfectionFacility]:
    return {farm.id: nearest_disinfection_facility(farm.lat, farm.lng) for farm in farms}


async def _build_nodes(
    farms: list[DispatchFarm],
    options: DispatchOptions,
) -> tuple[list[DispatchNode], dict[int, DisinfectionFacility]]:
    cluster_by_farm_id = _cluster_farms(farms, options.team_count)
    hubs = _build_nearest_disinfection_hubs(farms)
    nodes = [
        DispatchNode(
            node_id=0,
            node_type="depot",
            lat=options.depot_lat,
            lng=options.depot_lng,
            service_minutes=0,
            name=options.depot_name,
        )
    ]
    hub_by_farm_node_id: dict[int, DisinfectionFacility] = {}

    for farm in sorted(farms, key=lambda item: item.risk_score, reverse=True):
        cluster_id = cluster_by_farm_id[farm.id]
        farm_node_id = len(nodes)
        farm_service = farm.estimated_duration_minutes or options.farm_service_minutes
        nodes.append(
            DispatchNode(
                node_id=farm_node_id,
                node_type="farm",
                lat=farm.lat,
                lng=farm.lng,
                service_minutes=farm_service,
                name=farm.name,
                farm=farm,
                cluster_id=cluster_id,
            )
        )

        hub_by_farm_node_id[farm_node_id] = hubs[farm.id]

    return nodes, hub_by_farm_node_id


def _arc_minutes(
    nodes: list[DispatchNode],
    matrix: list[list[int]],
    hub_matrix_index_by_farm_node_id: dict[int, int],
    options: DispatchOptions,
    from_node_id: int,
    to_node_id: int,
) -> int:
    from_node = nodes[from_node_id]
    if from_node.node_type == "farm":
        hub_index = hub_matrix_index_by_farm_node_id[from_node_id]
        return farm_arc_minutes_with_required_disinfection(
            matrix,
            from_node_id,
            hub_index,
            to_node_id,
            from_node.service_minutes,
            options.disinfect_service_minutes,
        )
    return matrix[from_node_id][to_node_id] + from_node.service_minutes


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

    nodes, hub_by_farm_node_id = await _build_nodes(farms, options)
    hub_points = list(hub_by_farm_node_id.values())
    matrix_points = [OsrmPoint(node.lat, node.lng) for node in nodes] + [hub.point for hub in hub_points]
    hub_matrix_index_by_farm_node_id = {
        farm_node_id: len(nodes) + hub_index
        for hub_index, farm_node_id in enumerate(hub_by_farm_node_id)
    }
    matrix = await build_osrm_duration_matrix(matrix_points)
    manager = pywrapcp.RoutingIndexManager(
        len(nodes),
        options.team_count,
        [0] * options.team_count,
        [0] * options.team_count,
    )
    routing = pywrapcp.RoutingModel(manager)

    def transit_minutes(from_index: int, to_index: int) -> int:
        return _arc_minutes(
            nodes,
            matrix,
            hub_matrix_index_by_farm_node_id,
            options,
            manager.IndexToNode(from_index),
            manager.IndexToNode(to_index),
        )

    transit_index = routing.RegisterTransitCallback(transit_minutes)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_index)
    time_dimension = add_time_limit_dimension(
        routing,
        transit_index,
        options.team_count,
        options.max_route_minutes,
    )

    node_cluster_by_id = {
        node.node_id: node.cluster_id
        for node in nodes
        if node.node_type == "farm" and node.cluster_id is not None
    }
    if options.allow_unassigned:
        allow_unassigned_farms(
            routing,
            manager,
            {
                node.node_id: 100_000 + int((node.farm.risk_score if node.farm else 0) * 10_000)
                for node in nodes
                if node.node_type == "farm"
            },
        )
    constrain_one_cluster_per_team(routing, manager, node_cluster_by_id)
    minimize_total_and_longest_team_time(routing, time_dimension, options.team_count)

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PARALLEL_CHEAPEST_INSERTION
    params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    params.time_limit.FromSeconds(options.search_time_limit_seconds)

    solution = routing.SolveWithParameters(params)
    if solution is None:
        raise RuntimeError("배차 제약조건을 만족하는 경로를 찾지 못했습니다.")

    teams: list[dict[str, Any]] = []
    assigned_farm_ids: set[str] = set()
    team_durations: list[int] = []
    total_duration = 0
    depot = nodes[0]
    depot_response = {"name": depot.name, "lat": depot.lat, "lng": depot.lng}
    for vehicle_id in range(options.team_count):
        stops: list[dict[str, Any]] = []
        index = routing.Start(vehicle_id)
        while not routing.IsEnd(index):
            node = nodes[manager.IndexToNode(index)]
            if node.node_type == "farm" and node.farm is not None:
                assigned_farm_ids.add(node.farm.id)
                disinfection_hub = hub_by_farm_node_id[node.node_id]
                stops.append(
                    {
                        "farm": farm_to_response(node.farm),
                        "disinfectionHub": {
                            "id": disinfection_hub.id,
                            "name": disinfection_hub.name,
                            "lat": disinfection_hub.lat,
                            "lng": disinfection_hub.lng,
                        },
                        "order": len(stops) + 1,
                        "status": "plain",
                    }
                )
            index = solution.Value(routing.NextVar(index))

        duration = int(solution.Value(time_dimension.CumulVar(index)))
        team_durations.append(duration)
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
