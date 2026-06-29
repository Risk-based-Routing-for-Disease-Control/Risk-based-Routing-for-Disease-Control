"""ML/ML_{시도}_농장현황_{윈도우}.csv (윈도우: 6months/1year, 각각 1건/alldates 버전)의
WGS84위도/경도 결측치를 채우고 뒤바뀜을 정정한다.

이 파일들은 data/{시도}/농장현황/(원본, 좌표 없음)에서 만들어져서 경기도를 제외하곤
좌표가 전부 비어있다. 같은 주소가 같은 시도의 다른 윈도우 파일에 이미 지오코딩되어
있으면 거기서 가져오고, 어디에도 없는 주소만 Kakao 지오코딩으로 새로 채운다.
ML_전국_농장현황_{윈도우}.csv는 ML_merge_전국.py가 다시 만들 집계본이라 여기서는 건너뛴다.
"""
import glob
import os

import pandas as pd

import geocode_lib as gl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ML_DIR = os.path.join(ROOT, "ML")
LAT_COL = "WGS84위도"
LON_COL = "WGS84경도"
ADDR_COL = "소재지지번주소"
WINDOWS = ["6months", "1year", "6months_alldates", "1year_alldates"]

# 한국 영토의 대략적인 위경도 범위 (geocode_farm_status.py와 동일)
LAT_RANGE = (30, 45)
LON_RANGE = (120, 135)


def fix_swapped(df):
    """위도 컬럼에 경도값이 들어간(원본 데이터 자체의 뒤바뀜) 행을 정정한다."""
    have = df[LAT_COL].notna() & df[LON_COL].notna()
    swapped = have & df[LAT_COL].between(*LON_RANGE) & df[LON_COL].between(*LAT_RANGE)
    n = swapped.sum()
    if n:
        df.loc[swapped, [LAT_COL, LON_COL]] = df.loc[swapped, [LON_COL, LAT_COL]].values
    return n


def build_global_lookup(paths):
    """모든 시도/윈도우 파일을 훑어 주소 -> (lat, lon, coord_precision) 딕셔너리를 만든다."""
    lookup = {}
    for path in paths:
        if not os.path.exists(path):
            continue
        ref = pd.read_csv(path)
        ref = ref.dropna(subset=[LAT_COL, LON_COL, ADDR_COL])
        precision_col = ref["coord_precision"] if "coord_precision" in ref.columns else "exact"
        for addr, lat, lon, prec in zip(ref[ADDR_COL], ref[LAT_COL], ref[LON_COL], precision_col):
            lookup.setdefault(addr, (lat, lon, prec))
    return lookup


def process_file(path, api_key, cache, lookup):
    name = os.path.basename(path)
    df = pd.read_csv(path)

    if "coord_precision" not in df.columns:
        df["coord_precision"] = "exact"

    n_swapped = fix_swapped(df)

    missing_mask = df[LAT_COL].isna() | df[LON_COL].isna()
    n_missing_before = missing_mask.sum()
    print(f"\n=== {name} === 위경도 뒤바뀜 보정: {n_swapped}건, 결측 {n_missing_before}/{len(df)}건")
    if n_missing_before == 0:
        if n_swapped:
            df.to_csv(path, index=False, encoding="utf-8")
        return 0, 0, 0

    filled_from_ref = 0
    for idx in df.index[missing_mask]:
        addr = df.at[idx, ADDR_COL]
        if not pd.notna(addr):
            continue
        hit = lookup.get(addr)
        if not hit:
            entry = cache.get(addr)
            if entry and entry["lat"] is not None:
                hit = (entry["lat"], entry["lon"], "approx_" + entry["source"])
        if hit:
            df.at[idx, LAT_COL], df.at[idx, LON_COL], df.at[idx, "coord_precision"] = hit
            filled_from_ref += 1
    print(f"기존 지오코딩 결과(다른 시도/윈도우 파일+캐시)에서 채움: {filled_from_ref}건")

    still_missing = df[LAT_COL].isna() | df[LON_COL].isna()
    addresses = df.loc[still_missing, ADDR_COL].dropna().unique().tolist()
    if addresses:
        failed = gl.geocode_addresses(addresses, api_key, cache)
        print(f"신규 지오코딩 대상 주소 {len(addresses)}개, 실패 {len(failed)}개")

        filled_new = 0
        for idx in df.index[still_missing]:
            addr = df.at[idx, ADDR_COL]
            entry = cache.get(addr) if pd.notna(addr) else None
            if entry and entry["lat"] is not None:
                df.at[idx, LAT_COL] = entry["lat"]
                df.at[idx, LON_COL] = entry["lon"]
                df.at[idx, "coord_precision"] = "approx_" + entry["source"]
                filled_new += 1
    else:
        filled_new = 0

    n_missing_after = (df[LAT_COL].isna() | df[LON_COL].isna()).sum()
    print(f"신규 지오코딩으로 채움: {filled_new}건, 최종 결측: {n_missing_after}건")

    df.to_csv(path, index=False, encoding="utf-8")
    return filled_from_ref, filled_new, n_missing_after


def main():
    api_key = gl.load_api_key()
    cache = gl.load_cache()

    files = sorted(
        p
        for window in WINDOWS
        for p in glob.glob(os.path.join(ML_DIR, f"ML_*_농장현황_{window}.csv"))
        if not os.path.basename(p).startswith("ML_전국_")
    )

    lookup = build_global_lookup(files)

    totals = {"from_ref": 0, "new_geocode": 0, "still_missing": 0}
    for path in files:
        a, b, c = process_file(path, api_key, cache, lookup)
        totals["from_ref"] += a
        totals["new_geocode"] += b
        totals["still_missing"] += c

    print("\n=== TOTAL ===")
    print(totals)
    print("\n다음으로 ML_merge_전국.py를 실행해 ML_전국_농장현황_{윈도우}.csv 4종을 다시 만들어야 한다.")


if __name__ == "__main__":
    main()
