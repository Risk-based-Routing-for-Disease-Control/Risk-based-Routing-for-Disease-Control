"""Final/전국_위험라우팅_타임라인.csv의 reference_date - 15일 ~ reference_date 구간 전체를
커버하도록 weather_daily_raw.csv를 보강한다.

extend_weather_for_routing.py는 reference_date 당일만 커버했다. 이 스크립트는
attach_routing_weather_window.py(직전 15일 long format)가 필요로 하는 더 넓은 날짜 범위를
채운다. 빠진 날짜를 연속 구간으로 묶어 기상청 API Hub(kma_sfcdd3)로 추가 조회하고,
기존 행과 합쳐 다시 저장한다.
"""
import os
import time

import pandas as pd

from fetch_weather import API_FIELD_ORDER, TARGET_COLS, TM_FIELDS, fetch_block, load_api_key

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KMA_DIR = os.path.dirname(os.path.abspath(__file__))
TIMELINE_PATH = os.path.join(ROOT, "Final", "전국_위험라우팅_타임라인.csv")
WEATHER_PATH = os.path.join(KMA_DIR, "weather_daily_raw.csv")

WINDOW_DAYS = 15


def needed_dates():
    ref_dates = pd.to_datetime(
        pd.read_csv(TIMELINE_PATH, usecols=["reference_date"])["reference_date"]
    ).unique()
    dates = set()
    for d in pd.to_datetime(ref_dates):
        for offset in range(WINDOW_DAYS + 1):
            dates.add(d - pd.Timedelta(days=offset))
    return dates


def missing_date_blocks(needed, have_dates):
    missing = sorted(d for d in needed if d not in have_dates)
    blocks = []
    for d in missing:
        if blocks and (d - blocks[-1][1]).days <= 1:
            blocks[-1] = (blocks[-1][0], d)
        else:
            blocks.append((d, d))
    return blocks


def main():
    existing = pd.read_csv(WEATHER_PATH)
    existing["TM"] = pd.to_datetime(existing["TM"])
    have_dates = set(existing["TM"].unique())

    blocks = missing_date_blocks(needed_dates(), have_dates)
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
