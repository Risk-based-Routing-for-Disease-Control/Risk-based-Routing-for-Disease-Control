"""Final/전국_위험라우팅_타임라인.csv의 각 행(농장, 1일)마다 reference_date 기준
직전 15일(reference_date-15 ~ reference_date) 날씨를 long format으로 붙인다.
-> Final/전국_위험라우팅_타임라인_날씨_전15일.csv

농장 좌표 기준 최근접 관측소는 attach_routing_weather.py와 동일한 방식(좌표별 1회 계산)으로 구한다.
타임라인 한 행당 최대 16행(직전 15일 + 당일)으로 늘어나는 long format이다.
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KMA_DIR = os.path.dirname(os.path.abspath(__file__))
TIMELINE_PATH = os.path.join(ROOT, "Final", "전국_위험라우팅_타임라인.csv")
STN_PATH = os.path.join(KMA_DIR, "stn_info.csv")
WEATHER_PATH = os.path.join(KMA_DIR, "weather_daily_raw.csv")
OUT_PATH = os.path.join(ROOT, "Final", "전국_위험라우팅_타임라인_날씨_전15일.csv")

WINDOW_DAYS = 15


def nearest_station(lat, lon, stn):
    lat1 = np.radians(lat.to_numpy())[:, None]
    lon1 = np.radians(lon.to_numpy())[:, None]
    lat2 = np.radians(stn["LAT"].to_numpy())[None, :]
    lon2 = np.radians(stn["LON"].to_numpy())[None, :]

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    dist_km = 2 * 6371 * np.arcsin(np.sqrt(a))

    nearest_idx = dist_km.argmin(axis=1)
    return stn["STN"].to_numpy()[nearest_idx], dist_km[np.arange(len(lat)), nearest_idx]


def main():
    timeline = pd.read_csv(TIMELINE_PATH)
    timeline["reference_date"] = pd.to_datetime(timeline["reference_date"])

    before = len(timeline)
    timeline = timeline.dropna(subset=["latitude", "longitude"]).reset_index(drop=True)
    print(f"좌표 없는 행 {before - len(timeline)}건 제외, {len(timeline)}행 대상")

    timeline = timeline.reset_index().rename(columns={"index": "row_id"})

    stn = pd.read_csv(STN_PATH)
    weather = pd.read_csv(WEATHER_PATH)
    weather["TM"] = pd.to_datetime(weather["TM"])
    weather = weather.drop_duplicates(subset=["STN", "TM"])

    # 같은 (latitude, longitude) 조합마다 최근접 관측소를 한 번씩만 계산한다.
    coords = timeline[["latitude", "longitude"]].drop_duplicates().reset_index(drop=True)
    coords["matched_STN"], coords["matched_dist_km"] = nearest_station(
        coords["latitude"], coords["longitude"], stn
    )
    coords = coords.merge(
        stn.rename(columns={"STN": "matched_STN", "STN_KO": "matched_STN_KO"}),
        on="matched_STN", how="left",
    ).drop(columns=["LAT", "LON"])
    print(f"고유 좌표 {len(coords)}개, 최근접 관측소까지 평균 거리 {coords['matched_dist_km'].mean():.1f}km "
          f"(최대 {coords['matched_dist_km'].max():.1f}km)")

    timeline = timeline.merge(coords, on=["latitude", "longitude"], how="left")

    # 행마다 직전 15일 + 당일(offset 0~-15)을 explode. (STN, TM) 정확 매칭으로 weather와
    # 합치므로 STN 기준 cross join(attach_routing_weather.py식 날짜 필터)보다 메모리 부담이 적다.
    n = len(timeline)
    offsets = np.arange(0, WINDOW_DAYS + 1)
    rep_idx = np.repeat(np.arange(n), len(offsets))
    offset_tile = np.tile(offsets, n)

    long_df = timeline.iloc[rep_idx].reset_index(drop=True)
    long_df["days_from_reference"] = -offset_tile
    long_df["TM"] = long_df["reference_date"] - pd.to_timedelta(offset_tile, unit="D")

    merged = long_df.merge(
        weather, left_on=["matched_STN", "TM"], right_on=["STN", "TM"], how="left", suffixes=("", "_weather")
    )
    merged = merged.drop(columns=["STN"])
    merged = merged.sort_values(["row_id", "TM"]).reset_index(drop=True)

    no_weather_rows = merged.loc[merged["TA_AVG"].isna(), "row_id"].nunique()
    print(f"날씨를 하나도 못 붙인 날짜-행 조합: {merged['TA_AVG'].isna().sum()}건 "
          f"(원본 행 기준 {no_weather_rows}건 일부 영향)")
    print(f"타임라인 {len(timeline)}행 -> 날씨 병합 후 {len(merged)}행 "
          f"(행당 평균 {len(merged) / len(timeline):.1f}행)")

    merged.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print(f"\n저장 완료: {OUT_PATH}")


if __name__ == "__main__":
    main()
