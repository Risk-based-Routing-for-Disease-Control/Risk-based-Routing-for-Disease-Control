"""농장(ML_전국_농장현황_1year_alldates.csv)마다 가장 가까운 관측소를 찾아
조사날짜-7일~조사날짜 구간의 일별 날씨를 그대로 붙인다 -> KMA/ML_농장_날씨.csv

농장 좌표 기준 최근접 관측소를 구한 뒤 그 관측소의 날씨를 매칭하므로,
조사날짜가 같아도 농장 위치(=최근접 관측소)가 다르면 서로 다른 날씨 시계열이 붙는다.
결과는 농장 1건당 최대 8일치(최근 7일 + 조사날짜 당일) 행으로 늘어나는 long format이다.
당일 행은 습도(HM_AVG/HM_MIN)를 그날 값으로 쓰기 위해 남겨둔다.

입력을 alldates 버전으로 쓰는 이유: 비-alldates 버전(ML_전국_농장현황_1year.csv)은
같은 시군에서 발생일(occr_date)이 여러 번이면 그 발생일 윈도우마다 독립적으로 감염날짜를
채우는데, 같은 농장·조사날짜가 두 윈도우에 동시에 걸리면 감염날짜가 윈도우별로 달라질 수
있다 (ML/README.md 3번 항목 참고). alldates는 이 후보들을 모두 보존해서 만든 결과이므로,
같은 시군명·농장명·소재지지번주소·조사날짜라도 감염날짜가 다른 행은 별도 행(farm_id)으로
취급해 그대로 둔다 (중복 제거하지 않음).
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KMA_DIR = os.path.dirname(os.path.abspath(__file__))
FARM_PATH = os.path.join(ROOT, "ML", "ML_전국_농장현황_1year_alldates.csv")
STN_PATH = os.path.join(KMA_DIR, "stn_info.csv")
WEATHER_PATH = os.path.join(KMA_DIR, "weather_daily_raw.csv")
OUT_PATH = os.path.join(KMA_DIR, "ML_농장_날씨.csv")

WINDOW_DAYS = 7


def nearest_station(farm_lat, farm_lon, stn):
    """농장 좌표마다 하버사인 거리 기준 최근접 관측소의 (STN, 거리km) 배열을 반환."""
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
    farm["감염날짜"] = pd.to_datetime(farm["감염날짜"])
    farm = farm.dropna(subset=["WGS84위도", "WGS84경도"]).reset_index(drop=True)

    stn = pd.read_csv(STN_PATH)
    
    weather = pd.read_csv(WEATHER_PATH)
    weather["TM"] = pd.to_datetime(weather["TM"])
    weather = weather.drop_duplicates(subset=["STN", "TM"])


    farm["matched_STN"], farm["matched_dist_km"] = nearest_station(
        farm["WGS84위도"], farm["WGS84경도"], stn
    )
    farm = farm.merge(stn.rename(columns={"STN": "matched_STN", "STN_KO": "matched_STN_KO"}),
                       on="matched_STN", how="left").drop(columns=["LAT", "LON"])
    farm["window_start"] = (farm["감염날짜"] - pd.Timedelta(days=WINDOW_DAYS))
    farm = farm.reset_index().rename(columns={"index": "farm_id"})


    print(f"농장 {len(farm)}건, 최근접 관측소까지 평균 거리 {farm['matched_dist_km'].mean():.1f}km "
          f"(최대 {farm['matched_dist_km'].max():.1f}km)")

    # farm["window_start"] = farm["감염날짜"] - pd.Timedelta(days=WINDOW_DAYS)
    # farm = farm.reset_index().rename(columns={"index": "farm_id"})

    merged = farm.merge(
        weather, left_on="matched_STN", right_on="STN", how="left", suffixes=("", "_weather")
    )
    merged["TM"] = pd.to_datetime(merged["TM"])
    merged = merged[(merged["TM"] >= merged["window_start"]) & 
                    (merged["TM"] <= merged["감염날짜"])]
    merged = merged.drop(columns=["STN", "window_start"])

    print(f"농장 {len(farm)}건 -> 날씨 병합 후 {len(merged)}행 "
          f"(농장당 평균 {len(merged) / len(farm):.1f}행)")

    merged.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print(f"\n✓ 저장 완료: {OUT_PATH}")


if __name__ == "__main__":
    main()
