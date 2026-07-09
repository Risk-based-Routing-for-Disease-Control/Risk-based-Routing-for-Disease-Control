"""위험기반 라우팅 타임라인 데이터셋 생성.

`최종감염농장/{PROVINCE}_최종감염농장.csv`의 감염 이벤트마다 반경 RADIUS_KM 내 농장(`data/{PROVINCE}/농장현황/`)을
찾아 일별 타임라인을 만든다. 알고리즘 설계는 `/Users/jeon-eunhee/.claude/plans/adaptive-sparking-lemur.md` 참고.

경기도는 농장현황 원본에 좌표가 대부분 있어 감염 이벤트 주소만 지오코딩하면 됐지만, 다른 시/도는
농장현황 원본에 좌표가 전혀 없어(README 참고) census 주소 전체를 Kakao API로 지오코딩한다
(`load_census_universe`의 census 지오코딩 단계).
"""
import glob
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geocode_lib as gl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVESTOCK_CODES_PATH = os.path.join(ROOT, "livestock_codes.csv")

RADIUS_KM = 3.0
LOOKBACK_DAYS = 7
LOOKFORWARD_DAYS = 7
DEAD_DAYS = 15

# 농장 식별 키는 (농장명, 소재지지번주소)만 쓴다. 원본 농장현황의 시군명 컬럼이 주소와 어긋나는 행이
# 12%(941/7,851)나 있어서(예: 시군명="김포시"인데 주소는 "경기도 여주시 ..." — 같은 농장이 조사 시점마다
# 다른 시군명으로 잘못 기록된 경우도 있음), 시군명을 키에 넣으면 같은 농장이 두 개로 쪼개질 수 있다.
# farm_county는 항상 주소 두 번째 토큰에서 다시 계산해 표시용으로만 쓴다.
FARM_KEY_COLS = ["농장명", "소재지지번주소"]


def county_from_address(addr_series):
    return addr_series.astype(str).str.split().str[1]


def build_self_outbreak_dates(infected):
    """(농장명, 소재지지번주소) -> 그 농장의 발생일 목록. 자가감염 농장의 census 기록을
    '최신' 대신 '발생일에 가장 가까운 조사날짜'로 고르는 데 쓴다."""
    dates_by_key = {}
    for _, row in infected.iterrows():
        addr = row["소재지지번주소"] if pd.notna(row["소재지지번주소"]) else row["FARM_LOCPLC"]
        if pd.isna(addr):
            continue
        name = resolve_farm_name(row)
        outbreak_date = pd.to_datetime(str(int(row["OCCRRNC_DE"])), format="%Y%m%d")
        dates_by_key.setdefault((name, addr), []).append(outbreak_date)
    return dates_by_key


def load_census_universe(self_outbreak_dates_by_key, census_dir):
    """data/{PROVINCE}/농장현황/*_농장현황.csv를 합쳐 농장 단위(농장명·주소)로 dedupe.

    자가감염 농장(self_outbreak_dates_by_key에 키가 있는 농장)은 여러 조사기록 중
    발생일에 가장 가까운 조사날짜를 고른다. 그 외 농장은 기존처럼 가장 최신 조사기록을 쓴다.
    """
    files = [
        f
        for f in glob.glob(os.path.join(census_dir, "*_농장현황.csv"))
        if not os.path.basename(f).startswith("_")
    ]
    frames = []
    for f in files:
        df = pd.read_csv(f, encoding="utf-8-sig")
        df.columns = [c.strip() for c in df.columns]
        frames.append(df)
    census = pd.concat(frames, ignore_index=True)

    lat = pd.to_numeric(census["WGS84위도"], errors="coerce")
    lon = pd.to_numeric(census["WGS84경도"], errors="coerce")
    swapped = lat > 90  # 위도는 한국 범위(33~39)를 벗어날 수 없음 -> 위경도가 뒤바뀐 행
    census["lat"] = lat.where(~swapped, lon)
    census["lon"] = lon.where(~swapped, lat)
    census["census_native_coord"] = census["lat"].notna()

    missing_coord = ~census["census_native_coord"]
    if missing_coord.any():
        api_key = gl.load_api_key()
        cache = gl.load_cache()
        unique_addrs = sorted(census.loc[missing_coord, "소재지지번주소"].dropna().unique().tolist())
        print(f"  census 좌표 없는 주소 지오코딩: {len(unique_addrs)}개")
        gl.geocode_addresses(unique_addrs, api_key, cache)
        census.loc[missing_coord, "lat"] = census.loc[missing_coord, "소재지지번주소"].map(
            lambda a: cache.get(a, {}).get("lat")
        )
        census.loc[missing_coord, "lon"] = census.loc[missing_coord, "소재지지번주소"].map(
            lambda a: cache.get(a, {}).get("lon")
        )

    census["조사날짜_dt"] = pd.to_datetime(census["조사날짜"], errors="coerce")
    census["has_coord"] = census["lat"].notna()

    keys = list(zip(census["농장명"], census["소재지지번주소"]))
    outbreak_lists = [self_outbreak_dates_by_key.get(k) for k in keys]
    is_self = pd.Series([v is not None for v in outbreak_lists], index=census.index)

    def min_dist_to_outbreaks(survey_date, outbreaks):
        if pd.isna(survey_date) or not outbreaks:
            return pd.Timedelta.max
        return min(abs(survey_date - od) for od in outbreaks)

    census["_date_dist"] = [
        min_dist_to_outbreaks(d, outbreaks)
        for d, outbreaks in zip(census["조사날짜_dt"], outbreak_lists)
    ]

    self_rows = census[is_self].sort_values(["has_coord", "_date_dist"], ascending=[False, True])
    other_rows = census[~is_self].sort_values(["has_coord", "조사날짜_dt"], ascending=[False, False])
    census = pd.concat([self_rows, other_rows])
    census = census.drop_duplicates(subset=FARM_KEY_COLS, keep="first")

    universe = pd.DataFrame(
        {
            "farm_county": county_from_address(census["소재지지번주소"]),
            "farm_name": census["농장명"],
            "farm_address": census["소재지지번주소"],
            "latitude": census["lat"],
            "longitude": census["lon"],
            "livestock_name": census["축종명"],
            "livestock_type": census["상세구분"],
            "head_count": census["사육두수(마리)"],
            "farm_source": np.where(census["census_native_coord"], "census", "census_geocoded"),
            "survey_date": census["조사날짜"],
        }
    )

    # 축종명(livestock_name)이 비어있어도 상세구분(livestock_type)이 한 축종에만 속하는 값이면
    # (예: '육계'/'산란계'/'종계' -> 닭) livestock_codes.csv 기준으로 축종명을 역으로 채운다.
    detail_to_name = load_detail_to_name_map()
    missing_name = universe["livestock_name"].isna() & universe["livestock_type"].notna()
    universe.loc[missing_name, "livestock_name"] = universe.loc[missing_name, "livestock_type"].map(detail_to_name)

    # 상세구분 자리에 축종명 값 자체가 잘못 들어온 행(예: livestock_type='오리')은 그 값을 그대로 livestock_name에 채운다.
    valid_names = set(pd.read_csv(LIVESTOCK_CODES_PATH)["축종명"].unique())
    still_missing = universe["livestock_name"].isna() & universe["livestock_type"].isin(valid_names)
    universe.loc[still_missing, "livestock_name"] = universe.loc[still_missing, "livestock_type"]

    return universe.reset_index(drop=True)


def resolve_farm_name(row):
    """농장명이 비어있으면(원본 발생정보에 농장명 자체가 없는 경우) 같은 동/리의 다른 발생건과
    엉뚱하게 합쳐지지 않도록 발생일로 구분되는 임시 이름을 부여한다."""
    if pd.notna(row.get("농장명")):
        return row["농장명"]
    return f"미상_{int(row['OCCRRNC_DE'])}"


def load_livestock_code_map():
    """표준 축산코드 -> (축종명, 상세구분) 매핑. 감염 이벤트의 LVSTCKSPC_CODE로 livestock_name/type을 채우는 데 쓴다."""
    codes = pd.read_csv(LIVESTOCK_CODES_PATH)
    return {
        int(row["표준 축산코드"]): (row["축종명"], row["상세구분"])
        for _, row in codes.iterrows()
    }


def load_detail_to_name_map():
    """상세구분 -> 축종명. 상세구분이 한 축종에만 속하는 경우만 포함한다
    ('비분류'/'기타'는 닭·오리 등 여러 축종에 걸쳐 있어 상세구분만으로는 축종을 특정할 수 없어 제외)."""
    codes = pd.read_csv(LIVESTOCK_CODES_PATH)
    grouped = codes.groupby("상세구분")["축종명"].unique()
    return {detail: names[0] for detail, names in grouped.items() if len(names) == 1}


def geocode_events_missing_coords(infected, universe):
    """좌표가 없는 감염 이벤트(미매칭 171건 + 매칭됐지만 좌표가 빈 6건)를 주소로 지오코딩해 농장 유니버스에 추가."""
    code_map = load_livestock_code_map()
    infected_name = infected.apply(resolve_farm_name, axis=1)
    infected_addr = infected["소재지지번주소"].where(infected["소재지지번주소"].notna(), infected["FARM_LOCPLC"])
    merged = pd.DataFrame({"farm_name": infected_name, "farm_address": infected_addr}).merge(
        universe[["farm_name", "farm_address", "latitude", "longitude"]],
        on=["farm_name", "farm_address"],
        how="left",
    )
    needs_geocode = merged["latitude"].isna()
    print(f"  좌표 없는 감염 이벤트: {needs_geocode.sum()}건 (지오코딩 대상)")

    addr_col = infected.loc[needs_geocode.values].apply(
        lambda r: r["소재지지번주소"] if pd.notna(r["소재지지번주소"]) else r["FARM_LOCPLC"], axis=1
    )
    api_key = gl.load_api_key()
    cache = gl.load_cache()
    unique_addrs = sorted(addr_col.dropna().unique().tolist())
    gl.geocode_addresses(unique_addrs, api_key, cache)

    new_rows = []
    seen = set()
    for idx in needs_geocode[needs_geocode].index:
        row = infected.loc[idx]
        addr = row["소재지지번주소"] if pd.notna(row["소재지지번주소"]) else row["FARM_LOCPLC"]
        name = resolve_farm_name(row)
        if pd.isna(addr) or addr not in cache or cache[addr]["lat"] is None:
            continue
        key = (name, addr)
        if key in seen:
            continue
        seen.add(key)
        code = row.get("LVSTCKSPC_CODE")
        mapped = code_map.get(int(code)) if pd.notna(code) else None
        livestock_name, livestock_type = mapped if mapped else (row.get("축종명"), row.get("상세구분"))
        new_rows.append(
            {
                "farm_county": county_from_address(pd.Series([addr])).iloc[0],
                "farm_name": name,
                "farm_address": addr,
                "latitude": cache[addr]["lat"],
                "longitude": cache[addr]["lon"],
                "livestock_name": livestock_name,
                "livestock_type": livestock_type,
                "head_count": np.nan,
                "farm_source": "geocoded",
                "survey_date": np.nan,
            }
        )
    failed = needs_geocode.sum() - len(new_rows)
    print(f"  지오코딩 성공: {len(new_rows)}건, 실패(분석 제외): {failed}건")
    geocoded_df = pd.DataFrame(new_rows)
    universe_full = pd.concat([universe, geocoded_df], ignore_index=True)
    universe_full = universe_full.drop_duplicates(subset=["farm_name", "farm_address"], keep="first")
    return universe_full.reset_index(drop=True)


def build_events(infected, universe):
    """감염 이벤트(원본 274건)를 농장 유니버스의 행 인덱스에 연결."""
    key_to_idx = {
        (r.farm_name, r.farm_address): i for i, r in universe.iterrows()
    }

    events = []
    unresolved = 0
    for _, row in infected.iterrows():
        addr = row["소재지지번주소"] if pd.notna(row["소재지지번주소"]) else row["FARM_LOCPLC"]
        name = resolve_farm_name(row)
        farm_idx = key_to_idx.get((name, addr))
        if farm_idx is None:
            unresolved += 1
            continue
        outbreak_date = pd.to_datetime(str(int(row["OCCRRNC_DE"])), format="%Y%m%d")
        events.append({"farm_idx": farm_idx, "outbreak_date": outbreak_date})

    events_df = pd.DataFrame(events).drop_duplicates(subset=["farm_idx", "outbreak_date"])
    print(f"  연결 안 된(좌표 끝내 못 구한) 감염 이벤트: {unresolved}건 (분석 제외)")
    print(f"  최종 분석 대상 감염 이벤트: {len(events_df)}건")
    return events_df.reset_index(drop=True)


def haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    return 2 * 6371 * np.arcsin(np.sqrt(a))


def find_neighbors_within_radius(events_df, universe):
    """이벤트마다 반경 RADIUS_KM 내 농장 인덱스(자기 자신 제외) 목록을 반환."""
    farm_lat = universe["latitude"].to_numpy()
    farm_lon = universe["longitude"].to_numpy()
    event_lat = universe.loc[events_df["farm_idx"], "latitude"].to_numpy()
    event_lon = universe.loc[events_df["farm_idx"], "longitude"].to_numpy()

    dist = haversine_km(event_lat[:, None], event_lon[:, None], farm_lat[None, :], farm_lon[None, :])
    within = dist <= RADIUS_KM

    neighbor_lists = []
    for i, farm_idx in enumerate(events_df["farm_idx"]):
        idxs = np.where(within[i])[0]
        idxs = idxs[idxs != farm_idx]
        neighbor_lists.append(idxs)
    return neighbor_lists


def accumulate_contributions(events_df, neighbor_lists):
    """농장 인덱스별로 (date, is_self, outbreak_date) 기여를 모은다."""
    contributions = {}  # farm_idx -> list of (date, is_self, outbreak_date)

    def add(farm_idx, dates, is_self, outbreak_date):
        contributions.setdefault(farm_idx, []).append((dates, is_self, outbreak_date))

    for (_, ev), neighbors in zip(events_df.iterrows(), neighbor_lists):
        farm_idx = ev["farm_idx"]
        outbreak_date = ev["outbreak_date"]
        ref_date = outbreak_date - pd.Timedelta(days=LOOKBACK_DAYS)

        self_dates = pd.date_range(ref_date, outbreak_date - pd.Timedelta(days=1))
        add(farm_idx, self_dates, True, outbreak_date)

        neighbor_dates = pd.date_range(ref_date, outbreak_date + pd.Timedelta(days=LOOKFORWARD_DAYS))
        for n_idx in neighbors:
            add(n_idx, neighbor_dates, False, outbreak_date)

    return contributions


def resolve_timeline(farm_idx, contrib_list, self_outbreak_dates):
    """한 농장의 기여 목록을 날짜별 (label_infected, outbreak_date)로 합치고 15일 삭제기간을 적용."""
    rows = []
    for dates, is_self, outbreak_date in contrib_list:
        for d in dates:
            rows.append((d, is_self, outbreak_date))
    df = pd.DataFrame(rows, columns=["date", "is_self", "outbreak_date"])

    # label=1(자기 자신의 감염 주간)인 날짜는 반드시 그 자기-발생 이벤트의 outbreak_date를 써야 한다.
    # 같은 날짜에 다른(보통 더 이른) 인근 발생의 이웃-기여가 겹쳐도 그 이벤트의 발생일로 덮이면 안 됨.
    self_df = df[df["is_self"]]
    other_df = df[~df["is_self"]]
    self_outbreak = self_df.groupby("date")["outbreak_date"].min()
    other_outbreak = other_df.groupby("date")["outbreak_date"].min()
    label = pd.Series(False, index=df["date"].unique())
    label.loc[self_outbreak.index] = True

    outbreak_date = other_outbreak.combine_first(self_outbreak)
    outbreak_date.loc[self_outbreak.index] = self_outbreak  # self가 있으면 항상 self 우선

    grouped = pd.DataFrame({"label_infected": label, "outbreak_date": outbreak_date})
    grouped["label_infected"] = grouped["label_infected"].astype(int)
    grouped.loc[grouped["label_infected"] == 0, "outbreak_date"] = pd.NaT

    for d in self_outbreak_dates:
        dead_start, dead_end = d, d + pd.Timedelta(days=DEAD_DAYS)
        mask = (grouped.index >= dead_start) & (grouped.index < dead_end)
        grouped = grouped.loc[~mask]

    grouped = grouped.sort_index()
    grouped["reference_date"] = grouped.index
    grouped["date"] = grouped.index
    return grouped.reset_index(drop=True)


def main(province):
    census_dir = os.path.join(ROOT, "data", province, "농장현황")
    infected_path = os.path.join(ROOT, "최종감염농장", f"{province}_최종감염농장.csv")
    out_path = os.path.join(ROOT, "Final", f"{province}_위험라우팅_타임라인.csv")

    print(f"=== {province} ===")
    print("1. 감염 이벤트 로드")
    infected = pd.read_csv(infected_path, encoding="utf-8-sig")
    infected.columns = [c.strip() for c in infected.columns]
    print(f"  {province} 감염 이벤트(원본): {len(infected)}건")

    print("2. 농장현황 농장 유니버스 구축 (자가감염 농장은 발생일에 가까운 조사기록 선택)")
    self_outbreak_dates_by_key = build_self_outbreak_dates(infected)
    universe = load_census_universe(self_outbreak_dates_by_key, census_dir)
    print(f"  census 농장 유니버스: {len(universe)}개 (좌표 결측 {universe['latitude'].isna().sum()}개 포함)")

    print("3. 좌표 없는 이벤트 지오코딩")
    universe = geocode_events_missing_coords(infected, universe)
    universe = universe[universe["latitude"].notna() & universe["longitude"].notna()].reset_index(drop=True)
    print(f"  최종 농장 유니버스(좌표 보유): {len(universe)}개")

    print("4. 이벤트 -> 농장 유니버스 연결")
    events_df = build_events(infected, universe)

    print("5. 반경 3km 매칭")
    neighbor_lists = find_neighbors_within_radius(events_df, universe)
    isolated = sum(1 for n in neighbor_lists if len(n) == 0)
    print(f"  반경 내 이웃이 0건인 고립 감염 이벤트: {isolated}건 (자기 자신 타임라인은 그대로 포함됨)")

    print("6. 농장별 구간 누적")
    contributions = accumulate_contributions(events_df, neighbor_lists)

    self_outbreaks_by_farm = events_df.groupby("farm_idx")["outbreak_date"].apply(list).to_dict()

    print("7. 농장별 타임라인 조립")
    all_rows = []
    for farm_idx, contrib_list in contributions.items():
        timeline = resolve_timeline(farm_idx, contrib_list, self_outbreaks_by_farm.get(farm_idx, []))
        if timeline.empty:
            continue
        farm_attrs = universe.loc[farm_idx]
        for col in ["farm_county", "farm_name", "farm_address", "latitude", "longitude",
                    "livestock_name", "livestock_type", "head_count", "farm_source", "survey_date"]:
            timeline[col] = farm_attrs[col]
        all_rows.append(timeline)

    result = pd.concat(all_rows, ignore_index=True)
    result = result[[
        "farm_county", "farm_name", "farm_address", "latitude", "longitude",
        "livestock_name", "livestock_type", "head_count", "farm_source", "survey_date",
        "date", "reference_date", "outbreak_date", "label_infected",
    ]]
    result = result.sort_values(["farm_county", "farm_name", "farm_address", "date"]).reset_index(drop=True)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    result.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"\n=== {province} 요약 ===")
    print(f"분석 대상 감염 이벤트: {len(events_df)}건")
    print(f"영향권에 포함된 농장 수: {result[['farm_county','farm_name','farm_address']].drop_duplicates().shape[0]}개")
    print(f"최종 행 수: {len(result)}")
    print(f"label_infected=1 행 수: {(result['label_infected']==1).sum()} (기대값: 이벤트수 x 7 = {len(events_df)*7})")
    print(f"저장 위치: {out_path}")


if __name__ == "__main__":
    provinces = sys.argv[1:] or ["경기도"]
    for province in provinces:
        main(province)
