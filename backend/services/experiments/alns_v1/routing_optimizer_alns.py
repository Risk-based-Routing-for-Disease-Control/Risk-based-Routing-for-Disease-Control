import json
import random
import math

# ================================================================
# 배차 최적화 알고리즘 - ALNS (Adaptive Large Neighborhood Search)
#
# LNS 대비 변경사항:
#   - Destroy 전략 3개 (위험도 기준 / 이동비용 기준 / 완전 랜덤)
#   - Repair 전략 2개 (위험도/비용 효율 / 순수 위험도)
#   - 각 전략이 가중치로 경쟁 → 성과 좋은 전략이 더 자주 선택됨
#   - 가중치는 매 iteration마다 자동 업데이트 (적응)
# ================================================================

random.seed(42)

# 실행할 데이터 파일 경로 (원하는 케이스로 교체 가능)
DATA_PATH = "/home/claude/pocheon_realistic_data.json"

with open(DATA_PATH, encoding="utf-8") as f:
    data = json.load(f)

MAX_TIME = data["meta"]["max_time_min"]
time_matrix = data["time_matrix"]
farm_map = {f["id"]: f for f in data["nodes"]["farms"]}
disinfection_ids = [d["id"] for d in data["nodes"]["disinfections"]]
all_farm_ids = list(farm_map.keys())


# ================================================================
# Phase 1. 공통 함수 (변경 없음)
# ================================================================

def calc_total_time(route):
    travel = sum(time_matrix[route[i]][route[i+1]] for i in range(len(route)-1))
    service = sum(farm_map[n]["service_min"] for n in route if n in farm_map)
    return round(travel+service,1), round(travel,1), round(service,1)

def calc_total_risk(route):
    visited = [n for n in route if n in farm_map]
    return round(sum(farm_map[n]["risk"] for n in visited),3), visited

def calc_overhead(route):
    oh = 0
    for i in range(len(route)-1):
        cur, nxt = route[i], route[i+1]
        if cur in farm_map and nxt in farm_map:
            oh += min(time_matrix[cur][d]+time_matrix[d][nxt]-time_matrix[cur][nxt]
                      for d in disinfection_ids)
    return round(oh, 1)

def time_with_dis(route):
    t,_,_ = calc_total_time(route)
    return round(t + calc_overhead(route), 1)

def is_valid_route(route):
    violations = []
    if route[0]!="depot" or route[-1]!="depot":
        violations.append("depot 오류")
    t,_,_ = calc_total_time(route)
    if t > MAX_TIME: violations.append(f"시간초과 {t}분")
    fv = [n for n in route if n in farm_map]
    if len(fv)!=len(set(fv)): violations.append("중복방문")
    return len(violations)==0, violations


# ================================================================
# Phase 2. Greedy 초기해 (변경 없음)
# ================================================================

def greedy_route(farm_ids):
    unvisited = list(farm_ids)
    route = ["depot","depot"]
    while unvisited:
        best_farm, best_score, best_pos = None, -1, None
        for fid in unvisited:
            for pos in range(1, len(route)):
                prev, nxt = route[pos-1], route[pos]
                cost = (time_matrix[prev][fid]+time_matrix[fid][nxt]
                        -time_matrix[prev][nxt]+farm_map[fid]["service_min"])
                trial = route[:pos]+[fid]+route[pos:]
                if time_with_dis(trial) > MAX_TIME: continue
                score = farm_map[fid]["risk"] / max(cost, 1)
                if score > best_score:
                    best_score, best_farm, best_pos = score, fid, pos
        if best_farm is None: break
        route = route[:best_pos]+[best_farm]+route[best_pos:]
        unvisited.remove(best_farm)
    return route


# ================================================================
# Phase 3. ALNS
# ================================================================

# --- Destroy 전략 3개 ---

def destroy_by_risk(route, n):
    """
    D1. 위험도 기준 제거
    위험도 하위 50% 중에서 n개 제거
    → 효율 낮은 농장을 제거해서 더 좋은 농장으로 교체 시도
    """
    farms = [x for x in route if x in farm_map]
    by_risk = sorted(farms, key=lambda x: farm_map[x]["risk"])
    pool = by_risk[:max(1, len(by_risk)//2)]
    removed = random.sample(pool, min(n, len(pool)))
    new_route = route[:]
    for f in removed: new_route.remove(f)
    return new_route, removed

def destroy_by_cost(route, n):
    """
    D2. 이동비용 기준 제거
    위험도/이동비용 효율이 낮은 농장 n개 제거
    → 이동시간을 많이 잡아먹는 비효율 농장 제거
    → 케이스2처럼 시간이 빡빡할 때 특히 효과적
    """
    farms = [x for x in route if x in farm_map]
    if len(farms) < 2:
        return destroy_by_risk(route, n)

    efficiencies = []
    for i, f in enumerate(route):
        if f not in farm_map: continue
        idx = route.index(f)
        prev = route[idx-1]
        nxt  = route[idx+1]
        move_cost = time_matrix[prev][f] + time_matrix[f][nxt]
        eff = farm_map[f]["risk"] / max(move_cost, 1)
        efficiencies.append((f, eff))

    # 효율 낮은 순 정렬 → 하위 50% pool
    efficiencies.sort(key=lambda x: x[1])
    pool = [f for f, _ in efficiencies[:max(1, len(efficiencies)//2)]]
    removed = random.sample(pool, min(n, len(pool)))
    new_route = route[:]
    for f in removed: new_route.remove(f)
    return new_route, removed

def destroy_random(route, n):
    """
    D3. 완전 랜덤 제거
    어떤 농장이든 랜덤으로 n개 제거
    → 탐색 다양성 확보, 국소 최적 탈출용
    """
    farms = [x for x in route if x in farm_map]
    removed = random.sample(farms, min(n, len(farms)))
    new_route = route[:]
    for f in removed: new_route.remove(f)
    return new_route, removed

# --- Repair 전략 2개 ---

def repair_by_efficiency(route, candidates):
    """
    R1. 위험도/비용 효율 기준 삽입
    위험도/처리시간 비율이 높은 후보부터 최적 위치에 삽입
    → 시간 대비 효율이 좋은 농장 우선
    """
    cands = sorted(candidates,
                   key=lambda x: farm_map[x]["risk"]/max(farm_map[x]["service_min"],1),
                   reverse=True)
    return _insert_candidates(route, cands)

def repair_by_risk(route, candidates):
    """
    R2. 순수 위험도 기준 삽입
    위험도가 높은 후보부터 최적 위치에 삽입
    → 처리시간 무관하게 위험도 최우선
    → 위기 상황(케이스2, 4)에서 효과적
    """
    cands = sorted(candidates, key=lambda x: farm_map[x]["risk"], reverse=True)
    return _insert_candidates(route, cands)

def _insert_candidates(route, cands):
    """후보 농장들을 최적 위치에 순서대로 삽입"""
    cur = route[:]
    for cand in cands:
        best_pos, best_cost = None, float("inf")
        for pos in range(1, len(cur)):
            prev, nxt = cur[pos-1], cur[pos]
            cost = time_matrix[prev][cand]+time_matrix[cand][nxt]-time_matrix[prev][nxt]
            if cost < best_cost:
                best_cost, best_pos = cost, pos
        if best_pos is not None:
            trial = cur[:best_pos]+[cand]+cur[best_pos:]
            if time_with_dis(trial) <= MAX_TIME:
                cur = trial
    return cur

# --- ALNS 메인 루프 ---

def alns_improve(route, all_farm_ids, max_iter=500, destroy_count=2):
    """
    ALNS 메인 함수

    가중치 관리:
      - destroy_weights[i]: i번 전략이 선택될 확률
      - repair_weights[i]:  i번 전략이 선택될 확률
      - 성과 점수: 최고해 갱신=3, 현재해 개선=2, 개선없음=0
      - decay=0.1: 가중치가 천천히 적응 (급격한 변화 방지)
    """
    DECAY = 0.1
    SCORE_BEST  = 3   # 전체 최고해 갱신
    SCORE_BETTER = 2  # 현재 해보다 개선

    destroy_fns = [destroy_by_risk, destroy_by_cost, destroy_random]
    repair_fns  = [repair_by_efficiency, repair_by_risk]
    destroy_names = ["D1_위험도기준", "D2_이동비용기준", "D3_랜덤"]
    repair_names  = ["R1_효율기준", "R2_위험도기준"]

    # 초기 가중치: 균등
    d_weights = [1.0] * len(destroy_fns)
    r_weights = [1.0] * len(repair_fns)

    # 성과 추적
    d_scores = [0.0] * len(destroy_fns)
    r_scores = [0.0] * len(repair_fns)
    d_counts = [0] * len(destroy_fns)
    r_counts = [0] * len(repair_fns)

    best_route = route[:]
    best_risk, _ = calc_total_risk(best_route)
    no_imp = 0

    for iteration in range(max_iter):
        if no_imp >= 50:
            print(f"    조기 종료 ({iteration}번째, 연속 50번 개선 없음)")
            break

        current_route = best_route[:]
        farms_in = [n for n in current_route if n in farm_map]
        if not farms_in: break

        # --- 전략 선택 (가중치 기반 룰렛 휠) ---
        d_idx = _roulette(d_weights)
        r_idx = _roulette(r_weights)

        # --- Destroy ---
        actual_destroy = min(destroy_count, len(farms_in))
        destroyed_route, removed = destroy_fns[d_idx](current_route, actual_destroy)

        # --- Repair ---
        visited = {n for n in destroyed_route if n in farm_map}
        candidates = [f for f in all_farm_ids if f not in visited]
        repaired_route = repair_fns[r_idx](destroyed_route, candidates)

        # --- 성과 평가 ---
        trial_risk, _ = calc_total_risk(repaired_route)
        score = 0

        if trial_risk > best_risk:
            score = SCORE_BEST
            best_risk = trial_risk
            best_route = repaired_route[:]
            no_imp = 0
        elif trial_risk > calc_total_risk(current_route)[0]:
            score = SCORE_BETTER
            no_imp += 1
        else:
            no_imp += 1

        # --- 가중치 업데이트 ---
        d_counts[d_idx] += 1
        r_counts[r_idx] += 1
        d_scores[d_idx] += score
        r_scores[r_idx] += score

        # decay로 점진적 업데이트
        d_weights[d_idx] = (d_weights[d_idx] * (1 - DECAY)
                            + (score / max(d_counts[d_idx], 1)) * DECAY)
        r_weights[r_idx] = (r_weights[r_idx] * (1 - DECAY)
                            + (score / max(r_counts[r_idx], 1)) * DECAY)

        # 가중치가 0 이하로 내려가지 않게
        d_weights = [max(w, 0.01) for w in d_weights]
        r_weights = [max(w, 0.01) for w in r_weights]

    # 전략 사용 통계 출력
    print(f"\n  [ALNS 전략 사용 통계]")
    total_d = sum(d_counts)
    total_r = sum(r_counts)
    for i, name in enumerate(destroy_names):
        pct = round(d_counts[i]/max(total_d,1)*100, 1)
        final_w = round(d_weights[i], 4)
        print(f"    {name}: {d_counts[i]}회 ({pct}%) | 최종가중치: {final_w}")
    for i, name in enumerate(repair_names):
        pct = round(r_counts[i]/max(total_r,1)*100, 1)
        final_w = round(r_weights[i], 4)
        print(f"    {name}: {r_counts[i]}회 ({pct}%) | 최종가중치: {final_w}")

    return best_route

def _roulette(weights):
    """가중치 기반 룰렛 휠 선택"""
    total = sum(weights)
    r = random.uniform(0, total)
    cumulative = 0
    for i, w in enumerate(weights):
        cumulative += w
        if r <= cumulative:
            return i
    return len(weights) - 1


# ================================================================
# Phase 4. 소독소 삽입 (변경 없음)
# ================================================================

def insert_disinfections(route):
    def _ins(r):
        res = [r[0]]
        for i in range(len(r)-1):
            cur, nxt = r[i], r[i+1]
            if cur in farm_map and nxt in farm_map:
                best_d = min(disinfection_ids,
                             key=lambda d: time_matrix[cur][d]+time_matrix[d][nxt]-time_matrix[cur][nxt])
                res.append(best_d)
            res.append(nxt)
        return res
    fr = [n for n in route if n not in disinfection_ids]
    final = _ins(fr)
    t,_,_ = calc_total_time(final)
    while t > MAX_TIME:
        farms = [n for n in fr if n in farm_map]
        if not farms: break
        worst = min(farms, key=lambda x: farm_map[x]["risk"])
        fr = [n for n in fr if n != worst]
        final = _ins(fr)
        t,_,_ = calc_total_time(final)
    return final


# ================================================================
# 실행 및 출력
# ================================================================

def print_summary(label, route):
    total_time, travel, service = calc_total_time(route)
    total_risk, visited = calc_total_risk(route)
    valid, violations = is_valid_route(route)
    overhead = calc_overhead(route)
    print(f"\n[ {label} ]")
    print(f"  경로:      {' → '.join(route)}")
    print(f"  방문 농장: {visited} ({len(visited)}개)")
    print(f"  이동 {travel}분 + 처리 {service}분 = 총 {total_time}분 / {MAX_TIME}분")
    if overhead > 0:
        print(f"  소독소 예상 추가: {overhead}분 → 예상 최종 {round(total_time+overhead,1)}분")
    print(f"  총 위험도: {total_risk}")
    print(f"  유효성:    {'✅ 통과' if valid else '❌ '+', '.join(violations)}")

print("="*60)
print("  배차 최적화 알고리즘 ALNS 실행")
print("="*60)
print(f"  데이터: {data['meta'].get('case', data['meta']['description'][:30])}")
print(f"  대상 농장: {all_farm_ids}")
print(f"  최대 시간: {MAX_TIME}분")

print("\n── Phase 2: Greedy 초기해 ───────────────────────────")
greedy = greedy_route(all_farm_ids)
print_summary("Greedy", greedy)

print("\n── Phase 3: ALNS 개선 ───────────────────────────────")
improved = alns_improve(greedy, all_farm_ids, max_iter=500, destroy_count=2)
print_summary("ALNS 개선", improved)
g_risk,_ = calc_total_risk(greedy)
i_risk,_ = calc_total_risk(improved)
print(f"\n  위험도 개선: {g_risk} → {i_risk} (▲{round(i_risk-g_risk,3)})")

print("\n── Phase 4: 소독소 삽입 ─────────────────────────────")
final = insert_disinfections(improved)
print_summary("최종 경로 (소독소 포함)", final)

print("\n"+"="*60)
print("  최종 결과 요약")
print("="*60)
total_time,_,_ = calc_total_time(final)
total_risk, visited = calc_total_risk(final)
print(f"  방문 농장:   {len(visited)}개 / 전체 {len(all_farm_ids)}개")
print(f"  총 위험도:   {total_risk}")
print(f"  총 소요시간: {total_time}분 ({round(total_time/60,1)}시간)")
print(f"  최종 경로:\n    {' → '.join(final)}")


# ================================================================
# LNS vs ALNS 전체 케이스 비교
# ================================================================

def run_lns(data_path):
    with open(data_path, encoding="utf-8") as f:
        d = json.load(f)
    random.seed(42)
    MAX = d["meta"]["max_time_min"]
    tm = d["time_matrix"]
    fm = {f["id"]: f for f in d["nodes"]["farms"]}
    dids = [x["id"] for x in d["nodes"]["disinfections"]]
    aids = list(fm.keys())

    def tt(r):
        tr = sum(tm[r[i]][r[i+1]] for i in range(len(r)-1))
        sv = sum(fm[n]["service_min"] for n in r if n in fm)
        return round(tr+sv,1)
    def risk(r): return round(sum(fm[n]["risk"] for n in r if n in fm),3)
    def oh(r):
        o=0
        for i in range(len(r)-1):
            c,n=r[i],r[i+1]
            if c in fm and n in fm:
                o+=min(tm[c][x]+tm[x][n]-tm[c][n] for x in dids)
        return o
    def twd(r): return round(tt(r)+oh(r),1)

    def greedy(aids):
        uv=list(aids); route=["depot","depot"]
        while uv:
            bf,bs,bp=None,-1,None
            for fid in uv:
                for pos in range(1,len(route)):
                    p,n=route[pos-1],route[pos]
                    c=(tm[p][fid]+tm[fid][n]-tm[p][n]+fm[fid]["service_min"])
                    t=route[:pos]+[fid]+route[pos:]
                    if twd(t)>MAX: continue
                    s=fm[fid]["risk"]/max(c,1)
                    if s>bs: bs,bf,bp=s,fid,pos
            if bf is None: break
            route=route[:bp]+[bf]+route[bp:]; uv.remove(bf)
        return route

    def lns(route, seed=42):
        random.seed(seed); best=route[:]; br=risk(best); ni=0
        for _ in range(500):
            if ni>=50: break
            cur=best[:]; fi=[x for x in cur if x in fm]
            if not fi: break
            ac=min(2,len(fi))
            if random.random()<0.1: rm=random.sample(fi,ac)
            else:
                br2=sorted(fi,key=lambda x:fm[x]["risk"]); pool=br2[:max(1,len(br2)//2)]
                rm=random.sample(pool,ac)
            for f in rm: cur.remove(f)
            vis={x for x in cur if x in fm}
            cands=sorted([f for f in aids if f not in vis],
                         key=lambda x:fm[x]["risk"]/max(fm[x]["service_min"],1),reverse=True)
            for cand in cands:
                bp2,bc=None,float("inf")
                for pos in range(1,len(cur)):
                    p,n=cur[pos-1],cur[pos]
                    c=tm[p][cand]+tm[cand][n]-tm[p][n]
                    if c<bc: bc,bp2=c,pos
                if bp2:
                    t=cur[:bp2]+[cand]+cur[bp2:]
                    if twd(t)<=MAX: cur=t
            r2=risk(cur)
            if r2>br: br,best,ni=r2,cur[:],0
            else: ni+=1
        return best

    g=greedy(aids); gr=risk(g)
    imp=lns(g); ir=risk(imp)
    return gr, ir

def run_alns_only(data_path):
    with open(data_path, encoding="utf-8") as f:
        d = json.load(f)
    # 전역 변수 임시 교체
    global MAX_TIME, time_matrix, farm_map, disinfection_ids, all_farm_ids
    MAX_TIME = d["meta"]["max_time_min"]
    time_matrix = d["time_matrix"]
    farm_map = {f["id"]: f for f in d["nodes"]["farms"]}
    disinfection_ids = [x["id"] for x in d["nodes"]["disinfections"]]
    all_farm_ids = list(farm_map.keys())
    random.seed(42)
    g = greedy_route(all_farm_ids)
    gr = calc_total_risk(g)[0]
    imp = alns_improve(g, all_farm_ids, max_iter=500, destroy_count=2)
    ir = calc_total_risk(imp)[0]
    return gr, ir

cases = [
    ("/home/claude/case1_uniform_normal.json",   "케이스1: 균등_보통"),
    ("/home/claude/case2_crisis_tight.json",     "케이스2: 위기_빡빡"),
    ("/home/claude/case3_bird_normal.json",      "케이스3: 철새혼합_보통"),
    ("/home/claude/case4_epicenter_tight.json",  "케이스4: 진원지_빡빡"),
    ("/home/claude/case5_dispersed_normal.json", "케이스5: 분산_보통"),
]

print("\n\n" + "="*65)
print("  LNS vs ALNS 전체 케이스 비교")
print("="*65)
print(f"  {'케이스':<20} {'Greedy':>8} {'LNS':>8} {'ALNS':>8} {'LNS개선':>8} {'ALNS개선':>9}")
print(f"  {'-'*60}")

import io, sys

for path, label in cases:
    # LNS
    lg, li = run_lns(path)

    # ALNS (출력 억제)
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    ag, ai = run_alns_only(path)
    sys.stdout = old_stdout

    lns_imp  = round(li - lg, 3)
    alns_imp = round(ai - ag, 3)
    lns_str  = f"▲{lns_imp}"  if lns_imp  > 0 else "-"
    alns_str = f"▲{alns_imp}" if alns_imp > 0 else "-"
    better = "🏆 ALNS" if ai > li else ("🏆 LNS" if li > ai else "동점")
    print(f"  {label:<20} {lg:>8.3f} {li:>8.3f} {ai:>8.3f} {lns_str:>8} {alns_str:>9}  {better}")

