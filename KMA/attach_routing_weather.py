"""Final/전국_위험라우팅_타임라인.csv의 각 행(농장, 1일)에 그 날짜의 날씨를 붙인다.

다른 KMA 스크립트(match_farm_weather.py 등)는 농장 1건당 여러 날(윈도우)을 만들어 붙이지만,
위험라우팅 타임라인은 이미 농장×날짜 long format이므로 행마다 그 날짜(reference_date) 날씨
하나만 그대로 붙이면 된다. 농장 좌표 기준 최근접 관측소를 구해 매칭한다.
-> Final/전국_위험라우팅_타임라인_날씨.csv
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KMA_DIR = os.path.dirname(os.path.abspath(__file__))
TIMELINE_PATH = os.path.join(ROOT, "Final", "전국_위험라우팅_타임라인.csv")
STN_PATH = os.path.join(KMA_DIR, "stn_info.csv")
WEATHER_PATH = os.path.join(KMA_DIR, "weather_daily_raw.csv")
OUT_PATH = os.path.join(ROOT, "Final", "전국_위험라우팅_타임라인_날씨.csv")


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

    stn = pd.read_csv(STN_PATH)
    weather = pd.read_csv(WEATHER_PATH)
    weather["TM"] = pd.to_datetime(weather["TM"])
    weather = weather.drop_duplicates(subset=["STN", "TM"])

    # 같은 (latitude, longitude) 조합마다 최근접 관측소를 한 번씩만 계산한다 (행 수보다 좌표 종류가 훨씬 적음).
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

    merged = timeline.merge(
        weather, left_on=["matched_STN", "reference_date"], right_on=["STN", "TM"], how="left"
    ).drop(columns=["STN", "TM"])

    no_weather = merged["TA_AVG"].isna().sum()
    print(f"날씨 못 붙인 행: {no_weather}건 (관측소 매칭은 됐지만 그 날짜 데이터가 없는 경우)")

    merged.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print(f"\n저장 완료: {OUT_PATH} ({len(merged)}행)")


if __name__ == "__main__":
    main()
