"""ML_농장_토지피복_feature.csv는 ML/ML_전국_농장현황_1year.csv 농장 목록만 커버한다.
Final/전국_위험라우팅_타임라인.csv는 별도 파이프라인(data/{시도}/농장현황/ 원본 + 지오코딩)으로
구축한 농장 유니버스라 두 목록이 다르고, 위험라우팅 쪽에만 있는 농장(5,605건 중 2,276건)은
토지피복 Feature가 없었다. 그 빠진 농장들만 계산해서 같은 ML_농장_토지피복_feature.csv에 이어붙인다.

compute_features.py와 같은 입력(landcover_for_join_{시도}.parquet, landcover_water_wetland_{시도}.parquet)과
같은 알고리즘(농장 하나씩 spatial index로 후보 polygon만 추려 intersection)을 쓴다. 차이는 농장 목록의
출처와, 이미 채워진 시군은 건너뛰는 대신 "이미 있는 farm_id"만 걸러내고 나머지를 전부 처리한다는 점이다
(같은 시군에 토지피복 있는 농장과 없는 농장이 섞여 있을 수 있어서 시군 단위 skip은 쓸 수 없다).

감염날짜: 위험라우팅 타임라인의 같은 farm_id에 label_infected=1인 행이 있으면 그 중 가장 이른
outbreak_date를 쓰고, 한 번도 자가감염되지 않은(이웃으로만 등장한) 농장은 비워둔다
(ML 파이프라인의 "반경 내 가장 가까운 감염일로 대체" 같은 보정은 하지 않음 — 별도 농장 유니버스라
그 보정 로직을 그대로 가져올 근거가 없음).

좌표 단축 경로: 토지피복 Feature는 좌표 기준 3km buffer로만 계산되고 농장명/주소 텍스트와는
무관하다. missing 농장 중 좌표(소수점 6자리)가 ML/ML_전국_농장현황_1year.csv의 이미 계산된
농장과 완전히 같은 경우(같은 농장이 다른 이름/주소 표기로 들어온 경우)는 GIS를 다시 돌리지 않고
그 기존 결과값을 그대로 복사한다. 좌표가 새로운 farm만 GIS로 계산한다.
"""
import hashlib
import os

import geopandas as gpd
import pandas as pd
import shapely
from shapely import wkt
from shapely.errors import GEOSException

EGIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(EGIS_DIR)
TIMELINE_PATH = os.path.join(ROOT, "Final", "전국_위험라우팅_타임라인.csv")
ML_FARM_PATH = os.path.join(ROOT, "ML", "ML_전국_농장현황_1year.csv")
OUT_PATH = os.path.join(EGIS_DIR, "ML_농장_토지피복_feature.csv")

CUSTOM_CRS = "+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=600000 +ellps=GRS80"
RATIO_RADIUS_KM = 3
PROVINCE_ORDER = ["충청북도", "충청남도", "전라북도", "전라남도", "경기도"]
COPIED_COLS = [
    "paddy_area_ratio_3km", "field_area_ratio_3km", "greenhouse_area_ratio_3km",
    "orchard_area_ratio_3km", "forest_area_ratio_3km", "wetland_area_ratio_3km",
    "water_area_ratio_3km", "dist_nearest_water_km",
]

L3_GROUPS = {
    "paddy_area_ratio_3km": ["211", "212"],
    "field_area_ratio_3km": ["221", "222"],
    "greenhouse_area_ratio_3km": ["231"],
    "orchard_area_ratio_3km": ["241"],
    "forest_area_ratio_3km": ["311", "321", "331"],
    "wetland_area_ratio_3km": ["511", "521"],
}
WATER_WETLAND_COMBINED = ["511", "521", "711", "712", "721"]


def make_farm_id(name, addr):
    return hashlib.md5(f"{name}|{addr}".encode("utf-8")).hexdigest()


def load_gdf(path, crs):
    df = pd.read_parquet(path)
    df["geometry"] = df["geometry_wkt"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326").to_crs(crs)
    gdf["geometry"] = shapely.make_valid(gdf.geometry.to_numpy())
    return gdf


def safe_intersection_area(geom, buffer_geom):
    try:
        return geom.intersection(buffer_geom).area
    except GEOSException:
        try:
            return shapely.make_valid(geom).intersection(buffer_geom).area
        except GEOSException:
            return 0.0


def farm_ratios(buffer_geom, buffer_area, lc_gdf, sindex):
    candidates = sindex.query(buffer_geom, predicate="intersects")
    if len(candidates) == 0:
        return {col: 0.0 for col in L3_GROUPS}, 0.0

    sub = lc_gdf.iloc[candidates]
    try:
        areas = sub.geometry.intersection(buffer_geom).area
    except GEOSException:
        areas = pd.Series([safe_intersection_area(g, buffer_geom) for g in sub.geometry], index=sub.index)
    by_code = areas.groupby(sub["L3_CODE"].to_numpy()).sum()

    ratios = {col: sum(by_code.get(c, 0.0) for c in codes) / buffer_area for col, codes in L3_GROUPS.items()}
    water_combined = sum(by_code.get(c, 0.0) for c in WATER_WETLAND_COMBINED) / buffer_area
    return ratios, water_combined


def load_existing_lc():
    if not os.path.exists(OUT_PATH):
        return pd.DataFrame(), set()
    lc = pd.read_csv(OUT_PATH, encoding="utf-8-sig")
    return lc, set(lc["farm_id"])


def load_missing_farms(existing_ids):
    timeline = pd.read_csv(TIMELINE_PATH)
    timeline["farm_id"] = timeline.apply(lambda r: make_farm_id(r["farm_name"], r["farm_address"]), axis=1)

    self_outbreak = (
        timeline[timeline["label_infected"] == 1]
        .groupby("farm_id")["outbreak_date"]
        .min()
    )

    farms = timeline.drop_duplicates(subset=["farm_id"]).set_index("farm_id")
    farms = farms[["city", "county", "farm_name", "farm_address", "latitude", "longitude", "survey_date"]]
    farms["감염날짜"] = self_outbreak

    missing = farms[~farms.index.isin(existing_ids)].reset_index()
    missing = missing.dropna(subset=["latitude", "longitude"]).reset_index(drop=True)
    return missing


def build_coord_lookup(lc, existing_ids):
    """(lat,lon) 6자리 -> 이미 계산된 토지피복 결과. ML 원본 농장 중 이미 lc에 있는 farm_id만 대상."""
    ml = pd.read_csv(ML_FARM_PATH).dropna(subset=["WGS84위도", "WGS84경도"])
    ml["farm_id"] = ml.apply(lambda r: make_farm_id(r["농장명"], r["소재지지번주소"]), axis=1)
    ml = ml[ml["farm_id"].isin(existing_ids)]
    ml["coord_key"] = list(zip(ml["WGS84위도"].round(6), ml["WGS84경도"].round(6)))
    ml = ml.drop_duplicates(subset=["coord_key"])

    merged = ml.merge(lc[["farm_id"] + COPIED_COLS], on="farm_id", how="left")
    return dict(zip(merged["coord_key"], merged[COPIED_COLS].to_dict("records")))


def main():
    lc, existing_ids = load_existing_lc()
    missing = load_missing_farms(existing_ids)
    print(f"토지피복 없는 농장 {len(missing)}건", flush=True)
    if len(missing) == 0:
        return

    coord_lookup = build_coord_lookup(lc, existing_ids)
    missing["coord_key"] = list(zip(missing["latitude"].round(6), missing["longitude"].round(6)))
    is_coord_match = missing["coord_key"].isin(coord_lookup)

    copied = missing[is_coord_match].copy()
    missing = missing[~is_coord_match].drop(columns=["coord_key"]).reset_index(drop=True)
    print(f"  좌표 완전일치(기존 결과 복사): {len(copied)}건, GIS 재계산 필요: {len(missing)}건", flush=True)

    wrote_header = os.path.exists(OUT_PATH)

    if len(copied) > 0:
        rows = []
        for r in copied.itertuples():
            row = {
                "farm_id": r.farm_id,
                "시도명": r.city,
                "시군명": r.county,
                "농장명": r.farm_name,
                "조사날짜": r.survey_date,
                "감염날짜": r.감염날짜,
            }
            row.update(coord_lookup[r.coord_key])
            rows.append(row)
        copied_df = pd.DataFrame(rows)
        copied_df.to_csv(OUT_PATH, mode="a", index=False, header=not wrote_header, encoding="utf-8-sig")
        wrote_header = True
        print(f"  -> {OUT_PATH}에 {len(copied_df)}건 복사 완료", flush=True)

    if len(missing) == 0:
        print(f"\n✓ 전체 저장 완료(좌표 복사만으로 처리됨): {OUT_PATH}")
        return

    missing_gdf = gpd.GeoDataFrame(
        missing, geometry=gpd.points_from_xy(missing["longitude"], missing["latitude"]), crs="EPSG:4326"
    ).to_crs(CUSTOM_CRS)

    for province in PROVINCE_ORDER:
        pf = missing_gdf[missing_gdf["city"] == province].copy()
        if len(pf) == 0:
            continue

        lc_gdf = load_gdf(os.path.join(EGIS_DIR, f"landcover_for_join_{province}.parquet"), CUSTOM_CRS)
        sindex = lc_gdf.sindex
        print(f"{province}: landcover {len(lc_gdf)}개 로드, 농장 {len(pf)}건 처리 시작", flush=True)

        ww_gdf = load_gdf(os.path.join(EGIS_DIR, f"landcover_water_wetland_{province}.parquet"), CUSTOM_CRS)
        nearest = gpd.sjoin_nearest(pf[["farm_id", "geometry"]], ww_gdf[["geometry"]], distance_col="dist_m")
        nearest_km = (nearest.groupby("farm_id")["dist_m"].min() / 1000).to_dict()

        for county in pf["county"].unique():
            sg = pf[pf["county"] == county]
            rows = []
            for farm_row in sg.itertuples():
                buf = farm_row.geometry.buffer(RATIO_RADIUS_KM * 1000)
                ratios, water_combined = farm_ratios(buf, buf.area, lc_gdf, sindex)
                rows.append({
                    "farm_id": farm_row.farm_id,
                    "시도명": province,
                    "시군명": county,
                    "농장명": farm_row.farm_name,
                    "조사날짜": farm_row.survey_date,
                    "감염날짜": farm_row.감염날짜,
                    **ratios,
                    "water_area_ratio_3km": water_combined,
                    "dist_nearest_water_km": nearest_km.get(farm_row.farm_id),
                })

            county_df = pd.DataFrame(rows)
            county_df.to_csv(OUT_PATH, mode="a", index=False, header=not wrote_header, encoding="utf-8-sig")
            wrote_header = True
            print(f"  {province} {county}: {len(county_df)}건 완료 -> {OUT_PATH}에 추가", flush=True)

        print(f"✓ {province}: 농장 {len(pf)}건 처리 완료", flush=True)

    print(f"\n✓ 전체 저장 완료: {OUT_PATH}")


if __name__ == "__main__":
    main()
