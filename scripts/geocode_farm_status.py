"""ML/ML_*_농장현황.csv 의 WGS84위도/경도 결측치를 소재지지번주소 기준으로 채우고,
기존 좌표 중 위경도가 뒤바뀐 행(위도 컬럼에 경도값이 들어간 경우)을 정정한다.
"""
import os
import glob

import pandas as pd

import geocode_lib as gl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ML_DIR = os.path.join(ROOT, "ML")
LAT_COL = "WGS84위도"
LON_COL = "WGS84경도"
ADDR_COL = "소재지지번주소"

# 한국 영토의 대략적인 위경도 범위
LAT_RANGE = (30, 45)
LON_RANGE = (120, 135)


def fix_swapped(df):
    have = df[LAT_COL].notna() & df[LON_COL].notna()
    swapped = (
        have
        & df[LAT_COL].between(*LON_RANGE)
        & df[LON_COL].between(*LAT_RANGE)
    )
    n = swapped.sum()
    if n:
        df.loc[swapped, [LAT_COL, LON_COL]] = df.loc[
            swapped, [LON_COL, LAT_COL]
        ].values
    return n


def process_file(path, api_key, cache):
    df = pd.read_csv(path)
    n_swapped = fix_swapped(df)

    missing_mask = df[LAT_COL].isna() | df[LON_COL].isna()
    addresses = df.loc[missing_mask, ADDR_COL].dropna().unique().tolist()
    print(f"\n=== {os.path.basename(path)} ===")
    print(f"swapped fixed: {n_swapped}, missing rows: {missing_mask.sum()}, unique addresses: {len(addresses)}")

    failed = gl.geocode_addresses(addresses, api_key, cache)
    print(f"geocoded: {len(addresses) - len(failed)}, failed: {len(failed)}")
    for a in failed:
        print("  FAILED:", a)

    if "coord_precision" not in df.columns:
        df["coord_precision"] = "exact"

    filled = 0
    for idx in df.index[missing_mask]:
        addr = df.at[idx, ADDR_COL]
        entry = cache.get(addr) if pd.notna(addr) else None
        if entry and entry["lat"] is not None:
            df.at[idx, LAT_COL] = entry["lat"]
            df.at[idx, LON_COL] = entry["lon"]
            df.at[idx, "coord_precision"] = "approx_" + entry["source"]
            filled += 1

    print(f"filled {filled} / {missing_mask.sum()} rows")
    df.to_csv(path, index=False)
    return n_swapped, filled, missing_mask.sum() - filled


def main():
    api_key = gl.load_api_key()
    cache = gl.load_cache()

    files = sorted(glob.glob(os.path.join(ML_DIR, "ML_*_농장현황.csv")))
    totals = {"swapped": 0, "filled": 0, "still_missing": 0}
    for path in files:
        n_swapped, filled, still_missing = process_file(path, api_key, cache)
        totals["swapped"] += n_swapped
        totals["filled"] += filled
        totals["still_missing"] += still_missing

    print("\n=== TOTAL ===")
    print(totals)


if __name__ == "__main__":
    main()
