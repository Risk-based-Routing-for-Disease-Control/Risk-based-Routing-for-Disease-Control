"""농장별 토지피복 Feature(면적비율, 최단거리)를 여기서 직접 계산해서 최종 테이블로 만든다.

Databricks의 Sedona 공간조인이 계속 에러나서, 정확한 buffer ∩ polygon intersection과
최단거리 계산을 geopandas로 여기서 끝낸다. Databricks는 이 결과를 farm_master에
조인해서 저장만 하면 된다 (GIS 연산 불필요).

입력: landcover_for_join_{시도}.parquet (3km 컷, 면적비율용)
      landcover_water_wetland_{시도}.parquet (거리 제한 없음, 최단거리용)
출력: ML_농장_토지피복_feature.csv
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
FARM_PATH = os.path.join(ROOT, "ML", "ML_전국_농장현황_1year.csv")
OUT_PATH = os.path.join(EGIS_DIR, "ML_농장_토지피복_feature.csv")

# 원본 SHP .prj와 동일한 커스텀 CRS (EPSG:5181과 False_Northing이 다름 — README 참고)
CUSTOM_CRS = "+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=600000 +ellps=GRS80"
RATIO_RADIUS_KM = 3

# 폴리곤 수가 적은 시도부터 처리 (문제 생기면 빨리 알아차리기 위함)
PROVINCE_ORDER = ["충청북도", "충청남도", "전라북도", "전라남도", "경기도"]

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
    # buffer(0)보다 make_valid가 "구멍을 shell에 못 붙이는" 류의 토폴로지 오류를 더 잘 고친다.
    gdf["geometry"] = shapely.make_valid(gdf.geometry.to_numpy())
    return gdf


def safe_intersection_area(geom, buffer_geom):
    """make_valid로도 못 고치는 GEOS 에러는 그 polygon만 건너뛰고 0으로 처리한다."""
    try:
        return geom.intersection(buffer_geom).area
    except GEOSException:
        try:
            return shapely.make_valid(geom).intersection(buffer_geom).area
        except GEOSException:
            return 0.0


def farm_ratios(buffer_geom, buffer_area, lc_gdf, sindex):
    """한 농장의 buffer 하나에 대해서만 후보를 spatial index로 추려서 intersection area를 구한다.

    gpd.overlay로 전체 농장 x 전체 polygon을 한번에 처리하면 농장이 밀집된 지역에서
    교차 조각이 수백만 개로 불어나 메모리가 터진다 — 농장 하나씩 처리해서 후보 폴리곤만
    그때그때 잘라내고 버린다.
    """
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


def main():
    farm = pd.read_csv(FARM_PATH)
    farm = farm.dropna(subset=["WGS84위도", "WGS84경도"]).reset_index(drop=True)
    farm["farm_id"] = farm.apply(lambda r: make_farm_id(r["농장명"], r["소재지지번주소"]), axis=1)

    farm_gdf = gpd.GeoDataFrame(
        farm, geometry=gpd.points_from_xy(farm["WGS84경도"], farm["WGS84위도"]), crs="EPSG:4326"
    ).to_crs(CUSTOM_CRS)

    wrote_header = os.path.exists(OUT_PATH)
    done_sigun = set()
    if wrote_header:
        prev = pd.read_csv(OUT_PATH)
        done_sigun = set(zip(prev["시도명"], prev["시군명"]))
        print(f"이전 실행 결과 발견: {len(prev)}건, 완료된 시군 {len(done_sigun)}개 -> 이어서 처리", flush=True)

    for province in PROVINCE_ORDER:
        pf = farm_gdf[farm_gdf["시도명"] == province].copy()
        if len(pf) == 0:
            continue

        lc_gdf = load_gdf(os.path.join(EGIS_DIR, f"landcover_for_join_{province}.parquet"), CUSTOM_CRS)
        sindex = lc_gdf.sindex
        print(f"{province}: landcover {len(lc_gdf)}개 로드, 농장 {len(pf)}건 처리 시작", flush=True)

        ww_gdf = load_gdf(os.path.join(EGIS_DIR, f"landcover_water_wetland_{province}.parquet"), CUSTOM_CRS)
        nearest = gpd.sjoin_nearest(pf[["farm_id", "geometry"]], ww_gdf[["geometry"]], distance_col="dist_m")
        nearest_km = (nearest.groupby("farm_id")["dist_m"].min() / 1000).to_dict()

        # 시군 단위로 쪼개서 처리 -> 진행 상황을 더 잘게 확인할 수 있고,
        # 시군 끝날 때마다 결과를 바로 csv에 append해서 중간에 죽어도 그동안 처리한 건 남는다.
        for sigun in pf["시군명"].unique():
            if (province, sigun) in done_sigun:
                print(f"  {province} {sigun}: 이미 처리됨, 건너뜀", flush=True)
                continue
            sg = pf[pf["시군명"] == sigun]
            rows = []
            for farm_row in sg.itertuples():
                buf = farm_row.geometry.buffer(RATIO_RADIUS_KM * 1000)
                ratios, water_combined = farm_ratios(buf, buf.area, lc_gdf, sindex)
                rows.append({
                    "farm_id": farm_row.farm_id,
                    "시도명": farm_row.시도명,
                    "시군명": farm_row.시군명,
                    "농장명": farm_row.농장명,
                    "조사날짜": farm_row.조사날짜,
                    **ratios,
                    "water_area_ratio_3km": water_combined,
                    "dist_nearest_water_km": nearest_km.get(farm_row.farm_id),
                })

            sigun_df = pd.DataFrame(rows)
            sigun_df.to_csv(OUT_PATH, mode="a", index=False, header=not wrote_header, encoding="utf-8-sig")
            wrote_header = True
            print(f"  {province} {sigun}: {len(sigun_df)}건 완료 -> {OUT_PATH}에 저장", flush=True)

        print(f"✓ {province}: 농장 {len(pf)}건 처리 완료", flush=True)

    print(f"\n✓ 전체 저장 완료: {OUT_PATH}")


if __name__ == "__main__":
    main()
