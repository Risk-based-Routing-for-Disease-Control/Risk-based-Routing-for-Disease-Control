import math


# ================================================================
# 위험도 기반 클러스터링 v4
#
# v2 문제: 처리시간 불균형 (클러스터 크기 차이 큼)
# v3 문제: 재조정 시 지리적으로 먼 농장도 이동 → 응집성 파괴
#
# v4 해결책: 재조정 시 "절대 거리 상한선" 추가
#   - 현재 클러스터 centroid에서 MAX_MOVE_RATIO 이내인 농장만 이동 가능
#   - 지리적으로 가까운 경계 농장만 이동 → 응집성 유지
#   - 거리 상한선을 넘는 농장은 처리시간 불균형이 남더라도 이동 안 함
#
# MAX_MOVE_RATIO 의미:
#   이동 대상 농장이 "현재 클러스터의 평균 내부 거리"의
#   몇 배 이내에 있어야 이동 가능한지를 결정
#   1.0 = 평균 내부 거리 이내 (엄격)
#   1.5 = 평균 내부 거리의 1.5배 이내 (기본값)
#   2.0 = 평균 내부 거리의 2배 이내 (느슨)
# ================================================================

MAX_MOVE_RATIO = 1.5  # 조정 가능한 파라미터


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(a))


def _avg_intra_distance(cluster: list[dict], centroid: dict) -> float:
    """클러스터 내 농장들의 centroid까지 평균 거리 (km)"""
    if not cluster:
        return 0.0
    dists = [haversine_km(f["lat"], f["lon"], centroid["lat"], centroid["lon"])
             for f in cluster]
    return sum(dists) / len(dists)


def select_initial_centroids(farms: list[dict], K: int) -> list[dict]:
    """
    초기 centroid 선택: 위험도 × 지리적 분산 동시 고려

    1번째: 위험도 최고 농장 선택
    2번째~: "위험도 × 기존 centroid들과의 최소 거리" 점수가 가장 높은 농장 선택
    """
    selected = []
    first = max(farms, key=lambda x: x["risk"])
    selected.append(first)

    for _ in range(1, K):
        best_farm = None
        best_score = -1.0
        for farm in farms:
            if farm in selected:
                continue
            min_dist = min(
                haversine_km(farm["lat"], farm["lon"], c["lat"], c["lon"])
                for c in selected
            )
            score = farm["risk"] * min_dist
            if score > best_score:
                best_score = score
                best_farm = farm
        if best_farm:
            selected.append(best_farm)

    return selected


def kmeans_cluster(
    farms: list[dict],
    K: int,
    max_iter: int = 100,
) -> tuple[dict[int, list[dict]], list[dict]]:
    """K-means 클러스터링 (초기 centroid는 위험도×거리 기준)"""
    initial = select_initial_centroids(farms, K)
    centroids = [{"lat": f["lat"], "lon": f["lon"]} for f in initial]
    prev_assignments: dict | None = None

    for _ in range(max_iter):
        clusters: dict[int, list[dict]] = {i: [] for i in range(K)}
        assignments: dict = {}

        for farm in farms:
            distances = [
                haversine_km(farm["lat"], farm["lon"], c["lat"], c["lon"])
                for c in centroids
            ]
            closest = distances.index(min(distances))
            clusters[closest].append(farm)
            assignments[farm["id"]] = closest

        # 빈 클러스터 처리
        for i in range(K):
            if not clusters[i]:
                largest = max(range(K), key=lambda x: len(clusters[x]))
                farthest = max(
                    clusters[largest],
                    key=lambda f: haversine_km(
                        f["lat"], f["lon"],
                        centroids[largest]["lat"], centroids[largest]["lon"],
                    ),
                )
                clusters[largest].remove(farthest)
                clusters[i].append(farthest)

        if assignments == prev_assignments:
            break
        prev_assignments = assignments

        for i in range(K):
            if clusters[i]:
                centroids[i] = {
                    "lat": sum(f["lat"] for f in clusters[i]) / len(clusters[i]),
                    "lon": sum(f["lon"] for f in clusters[i]) / len(clusters[i]),
                }

    return clusters, centroids


def rebalance_with_distance_cap(
    clusters: dict[int, list[dict]],
    centroids: list[dict],
    K: int,
    tolerance_min: int = 60,
    max_iter: int = 50,
    max_move_ratio: float = MAX_MOVE_RATIO,
) -> tuple[dict[int, list[dict]], list[dict]]:
    """
    처리시간 균등 재조정 (절대 거리 상한선 포함)

    핵심 변경 (v3 대비):
      이동 가능 조건에 절대 거리 상한선 추가
      → 현재 클러스터 평균 내부 거리 × max_move_ratio 이내인 농장만 이동 가능
      → 지리적으로 먼 농장은 처리시간 불균형이 남아도 이동 안 함

    예:
      클러스터0 평균 내부 거리 = 5km
      max_move_ratio = 1.5
      → centroid에서 7.5km 이내 농장만 이동 대상
      → 10km 떨어진 농장은 후보에서 제외
    """
    print(f"  [처리시간 균등 재조정 시작] 허용 오차: {tolerance_min}분, "
          f"거리 상한 비율: {max_move_ratio}×평균내부거리")

    moved = 0
    skipped_distance = 0

    for iteration in range(max_iter):
        svc = {i: sum(f["service_min"] for f in clusters[i]) for i in range(K)}
        mx = max(svc, key=svc.get)
        mn = min(svc, key=svc.get)
        diff = svc[mx] - svc[mn]

        if diff <= tolerance_min:
            print(f"  수렴 완료 ({iteration}번 조정, 최대 차이 {diff}분, "
                  f"거리 제한으로 {skipped_distance}개 후보 제외됨)")
            break

        # 현재 클러스터(mx)의 평균 내부 거리 계산
        avg_dist = _avg_intra_distance(clusters[mx], centroids[mx])
        max_allowed_dist = avg_dist * max_move_ratio

        # 이동 후보: 거리 상한선 이내 + 목표 클러스터 방향 (거리 비율 기준)
        best_farm = None
        best_ratio = float("inf")

        for farm in clusters[mx]:
            dist_from_centroid = haversine_km(
                farm["lat"], farm["lon"],
                centroids[mx]["lat"], centroids[mx]["lon"]
            )

            # ★ v4 핵심: 절대 거리 상한선 체크
            if dist_from_centroid > max_allowed_dist:
                skipped_distance += 1
                continue

            dist_cur = max(dist_from_centroid, 0.01)
            dist_tgt = haversine_km(
                farm["lat"], farm["lon"],
                centroids[mn]["lat"], centroids[mn]["lon"]
            )
            ratio = dist_tgt / dist_cur

            if ratio < best_ratio:
                best_ratio = ratio
                best_farm = farm

        if best_farm is None:
            # 거리 상한선으로 이동 가능한 농장이 없음 → 여기서 중단
            print(f"  조기 중단: 거리 제한으로 이동 가능한 농장 없음 "
                  f"(잔여 처리시간 차이: {diff}분)")
            break

        # 농장 이동
        clusters[mx].remove(best_farm)
        clusters[mn].append(best_farm)
        moved += 1

        new_svc = {i: sum(f["service_min"] for f in clusters[i]) for i in range(K)}
        print(f"  조정 {moved}: {best_farm['id']} "
              f"(처리 {best_farm['service_min']}분, "
              f"centroid까지 {round(haversine_km(best_farm['lat'], best_farm['lon'], centroids[mx]['lat'], centroids[mx]['lon']), 1)}km) "
              f"클러스터{mx}→{mn} | "
              f"차이 {diff}분→{new_svc[mx]-new_svc[mn]}분")

        # centroid 업데이트
        for i in [mx, mn]:
            if clusters[i]:
                centroids[i] = {
                    "lat": sum(f["lat"] for f in clusters[i]) / len(clusters[i]),
                    "lon": sum(f["lon"] for f in clusters[i]) / len(clusters[i]),
                }

    else:
        final_svc = {i: sum(f["service_min"] for f in clusters[i]) for i in range(K)}
        final_diff = max(final_svc.values()) - min(final_svc.values())
        print(f"  최대 반복 도달 (잔여 차이 {final_diff}분)")

    return clusters, centroids


def risk_clustering_v4(
    farms: list[dict],
    K: int,
    tolerance_min: int = 60,
    max_move_ratio: float = MAX_MOVE_RATIO,
    max_iter: int = 100,
) -> tuple[dict[int, list[dict]], list[dict]]:
    """
    위험도 기반 클러스터링 v4 메인 함수

    Args:
        farms: 농장 리스트 (id, lat, lon, risk, service_min 필드 필요)
        K: 팀 수
        tolerance_min: 처리시간 균등 허용 오차 (분)
        max_move_ratio: 이동 가능한 최대 거리 = 클러스터 평균 내부 거리 × 이 값
        max_iter: K-means 최대 반복 횟수
    """
    if K > len(farms):
        raise ValueError(f"팀 수({K})가 농장 수({len(farms)})보다 많을 수 없어요")

    print(f"\n  1단계: 초기 centroid 선택 (위험도 × 거리)")
    initial = select_initial_centroids(farms, K)
    for i, f in enumerate(initial):
        print(f"    팀{i+1}: {f['id']} (위험도 {f['risk']:.3f})")

    print(f"\n  2단계: K-means 클러스터링")
    clusters, centroids = kmeans_cluster(farms, K, max_iter)
    svc = {i: sum(f["service_min"] for f in clusters[i]) for i in range(K)}
    diff_before = max(svc.values()) - min(svc.values())
    sizes = [len(clusters[i]) for i in range(K)]
    print(f"  완료 | 클러스터 크기: {sizes} | 처리시간 차이: {diff_before}분")

    print(f"\n  3단계: 처리시간 균등 재조정 (거리 상한 {max_move_ratio}×평균내부거리)")
    clusters, centroids = rebalance_with_distance_cap(
        clusters, centroids, K, tolerance_min, max_move_ratio=max_move_ratio
    )

    return clusters, centroids
