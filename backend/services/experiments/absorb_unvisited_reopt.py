"""
absorb_unvisited_reopt.py
미처리 농장 흡수 + ALNS 재최적화 모듈

dispatch_optimizer.py에서 import해서 사용:
  from services.experiments.absorb_unvisited_reopt import absorb_unvisited_reopt

dispatch_optimizer.py의 함수를 인자로 받아서 사용
→ 순환 import 없음
"""

from __future__ import annotations
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from services.experiments.dispatch_optimizer import AlnsContext, DispatchOptions


def absorb_unvisited_reopt(
    routes: list[list[str]],
    all_farm_ids: list[str],
    ctx: "AlnsContext",
    options: "DispatchOptions",
    alns_improve_fn: Callable,
    route_minutes_fn: Callable,
    route_risk_fn: Callable,
    best_feasible_insert_fn: Callable,
    reopt_max_iter: int = 200,
) -> tuple[list[list[str]], int]:
    """
    ALNS 완료 후 미처리 농장을 시간이 남은 팀에 흡수 + ALNS 재최적화

    Args:
        routes:                   팀별 경로 리스트
        all_farm_ids:             방역관이 선택한 전체 농장 ID 리스트
        ctx:                      AlnsContext
        options:                  DispatchOptions
        alns_improve_fn:          dispatch_optimizer.alns_improve 함수
        route_minutes_fn:         dispatch_optimizer.route_minutes 함수
        route_risk_fn:            dispatch_optimizer.route_risk 함수
        best_feasible_insert_fn:  dispatch_optimizer._best_feasible_insert 함수
        reopt_max_iter:           재최적화 ALNS 최대 반복 횟수 (기본 200)

    Returns:
        (업데이트된 routes, 흡수된 농장 수)
    """
    absorbed_count = 0

    while True:
        # 현재 방문된 농장 집합
        visited_ids = {
            node_id
            for route in routes
            for node_id in route
            if node_id in ctx.farm_map
        }

        # 미처리 농장 (위험도 높은 것 우선)
        unvisited = sorted(
            [fid for fid in all_farm_ids if fid not in visited_ids],
            key=lambda fid: ctx.farm_map[fid].risk_score,
            reverse=True,
        )

        if not unvisited:
            break

        # 모든 팀 × 미처리 농장 조합에서 delta 최소 탐색
        best_combo: tuple[int, str, int] | None = None
        best_delta = float("inf")

        for team_idx, route in enumerate(routes):
            if route_minutes_fn(route, ctx, options) >= ctx.max_time:
                continue

            for farm_id in unvisited:
                pos, delta = best_feasible_insert_fn(route, farm_id, ctx, options)
                if pos is None:
                    continue
                if delta < best_delta:
                    best_delta = delta
                    best_combo = (team_idx, farm_id, pos)

        if best_combo is None:
            print(f"[ABSORB] 흡수 불가: 남은 {len(unvisited)}개")
            for farm_id in unvisited:
                best_team, best_after = None, float("inf")
                for ti, route in enumerate(routes):
                    for pos in range(1, len(route)):
                        trial = route[:pos] + [farm_id] + route[pos:]
                        after = route_minutes_fn(trial, ctx, options)
                        if after < best_after:
                            best_after = after
                            best_team = ti + 1
                farm = ctx.farm_map[farm_id]
                print(f"  {farm.name}({farm.risk_score:.2f}): "
                    f"최선 팀{best_team}에 삽입 시 {round(best_after,1)}분 "
                    f"(상한 {ctx.max_time}분, {round(best_after-ctx.max_time,1)}분 초과)")
            break

        team_idx, farm_id, pos = best_combo

        risk_before = route_risk_fn(routes[team_idx], ctx)
        # 단순 삽입
        route_inserted = (
            routes[team_idx][:pos] + [farm_id] + routes[team_idx][pos:]
        )
        risk_inserted = route_risk_fn(route_inserted, ctx)

        # ALNS 재최적화
        farm_ids_after = [
            node_id for node_id in route_inserted if node_id in ctx.farm_map
        ]
        route_reopt = alns_improve_fn(
            route_inserted,
            farm_ids_after,
            ctx,
            options,
            max_iter=reopt_max_iter,
        )
        risk_reopt = route_risk_fn(route_reopt, ctx)

        # 더 좋은 결과 채택
        routes[team_idx] = (
            route_reopt if risk_reopt >= risk_inserted else route_inserted
        )
        absorbed_count += 1
        print(f"[ABSORB] 흡수 {absorbed_count}: "
              f"{ctx.farm_map[farm_id].name}({ctx.farm_map[farm_id].risk_score:.3f}) "
              f"→ 팀{team_idx+1} | delta {round(best_delta,1)}분 | "
              f"위험도 {round(risk_before,3)}→{round(route_risk_fn(routes[team_idx], ctx),3)}")

    return routes, absorbed_count
