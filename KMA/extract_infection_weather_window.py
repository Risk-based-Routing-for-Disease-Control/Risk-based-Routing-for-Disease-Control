"""전국_최종감염농장.csv 기준으로 감염날짜 전 14일 날씨를 weather_daily_raw.csv에서 추출.

각 감염농장마다 하버사인 거리 기준 최근접 관측소를 찾고,
outbreak_date - 14일 ~ outbreak_date (총 최대 15일) 날씨를 붙여 long format으로 저장.
"""

import os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KMA_DIR = os.path.dirname(os.path.abspath(__file__))

FARM_PATH = os.path.join(ROOT, "최종감염농장", "전국_최종감염농장.csv")
STN_PATH = os.path.join(KMA_DIR, "stn_info.csv")
WEATHER_PATH = os.path.join(KMA_DIR, "weather_daily_raw.csv")
OUT_PATH = os.path.join(KMA_DIR, "감염농장_전14일_날씨.csv")

WINDOW_DAYS = 14


def nearest_station(farm_lat, farm_lon, stn):
    lat1 = np.radians(farm_lat.to_numpy())[:, None]
    lon1 = np.radians(farm_lon.to_numpy())[:, None]
    lat2 = np.radians(stn["LAT"].to_numpy())[None, :]
    lon2 = np.radians(stn["LON"].to_numpy())[None, :]

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    dist_km = 2 * 6371 * np.arcsin(np.sqrt(a))

    nearest_idx = dist_km.argmin(axis=1)
    return stn["STN"].to_numpy()[nearest_idx], dist_km[np.arange(len(farm_lat)), nearest_idx]


def main():
    farm = pd.read_csv(FARM_PATH)
    farm["outbreak_date"] = pd.to_datetime(farm["outbreak_date"], format="%Y%m%d")
    farm = farm.dropna(subset=["latitude", "longitude"]).reset_index(drop=True)

    stn = pd.read_csv(STN_PATH)

    weather = pd.read_csv(WEATHER_PATH)
    weather["TM"] = pd.to_datetime(weather["TM"])
    weather = weather.drop_duplicates(subset=["STN", "TM"])

    farm["matched_STN"], farm["matched_dist_km"] = nearest_station(
        farm["latitude"], farm["longitude"], stn
    )
    farm = farm.merge(
        stn.rename(columns={"STN": "matched_STN", "STN_KO": "matched_STN_KO"}),
        on="matched_STN", how="left"
    ).drop(columns=["LAT", "LON"])

    farm["window_start"] = farm["outbreak_date"] - pd.Timedelta(days=WINDOW_DAYS)
    farm = farm.reset_index().rename(columns={"index": "farm_id"})

    print(f"감염농장 {len(farm)}건, 최근접 관측소까지 평균 거리 {farm['matched_dist_km'].mean():.1f}km "
          f"(최대 {farm['matched_dist_km'].max():.1f}km)")

    merged = farm.merge(
        weather, left_on="matched_STN", right_on="STN", how="left", suffixes=("", "_weather")
    )
    merged["TM"] = pd.to_datetime(merged["TM"])
    merged = merged[
        (merged["TM"] >= merged["window_start"]) &
        (merged["TM"] <= merged["outbreak_date"])
    ]

    # 감염날짜 기준 상대적 날짜 offset 추가 (음수=이전, 0=감염날)
    merged["days_from_outbreak"] = (merged["TM"] - merged["outbreak_date"]).dt.days

    merged = merged.drop(columns=["STN", "window_start"])
    merged = merged.sort_values(["farm_id", "TM"]).reset_index(drop=True)

    print(f"감염농장 {len(farm)}건 -> 날씨 병합 후 {len(merged)}행 "
          f"(농장당 평균 {len(merged) / len(farm):.1f}행)")

    merged.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print(f"\n저장 완료: {OUT_PATH}")


if __name__ == "__main__":
    main()
