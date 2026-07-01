import json
import math
import random

# ================================================================
# 위험도 기반 클러스터링 v2
#
# v1 문제점:
#   위험도 Top K 농장이 지리적으로 몰려있으면
#   K-means가 제대로 된 K개 구역을 못 만듦
#
# v2 해결:
#   초기 centroid 선택 시 "위험도 × 기존 centroid와의 거리" 점수 사용
#   → 위험도도 높고 지리적으로도 분산된 centroid 선택
#   → K-means++의 변형 (거리만 → 위험도 × 거리)
# ================================================================


def haversine_km(lat1, lon1, lat2, lon2):
    """두 좌표 간 실제 거리 (km)"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(dlon/2)**2)
    return R * 2 * math.asin(math.sqrt(a))


def select_initial_centroids(farms, K):
    """
    초기 centroid 선택: 위험도 × 지리적 분산 동시 고려

    1번째: 위험도 가장 높은 농장 선택
    2번째~: "위험도 × 기존 centroid들과의 최소 거리" 점수가 가장 높은 농장 선택

    왜 이렇게 하나?
      위험도만 보면: Top K가 한 지역에 몰릴 수 있음
      거리만 보면:  위험도 낮은 농장이 centroid가 될 수 있음
      둘을 곱하면: 위험도도 높으면서 기존 centroid와 멀리 있는 농장 선택
                  → 위험도 + 지리 분산 동시 달성
    """
    selected = []

    # 1번째: 위험도 최고 농장
    first = max(farms, key=lambda x: x["risk"])
    selected.append(first)

    print(f"  centroid 선택 과정:")
    print(f"    1번째: {first['id']} (위험도 {first['risk']}) ← 위험도 1등")

    # 2번째~K번째: 위험도 × 거리 점수
    for i in range(1, K):
        best_farm = None
        best_score = -1

        for farm in farms:
            if farm in selected:
                continue

            # 이미 선택된 centroid들과의 최소 거리
            min_dist = min(
                haversine_km(farm["lat"], farm["lon"], c["lat"], c["lon"])
                for c in selected
            )

            # 점수 = 위험도 × 최소 거리
            # 위험도 높을수록, 기존 centroid와 멀수록 점수 높음
            score = farm["risk"] * min_dist

            if score > best_score:
                best_score = score
                best_farm = farm

        selected.append(best_farm)
        min_dist_from_prev = min(
            haversine_km(best_farm["lat"], best_farm["lon"], c["lat"], c["lon"])
            for c in selected[:-1]
        )
        print(f"    {i+1}번째: {best_farm['id']} "
              f"(위험도 {best_farm['risk']}, "
              f"가장 가까운 centroid까지 {round(min_dist_from_prev,1)}km)")

    return selected


def risk_clustering_v2(farms, K, max_iter=100):
    """
    위험도 + 지리 분산 기반 K-means 클러스터링

    Args:
        farms: 농장 리스트 (id, lat, lon, risk, service_min 필요)
        K: 팀(클러스터) 수
        max_iter: 최대 반복 횟수

    Returns:
        clusters: {팀 인덱스: [농장 리스트]}
        centroids: 최종 centroid 좌표 리스트
    """
    if K > len(farms):
        raise ValueError(f"팀 수({K})가 농장 수({len(farms)})보다 많을 수 없어요")

    # 1. 초기 centroid 선택
    initial = select_initial_centroids(farms, K)
    centroids = [{"lat": f["lat"], "lon": f["lon"], "id": f["id"]}
                 for f in initial]

    prev_assignments = None

    for iteration in range(max_iter):

        # 2. 각 농장을 가장 가까운 centroid에 배정
        clusters = {i: [] for i in range(K)}
        assignments = {}

        for farm in farms:
            distances = [
                haversine_km(farm["lat"], farm["lon"], c["lat"], c["lon"])
                for c in centroids
            ]
            closest = distances.index(min(distances))
            clusters[closest].append(farm)
            assignments[farm["id"]] = closest

        # 3. 빈 클러스터 처리
        for i in range(K):
            if not clusters[i]:
                print(f"  ⚠️ 팀{i+1} 빈 클러스터 → 가장 큰 클러스터에서 가장 먼 농장 이동")
                largest = max(range(K), key=lambda x: len(clusters[x]))
                farthest = max(
                    clusters[largest],
                    key=lambda f: haversine_km(
                        f["lat"], f["lon"],
                        centroids[largest]["lat"], centroids[largest]["lon"]
                    )
                )
                clusters[largest].remove(farthest)
                clusters[i].append(farthest)

        # 4. 수렴 확인
        if assignments == prev_assignments:
            print(f"  수렴 완료 ({iteration+1}번째 반복)")
            break
        prev_assignments = assignments

        # 5. centroid 업데이트 (클러스터 평균 위치)
        for i in range(K):
            if clusters[i]:
                avg_lat = sum(f["lat"] for f in clusters[i]) / len(clusters[i])
                avg_lon = sum(f["lon"] for f in clusters[i]) / len(clusters[i])
                centroids[i] = {"lat": avg_lat, "lon": avg_lon}

    return clusters, centroids


def print_cluster_summary(clusters, K, label=""):
    """클러스터링 결과 요약 출력"""
    print(f"\n  {'='*52}")
    if label:
        print(f"  {label}")
    print(f"  {'팀':>4} {'농장수':>6} {'총위험도':>9} {'평균위험도':>10} {'처리시간합':>10}")
    print(f"  {'-'*50}")

    for i in range(K):
        f_list = clusters[i]
        total_risk = round(sum(f["risk"] for f in f_list), 3)
        avg_risk = round(total_risk / len(f_list), 3) if f_list else 0
        total_svc = sum(f.get("service_min", 60) for f in f_list)
        print(f"  팀{i+1:>2} {len(f_list):>6}개 {total_risk:>9.3f} "
              f"{avg_risk:>10.3f} {total_svc:>8}분")

    # 팀별 담당 농장 (위험도 순)
    print(f"\n  [팀별 담당 농장 (위험도 내림차순)]")
    for i in range(K):
        sorted_f = sorted(clusters[i], key=lambda x: x["risk"], reverse=True)
        ids = [f["id"] for f in sorted_f]
        risks = [f["risk"] for f in sorted_f]
        lats = [round(f["lat"], 3) for f in sorted_f]
        print(f"  팀{i+1}: {ids}")
        print(f"       위험도: {risks}")
        print(f"       위도:   {lats}")

    # 균형 지표
    total_risks = [sum(f["risk"] for f in clusters[i]) for i in range(K)]
    total_svcs = [sum(f.get("service_min", 60) for f in clusters[i]) for i in range(K)]
    farm_counts = [len(clusters[i]) for i in range(K)]

    print(f"\n  [균형 지표]")
    print(f"  농장 수:    최대 {max(farm_counts)}개 / 최소 {min(farm_counts)}개 "
          f"(차이 {max(farm_counts)-min(farm_counts)}개)")
    print(f"  위험도 합:  최대 {max(total_risks):.3f} / 최소 {min(total_risks):.3f} "
          f"(차이 {round(max(total_risks)-min(total_risks),3)})")
    print(f"  처리시간:   최대 {max(total_svcs)}분 / 최소 {min(total_svcs)}분 "
          f"(차이 {max(total_svcs)-min(total_svcs)}분)")


def compare_v1_v2(farms, K):
    """v1(위험도 Top K)과 v2(위험도×거리) 비교"""

    # v1: 위험도 Top K만
    sorted_farms = sorted(farms, key=lambda x: x["risk"], reverse=True)
    v1_centroids_initial = sorted_farms[:K]
    print(f"\n  v1 초기 centroid (위험도 Top {K}):")
    for i, f in enumerate(v1_centroids_initial):
        print(f"    팀{i+1}: {f['id']} 위험도={f['risk']} 위도={f['lat']:.3f}")

    centroids_v1 = [{"lat": f["lat"], "lon": f["lon"]} for f in v1_centroids_initial]
    prev = None
    clusters_v1 = {i: [] for i in range(K)}
    for _ in range(100):
        clusters_v1 = {i: [] for i in range(K)}
        assignments = {}
        for farm in farms:
            dists = [haversine_km(farm["lat"],farm["lon"],c["lat"],c["lon"])
                     for c in centroids_v1]
            closest = dists.index(min(dists))
            clusters_v1[closest].append(farm)
            assignments[farm["id"]] = closest
        if assignments == prev: break
        prev = assignments
        for i in range(K):
            if clusters_v1[i]:
                centroids_v1[i] = {
                    "lat": sum(f["lat"] for f in clusters_v1[i])/len(clusters_v1[i]),
                    "lon": sum(f["lon"] for f in clusters_v1[i])/len(clusters_v1[i])
                }

    print_cluster_summary(clusters_v1, K, f"v1 결과 (위험도 Top {K} centroid)")

    # v2: 위험도 × 거리
    print(f"\n  v2 초기 centroid (위험도 × 거리):")
    clusters_v2, _ = risk_clustering_v2(farms, K)
    print_cluster_summary(clusters_v2, K, f"v2 결과 (위험도 × 거리 centroid)")

    # centroid 지리 분산 비교
    v1_init_lats = [f["lat"] for f in v1_centroids_initial]
    print(f"\n  [초기 centroid 지리 분산 비교]")
    print(f"  v1 위도 범위: {min(v1_init_lats):.3f} ~ {max(v1_init_lats):.3f} "
          f"(남북 {round((max(v1_init_lats)-min(v1_init_lats))*111,1)}km)")


# ================================================================
# 테스트 실행
# ================================================================

if __name__ == "__main__":
    with open("/home/claude/pocheon_realistic_data.json", encoding="utf-8") as f:
        data = json.load(f)

    farms = data["nodes"]["farms"]

    print("="*55)
    print("  위험도 기반 클러스터링 v2 테스트")
    print("="*55)
    print(f"  전체 농장 수: {len(farms)}개")

    for K in [2, 3]:
        print(f"\n\n{'━'*55}")
        print(f"  K={K} 비교: v1 vs v2")
        print(f"{'━'*55}")
        compare_v1_v2(farms, K)

