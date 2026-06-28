import json
import math

# ================================================================
# 위험도 기반 클러스터링 v3
#
# v2에서 추가된 것:
#   클러스터링 완료 후 처리시간 균등 재조정
#   - 처리시간이 많은 클러스터 → 적은 클러스터로 경계 농장 이동
#   - 경계 농장: 현재 클러스터 centroid보다 다른 클러스터 centroid에
#     더 가까운 농장 (지리적으로 경계에 있는 농장)
#   - 지리적 응집성을 최대한 유지하면서 처리시간 균등화
# ================================================================


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(dlon/2)**2)
    return R * 2 * math.asin(math.sqrt(a))


def select_initial_centroids(farms, K):
    """위험도 × 거리 기반 초기 centroid 선택 (v2와 동일)"""
    selected = []
    first = max(farms, key=lambda x: x["risk"])
    selected.append(first)

    for _ in range(1, K):
        best_farm, best_score = None, -1
        for farm in farms:
            if farm in selected:
                continue
            min_dist = min(
                haversine_km(farm["lat"], farm["lon"], c["lat"], c["lon"])
                for c in selected
            )
            score = farm["risk"] * min_dist
            if score > best_score:
                best_score, best_farm = score, farm
        selected.append(best_farm)

    return selected


def kmeans_cluster(farms, K, centroids_init, max_iter=100):
    """K-means 클러스터링 (주어진 초기 centroid로 시작)"""
    centroids = [{"lat": f["lat"], "lon": f["lon"]} for f in centroids_init]
    prev_assignments = None

    for _ in range(max_iter):
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

        # 빈 클러스터 처리
        for i in range(K):
            if not clusters[i]:
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

        if assignments == prev_assignments:
            break
        prev_assignments = assignments

        for i in range(K):
            if clusters[i]:
                centroids[i] = {
                    "lat": sum(f["lat"] for f in clusters[i]) / len(clusters[i]),
                    "lon": sum(f["lon"] for f in clusters[i]) / len(clusters[i])
                }

    return clusters, centroids


def rebalance_service_time(clusters, centroids, K, tolerance_min=60, max_iter=50):
    """
    처리시간 균등 재조정

    방식:
      가장 처리시간이 많은 클러스터에서
      가장 처리시간이 적은 클러스터로
      경계 농장을 하나씩 이동

    경계 농장 선택 기준:
      현재 클러스터 centroid까지 거리 대비
      목표 클러스터 centroid까지 거리 비율이 가장 작은 농장
      (= 목표 클러스터에 가장 가까운 농장)

    tolerance_min:
      팀 간 처리시간 차이가 이 값 이하면 균형 달성으로 판단
      60분 = 1시간 이내 차이면 허용
    """
    print(f"\n  [처리시간 균등 재조정 시작]")
    print(f"  허용 오차: {tolerance_min}분")

    for iteration in range(max_iter):
        # 각 클러스터 처리시간 계산
        service_times = {
            i: sum(f["service_min"] for f in clusters[i])
            for i in range(K)
        }

        max_cluster = max(service_times, key=service_times.get)
        min_cluster = min(service_times, key=service_times.get)
        diff = service_times[max_cluster] - service_times[min_cluster]

        if diff <= tolerance_min:
            print(f"  수렴 완료 ({iteration}번 조정, 최대 차이 {diff}분)")
            break

        # 최대 클러스터에서 경계 농장 찾기
        # 경계 농장: 목표 클러스터 centroid까지 거리 / 현재 클러스터 centroid까지 거리
        # 이 비율이 작을수록 목표 클러스터에 가까운 농장
        best_farm = None
        best_ratio = float("inf")

        for farm in clusters[max_cluster]:
            dist_current = haversine_km(
                farm["lat"], farm["lon"],
                centroids[max_cluster]["lat"], centroids[max_cluster]["lon"]
            )
            dist_target = haversine_km(
                farm["lat"], farm["lon"],
                centroids[min_cluster]["lat"], centroids[min_cluster]["lon"]
            )

            # 0으로 나누기 방지
            ratio = dist_target / max(dist_current, 0.01)

            if ratio < best_ratio:
                best_ratio = ratio
                best_farm = farm

        if best_farm is None:
            break

        # 농장 이동
        clusters[max_cluster].remove(best_farm)
        clusters[min_cluster].append(best_farm)

        new_times = {i: sum(f["service_min"] for f in clusters[i]) for i in range(K)}
        print(f"  조정 {iteration+1}: {best_farm['id']} "
              f"(처리시간 {best_farm['service_min']}분) "
              f"팀{max_cluster+1}→팀{min_cluster+1} | "
              f"차이 {diff}분→{new_times[max_cluster]-new_times[min_cluster]}분")

        # centroid 업데이트
        for i in [max_cluster, min_cluster]:
            if clusters[i]:
                centroids[i] = {
                    "lat": sum(f["lat"] for f in clusters[i]) / len(clusters[i]),
                    "lon": sum(f["lon"] for f in clusters[i]) / len(clusters[i])
                }

    else:
        final_times = {i: sum(f["service_min"] for f in clusters[i]) for i in range(K)}
        final_diff = max(final_times.values()) - min(final_times.values())
        print(f"  최대 반복 도달 (최대 차이 {final_diff}분)")

    return clusters, centroids


def risk_clustering_v3(farms, K, tolerance_min=60, max_iter=100):
    """
    위험도 기반 클러스터링 v3 메인 함수

    Args:
        farms: 농장 리스트
        K: 팀 수
        tolerance_min: 처리시간 균등 허용 오차 (분)
        max_iter: 최대 반복 횟수
    """
    print(f"\n  1단계: 초기 centroid 선택 (위험도 × 거리)")
    initial = select_initial_centroids(farms, K)
    for i, f in enumerate(initial):
        print(f"    팀{i+1}: {f['id']} (위험도 {f['risk']}, 위도 {f['lat']:.3f})")

    print(f"\n  2단계: K-means 클러스터링")
    clusters, centroids = kmeans_cluster(farms, K, initial, max_iter)
    service_times = {i: sum(f["service_min"] for f in clusters[i]) for i in range(K)}
    diff_before = max(service_times.values()) - min(service_times.values())
    print(f"  완료 | 처리시간 차이: {diff_before}분")

    print(f"\n  3단계: 처리시간 균등 재조정")
    clusters, centroids = rebalance_service_time(
        clusters, centroids, K, tolerance_min
    )

    return clusters, centroids


def print_cluster_summary(clusters, K, label=""):
    """클러스터링 결과 요약 출력"""
    print(f"\n  {'='*55}")
    if label:
        print(f"  {label}")
    print(f"  {'팀':>4} {'농장수':>6} {'총위험도':>9} {'평균위험도':>10} {'처리시간합':>10}")
    print(f"  {'-'*52}")

    for i in range(K):
        f_list = clusters[i]
        total_risk = round(sum(f["risk"] for f in f_list), 3)
        avg_risk = round(total_risk / len(f_list), 3) if f_list else 0
        total_svc = sum(f.get("service_min", 60) for f in f_list)
        print(f"  팀{i+1:>2} {len(f_list):>6}개 {total_risk:>9.3f} "
              f"{avg_risk:>10.3f} {total_svc:>8}분")

    print(f"\n  [팀별 담당 농장]")
    for i in range(K):
        sorted_f = sorted(clusters[i], key=lambda x: x["risk"], reverse=True)
        ids = [f["id"] for f in sorted_f]
        risks = [f["risk"] for f in sorted_f]
        print(f"  팀{i+1}: {ids}")
        print(f"       위험도: {risks}")

    total_risks = [sum(f["risk"] for f in clusters[i]) for i in range(K)]
    total_svcs = [sum(f.get("service_min", 60) for f in clusters[i]) for i in range(K)]
    farm_counts = [len(clusters[i]) for i in range(K)]

    print(f"\n  [균형 지표]")
    print(f"  농장 수:   최대 {max(farm_counts)}개 / 최소 {min(farm_counts)}개 "
          f"(차이 {max(farm_counts)-min(farm_counts)}개)")
    print(f"  위험도 합: 최대 {max(total_risks):.3f} / 최소 {min(total_risks):.3f} "
          f"(차이 {round(max(total_risks)-min(total_risks),3)})")
    print(f"  처리시간:  최대 {max(total_svcs)}분 / 최소 {min(total_svcs)}분 "
          f"(차이 {max(total_svcs)-min(total_svcs)}분)")


# ================================================================
# 테스트 실행
# ================================================================

if __name__ == "__main__":
    with open("/home/claude/pocheon_realistic_data.json", encoding="utf-8") as f:
        data = json.load(f)

    farms = data["nodes"]["farms"]

    print("="*58)
    print("  위험도 기반 클러스터링 v3 테스트")
    print("  (위험도×거리 centroid + 처리시간 균등 재조정)")
    print("="*58)
    print(f"  전체 농장 수: {len(farms)}개")
    print(f"  전체 처리시간 합: {sum(f['service_min'] for f in farms)}분")

    for K in [2, 3]:
        print(f"\n\n{'━'*58}")
        print(f"  K={K}")
        print(f"{'━'*58}")

        # v2 결과 (재조정 전)
        initial = select_initial_centroids(farms, K)
        clusters_v2, centroids_v2 = kmeans_cluster(farms, K, initial)
        print_cluster_summary(clusters_v2, K, "v2 결과 (재조정 전)")

        # v3 결과 (재조정 후)
        print(f"\n  ── v3 실행 과정 ──────────────────────────────────")
        clusters_v3, centroids_v3 = risk_clustering_v3(
            farms, K, tolerance_min=60
        )
        print_cluster_summary(clusters_v3, K, "v3 결과 (재조정 후)")

