"""안성시 농장현황에서 지정한 기준일(2025-12-10, 2025-12-16)마다 농장별로 가장 가까운
조사날짜 기록을 골라 Final/전국_위험라우팅_타임라인.csv(merge_risk_routing_timeline.py 산출물)와
같은 컬럼 스키마(city, county, farm_name, ..., label_infected)에 farm_id와 날씨 feature
(humidity, min_temp_7d, precipitation_7d, wind_speed_avg_7d)를 붙여, 기준일별로 파일을 나눠 저장한다.

- farm_id: 02_silver_clean_farm_master.ipynb와 동일하게 md5(farm_name|farm_address).
- humidity: 기준일 당일 최근접 관측소의 HM_AVG.
- min_temp_7d/precipitation_7d/wind_speed_avg_7d: 03_gold_create_weather_features.ipynb와 동일하게
  [기준일-7, 기준일) 구간(기준일 당일 미포함, 즉 12/10이면 12/3~12/9)의 TA_MIN 최솟값 / RN_DAY 합계
  (전부 NULL이면 NULL, 아니면 NULL=0 취급) / WS_AVG 평균.

감염 이벤트가 없는 순수 census 스냅샷이라 label_infected=0, outbreak_date=NaT로 고정하고,
build_risk_routing_timeline.py의 '자가감염 농장은 발생일에 가까운 기록/그 외는 최신 기록' 룰은
적용하지 않는다 (기준일에 가장 가까운 기록만 쓴다).
"""
import hashlib
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import geocode_lib as gl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CENSUS_PATH = os.path.join(ROOT, "data", "경기도", "농장현황", "안성시_농장현황.csv")
LIVESTOCK_CODES_PATH = os.path.join(ROOT, "livestock_codes.csv")
STN_PATH = os.path.join(ROOT, "KMA", "stn_info.csv")
WEATHER_PATH = os.path.join(ROOT, "KMA", "weather_daily_raw.csv")

TARGET_DATES = [pd.Timestamp("2025-12-10"), pd.Timestamp("2025-12-16")]
FARM_KEY_COLS = ["농장명", "소재지지번주소"]
WEATHER_WINDOW_DAYS = 7

FINAL_COLS = [
    "farm_id", "city", "county", "farm_name", "farm_address", "latitude", "longitude",
    "livestock_name", "livestock_type", "head_count", "survey_date",
    "reference_date", "outbreak_date", "label_infected",
    "humidity", "min_temp_7d", "precipitation_7d", "wind_speed_avg_7d",
]


def county_from_address(addr_series):
    return addr_series.astype(str).str.split().str[1]


def load_detail_to_name_map():
    codes = pd.read_csv(LIVESTOCK_CODES_PATH)
    grouped = codes.groupby("상세구분")["축종명"].unique()
    return {detail: names[0] for detail, names in grouped.items() if len(names) == 1}


def load_census():
    census = pd.read_csv(CENSUS_PATH, encoding="utf-8-sig")
    census.columns = [c.strip() for c in census.columns]

    lat = pd.to_numeric(census["WGS84위도"], errors="coerce")
    lon = pd.to_numeric(census["WGS84경도"], errors="coerce")
    swapped = lat > 90
    census["lat"] = lat.where(~swapped, lon)
    census["lon"] = lon.where(~swapped, lat)
    census["census_native_coord"] = census["lat"].notna()

    missing_coord = ~census["census_native_coord"]
    if missing_coord.any():
        api_key = gl.load_api_key()
        cache = gl.load_cache()
        unique_addrs = sorted(census.loc[missing_coord, "소재지지번주소"].dropna().unique().tolist())
        gl.geocode_addresses(unique_addrs, api_key, cache)
        census.loc[missing_coord, "lat"] = census.loc[missing_coord, "소재지지번주소"].map(
            lambda a: cache.get(a, {}).get("lat")
        )
        census.loc[missing_coord, "lon"] = census.loc[missing_coord, "소재지지번주소"].map(
            lambda a: cache.get(a, {}).get("lon")
        )

    census["farm_county"] = county_from_address(census["소재지지번주소"])
    census = census[census["farm_county"] == "안성시"].reset_index(drop=True)
    census["조사날짜_dt"] = pd.to_datetime(census["조사날짜"], errors="coerce")
    census["has_coord"] = census["lat"].notna()
    return census


def nearest_per_farm(census, target_date):
    """농장별로 target_date에 가장 가까운 조사날짜 기록 하나를 고른다."""
    df = census.copy()
    df["_dist"] = (df["조사날짜_dt"] - target_date).abs()
    df = df.sort_values(["has_coord", "_dist"], ascending=[False, True])
    picked = df.drop_duplicates(subset=FARM_KEY_COLS, keep="first")

    out = pd.DataFrame(
        {
            "city": "경기도",
            "county": picked["farm_county"],
            "farm_name": picked["농장명"],
            "farm_address": picked["소재지지번주소"],
            "latitude": picked["lat"],
            "longitude": picked["lon"],
            "livestock_name": picked["축종명"],
            "livestock_type": picked["상세구분"],
            "head_count": picked["사육두수(마리)"],
            "survey_date": picked["조사날짜"],
            "reference_date": target_date.strftime("%Y-%m-%d"),
            "outbreak_date": pd.NaT,
            "label_infected": 0,
        }
    )

    detail_to_name = load_detail_to_name_map()
    missing_name = out["livestock_name"].isna() & out["livestock_type"].notna()
    out.loc[missing_name, "livestock_name"] = out.loc[missing_name, "livestock_type"].map(detail_to_name)

    valid_names = set(pd.read_csv(LIVESTOCK_CODES_PATH)["축종명"].unique())
    still_missing = out["livestock_name"].isna() & out["livestock_type"].isin(valid_names)
    out.loc[still_missing, "livestock_name"] = out.loc[still_missing, "livestock_type"]

    out["farm_id"] = (out["farm_name"] + "|" + out["farm_address"]).map(
        lambda s: hashlib.md5(s.encode("utf-8")).hexdigest()
    )

    return out.reset_index(drop=True)


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
    return stn["STN"].to_numpy()[nearest_idx]


def attach_weather(farms, target_date, weather, stn):
    """farms(농장 1행씩)에 target_date 기준 humidity(당일)와 7일(직전, 당일 미포함) feature를 붙인다."""
    coords = farms[["latitude", "longitude"]].drop_duplicates().reset_index(drop=True)
    coords["matched_STN"] = nearest_station(coords["latitude"], coords["longitude"], stn)
    farms = farms.merge(coords, on=["latitude", "longitude"], how="left")

    humidity_day = weather[weather["TM"] == target_date][["STN", "HM_AVG"]].rename(
        columns={"HM_AVG": "humidity"}
    )

    window_start = target_date - pd.Timedelta(days=WEATHER_WINDOW_DAYS)
    window = weather[(weather["TM"] >= window_start) & (weather["TM"] < target_date)]
    agg_7d = window.groupby("STN").agg(
        min_temp_7d=("TA_MIN", "min"),
        wind_speed_avg_7d=("WS_AVG", "mean"),
        _rn_count=("RN_DAY", "count"),
        _rn_sum=("RN_DAY", lambda s: s.fillna(0).sum()),
    ).reset_index()
    agg_7d["precipitation_7d"] = agg_7d["_rn_sum"].where(agg_7d["_rn_count"] > 0)
    agg_7d = agg_7d.drop(columns=["_rn_count", "_rn_sum"])

    farms = farms.merge(humidity_day, left_on="matched_STN", right_on="STN", how="left").drop(columns=["STN"])
    farms = farms.merge(agg_7d, left_on="matched_STN", right_on="STN", how="left").drop(columns=["STN", "matched_STN"])
    return farms


def main():
    census = load_census()
    print(f"안성시 census 원본: {len(census)}행, 좌표 결측: {(~census['has_coord']).sum()}행")

    stn = pd.read_csv(STN_PATH)
    weather = pd.read_csv(WEATHER_PATH)
    weather["TM"] = pd.to_datetime(weather["TM"])
    weather = weather.drop_duplicates(subset=["STN", "TM"])

    for target_date in TARGET_DATES:
        farms = nearest_per_farm(census, target_date)
        farms = farms[farms["latitude"].notna() & farms["longitude"].notna()].reset_index(drop=True)
        farms = attach_weather(farms, target_date, weather, stn)
        farms = farms[FINAL_COLS]
        farms = farms.sort_values(["farm_name", "farm_address"]).reset_index(drop=True)

        out_path = os.path.join(ROOT, "Final", f"안성시_농장현황_{target_date.strftime('%Y-%m-%d')}.csv")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        farms.to_csv(out_path, index=False, encoding="utf-8-sig")

        print(f"{target_date.strftime('%Y-%m-%d')}: 농장 {len(farms)}개, "
              f"humidity 결측 {farms['humidity'].isna().sum()}건, "
              f"min_temp_7d 결측 {farms['min_temp_7d'].isna().sum()}건")
        print(f"  저장 위치: {out_path}")


if __name__ == "__main__":
    main()
