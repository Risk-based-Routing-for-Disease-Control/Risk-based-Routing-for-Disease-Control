"""data/{시도}/농장현황/*.csv 원본 파일들을 병합해 data/전국_농장현황.csv를 만든다.

- 컬럼을 시도명,시군명,농장명,축종명,상세구분,사육두수(마리),소재지지번주소,WGS84위도,WGS84경도,조사날짜 로 통일
  (시도명은 파일이 위치한 상위 폴더명에서 가져옴)
- 위도/경도 컬럼이 뒤바뀐 행을 정정
- 위 10개 컬럼 기준 완전 중복 행 제거
- 위경도 결측 행은 소재지지번주소 기준으로 Kakao 지오코딩 API(캐시 사용)로 채움
"""
import glob
import os

import pandas as pd

import geocode_lib as gl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
OUT_PATH = os.path.join(DATA_DIR, "전국_농장현황.csv")

STANDARD_COLS = [
    "시군명", "농장명", "축종명", "상세구분", "사육두수(마리)",
    "소재지지번주소", "WGS84위도", "WGS84경도", "조사날짜",
]
ALL_COLS = ["시도명"] + STANDARD_COLS
LAT_COL, LON_COL, ADDR_COL = "WGS84위도", "WGS84경도", "소재지지번주소"

# 한국 영토의 대략적인 위경도 범위
LAT_RANGE = (30, 45)
LON_RANGE = (120, 135)


def fix_swapped(df):
    have = df[LAT_COL].notna() & df[LON_COL].notna()
    swapped = have & df[LAT_COL].between(*LON_RANGE) & df[LON_COL].between(*LAT_RANGE)
    n = swapped.sum()
    if n:
        df.loc[swapped, [LAT_COL, LON_COL]] = df.loc[swapped, [LON_COL, LAT_COL]].values
    return n


def main():
    files = sorted(glob.glob(os.path.join(DATA_DIR, "*", "농장현황", "*.csv")))
    print(f"대상 파일 {len(files)}개")

    frames = []
    total_swapped = 0
    for path in files:
        province = os.path.basename(os.path.dirname(os.path.dirname(path)))
        df = pd.read_csv(path, encoding="utf-8-sig")
        df = df[STANDARD_COLS]
        df = df.dropna(subset=["농장명"])
        total_swapped += fix_swapped(df)
        df.insert(0, "시도명", province)
        frames.append(df)

    merged = pd.concat(frames, ignore_index=True)
    before = len(merged)
    merged = merged.drop_duplicates(subset=ALL_COLS).reset_index(drop=True)
    print(f"병합 {before}건 -> 중복 제거 후 {len(merged)}건 (swapped 정정 {total_swapped}건)")

    api_key = gl.load_api_key()
    cache = gl.load_cache()

    missing_mask = merged[LAT_COL].isna() | merged[LON_COL].isna()
    addresses = merged.loc[missing_mask, ADDR_COL].dropna().unique().tolist()
    print(f"결측 {missing_mask.sum()}건, 고유 주소 {len(addresses)}개 지오코딩 시도")

    failed = gl.geocode_addresses(addresses, api_key, cache)
    print(f"지오코딩 성공 {len(addresses) - len(failed)}, 실패 {len(failed)}")
    for a in failed:
        print("  FAILED:", a)

    filled = 0
    for idx in merged.index[missing_mask]:
        addr = merged.at[idx, ADDR_COL]
        entry = cache.get(addr) if pd.notna(addr) else None
        if entry and entry["lat"] is not None:
            merged.at[idx, LAT_COL] = entry["lat"]
            merged.at[idx, LON_COL] = entry["lon"]
            filled += 1

    still_missing = merged[LAT_COL].isna().sum()
    print(f"좌표 채움 {filled}건, 여전히 결측 {still_missing}건")

    merged.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print(f"\n✓ 저장 완료: {OUT_PATH} ({len(merged)}건)")


if __name__ == "__main__":
    main()
