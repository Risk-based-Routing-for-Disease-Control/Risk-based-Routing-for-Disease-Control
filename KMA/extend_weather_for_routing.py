"""Final/전국_위험라우팅_타임라인.csv의 reference_date 전체를 커버하도록 weather_daily_raw.csv를 보강한다.

기존 weather_daily_raw.csv는 ML 농장현황의 조사날짜 기준 30일 윈도우만 모아둔 것이라
위험라우팅 타임라인이 필요로 하는 날짜(출현일 -7~+7) 중 상당수가 빠져 있다. 빠진 날짜를
연속 구간으로 묶어 기상청 API Hub(kma_sfcdd3)로 추가 조회하고, 기존 행과 합쳐 다시 저장한다.
"""
import os
import time

import pandas as pd

from fetch_weather import API_FIELD_ORDER, TARGET_COLS, TM_FIELDS, fetch_block, load_api_key

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KMA_DIR = os.path.dirname(os.path.abspath(__file__))
TIMELINE_PATH = os.path.join(ROOT, "Final", "전국_위험라우팅_타임라인.csv")
WEATHER_PATH = os.path.join(KMA_DIR, "weather_daily_raw.csv")


def missing_date_blocks(needed_dates, have_dates):
    missing = sorted(d for d in needed_dates if d not in have_dates)
    blocks = []
    for d in missing:
        if blocks and (d - blocks[-1][1]).days <= 1:
            blocks[-1] = (blocks[-1][0], d)
        else:
            blocks.append((d, d))
    return blocks


def main():
    timeline_dates = pd.to_datetime(
        pd.read_csv(TIMELINE_PATH, usecols=["reference_date"])["reference_date"]
    ).unique()
    existing = pd.read_csv(WEATHER_PATH)
    existing["TM"] = pd.to_datetime(existing["TM"])
    have_dates = set(existing["TM"].unique())

    blocks = missing_date_blocks(timeline_dates, have_dates)
    print(f"{len(blocks)}개 날짜 구간 보강 (총 {sum((e - s).days + 1 for s, e in blocks)}일)")

    api_key = load_api_key()
    parts = []
    for start, end in blocks:
        print(f"  fetching {start.date()} ~ {end.date()}")
        parts.append(fetch_block(start, end, api_key))
        time.sleep(0.2)

    new_df = pd.concat(parts, ignore_index=True)
    cols = [c for c in TARGET_COLS if c in new_df.columns]
    new_df = new_df[cols]
    new_df["TM"] = pd.to_datetime(new_df["TM"], format="%Y%m%d").dt.strftime("%Y-%m-%d")
    new_df["STN"] = new_df["STN"].astype(int)

    for c in cols:
        if c in ("TM", "STN") or c in TM_FIELDS:
            new_df[c] = new_df[c].replace("-9", pd.NA)
            continue
        new_df[c] = pd.to_numeric(new_df[c], errors="coerce")
        new_df.loc[new_df[c].isin([-9, -99, -999]), c] = pd.NA

    existing["TM"] = existing["TM"].dt.strftime("%Y-%m-%d")
    existing = existing.drop(columns=["weather_daily_id"])
    merged = pd.concat([existing, new_df], ignore_index=True)
    merged = merged.drop_duplicates(subset=["TM", "STN"]).sort_values(["TM", "STN"]).reset_index(drop=True)
    merged.insert(0, "weather_daily_id", range(1, len(merged) + 1))

    merged.to_csv(WEATHER_PATH, index=False)
    print(f"\n저장 완료: {WEATHER_PATH} ({len(merged)}행, 신규 {len(new_df)}행 조회)")


if __name__ == "__main__":
    main()
