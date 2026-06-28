from __future__ import annotations

from ortools.constraint_solver import pywrapcp


# NOTE: These constraints are temporary prototype assumptions for the current
# demo. Confirm policy, capacity, disinfection, and objective weights before
# using them as operational rules.


def add_time_limit_dimension(
    routing: pywrapcp.RoutingModel,
    transit_callback_index: int,
    team_count: int,
    max_route_minutes: int,
) -> pywrapcp.RoutingDimension:
    routing.AddDimensionWithVehicleCapacity(
        transit_callback_index,
        0,
        [max_route_minutes] * team_count,
        True,
        "Time",
    )
    return routing.GetDimensionOrDie("Time")



def constrain_one_cluster_per_team(
    routing: pywrapcp.RoutingModel,
    manager: pywrapcp.RoutingIndexManager,
    node_cluster_by_id: dict[int, int],
) -> None:
    for node_id, cluster_id in node_cluster_by_id.items():
        routing.VehicleVar(manager.NodeToIndex(node_id)).SetValues([-1, cluster_id])


def allow_unassigned_farms(
    routing: pywrapcp.RoutingModel,
    manager: pywrapcp.RoutingIndexManager,
    farm_penalty_by_node_id: dict[int, int],
) -> None:
    for node_id, penalty in farm_penalty_by_node_id.items():
        routing.AddDisjunction([manager.NodeToIndex(node_id)], penalty)



def farm_arc_minutes_with_required_disinfection(
    duration_matrix: list[list[int]],
    farm_node_id: int,
    hub_matrix_index: int,
    to_node_id: int,
    farm_service_minutes: int,
    disinfect_service_minutes: int,
) -> int:
    return (
        duration_matrix[farm_node_id][hub_matrix_index]
        + disinfect_service_minutes
        + duration_matrix[hub_matrix_index][to_node_id]
        + farm_service_minutes
    )



def minimize_total_and_longest_team_time(
    routing: pywrapcp.RoutingModel,
    time_dimension: pywrapcp.RoutingDimension,
    team_count: int,
    longest_team_weight: int = 100,
) -> None:
    time_dimension.SetGlobalSpanCostCoefficient(longest_team_weight)
    for vehicle_id in range(team_count):
        routing.AddVariableMinimizedByFinalizer(time_dimension.CumulVar(routing.End(vehicle_id)))
