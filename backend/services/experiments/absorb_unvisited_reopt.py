"""
absorb_unvisited_reopt.py
미처리 농장 흡수 + ALNS 재최적화 모듈

dispatch_optimizer.py에서 import해서 사용:
  from services.experiments.absorb_unvisited_reopt import absorb_unvisited_reopt

dispatch_optimizer.py의 함수(alns_improve, route_minutes, route_risk,
_best_feasible_insert)를 그대로 재활용하므로 ALNS 코드 중복 없음
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.experiments.dispatch_optimizer import (
        AlnsContext,
        DispatchOptions,
    )


def absorb_unvisited_reopt(
    routes: list[list[str]],
    all_farm_ids: list[str],
    ctx: "AlnsContext",
    options: "DispatchOptions",
    reopt_max_iter: int = 200,
) -> tuple[list[list[str]], int]:
    """
    ALNS 완료 후 미처리 농장을 시간이 남은 팀에 흡수 + ALNS 재최적화

    Args:
        routes:           팀별 경로 리스트 (소독소 삽입 전)
        all_farm_ids:     방역관이 선택한 전체 농장 ID 리스트
        ctx:              AlnsContext (time_matrix, farm_map, max_time 포함)
        options:          DispatchOptions
        reopt_max_iter:   재최적화 ALNS 최대 반복 횟수 (기본 200)
                          전체 ALNS(500회)보다 적게 실행
                          흡수 1개마다 실행되므로 속도와 품질 균형

    Returns:
        (업데이트된 routes, 흡수된 농장 수)

    흡수 방식:
      1. 전체 경로에서 방문된 농장 ID 집합 확인
      2. 미처리 농장 = 전체 - 방문됨 (위험도 내림차순 정렬)
      3. 모든 팀 × 미처리 농장 조합에서 cheapest insertion으로
         시간 증가분(delta)이 가장 작은 조합 선택
      4. 흡수 후 해당 팀 전체 경로를 ALNS로 재최적화
         → 재최적화로 이동시간이 줄어들면 추가 흡수 가능성 생김
      5. 재최적화 결과가 단순삽입보다 나쁘면 단순삽입 결과 유지
      6. 흡수된 농장은 즉시 방문 목록에 추가 (중복 방지)
      7. 더 이상 흡수 가능한 조합 없을 때까지 반복
    """
    # dispatch_optimizer.py 내부 함수 런타임에 import
    # (순환 import 방지를 위해 함수 내부에서 import)
    from services.experiments.dispatch_optimizer import (
        alns_improve,
        route_minutes,
        route_risk,
        _best_feasible_insert,
    )

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
            if route_minutes(route, ctx, options) >= ctx.max_time:
                continue

            for farm_id in unvisited:
                pos, delta = _best_feasible_insert(route, farm_id, ctx, options)
                if pos is None:
                    continue
                if delta < best_delta:
                    best_delta = delta
                    best_combo = (team_idx, farm_id, pos)

        if best_combo is None:
            break

        team_idx, farm_id, pos = best_combo

        # 단순 삽입
        route_inserted = (
            routes[team_idx][:pos] + [farm_id] + routes[team_idx][pos:]
        )
        risk_inserted = route_risk(route_inserted, ctx)

        # ALNS 재최적화
        farm_ids_after = [
            node_id for node_id in route_inserted if node_id in ctx.farm_map
        ]
        route_reopt = alns_improve(
            route_inserted,
            farm_ids_after,
            ctx,
            options,
            max_iter=reopt_max_iter,
        )
        risk_reopt = route_risk(route_reopt, ctx)

        # 더 좋은 결과 채택
        routes[team_idx] = (
            route_reopt if risk_reopt >= risk_inserted else route_inserted
        )
        absorbed_count += 1

    return routes, absorbed_count
