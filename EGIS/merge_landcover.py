"""EGIS/raw/{도엽번호}/*.shp (토지피복지도, 도엽 단위 배포)를 모두 읽어 하나로 합치고,
농장(ML_전국_농장현황_1year.csv) 좌표 기준 RADIUS_KM 이내의 polygon만 남긴다.

도엽 단위로 내려받은 SHP 세트(SHP/DBF/SHX/PRJ/XML)를 raw/{도엽번호}/ 에 풀어두면
이 스크립트가 raw/ 아래를 재귀적으로 찾아서 전부 합친다. 시/도 전체를 다 합치면
용량이 수 GB라, 실제로 농장 근처에서 안 쓰이는 polygon은 내보내기 전에 미리 잘라낸다.
반경 N km 비율·최단거리 계산(buffer ∩ polygon 등 실제 공간조인)은 Databricks에서 한다.

- landcover_merged.gpkg                  로컬 QGIS 확인용 (필터링 후, 전체 시도 한 파일)
- landcover_for_join_{시도}.parquet       Databricks Volume 업로드용, 시도별로 분리 (geometry -> WKT 문자열)
"""
import glob
import os
import unicodedata

import geopandas as gpd
import pandas as pd

EGIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(EGIS_DIR)
RAW_DIR = os.path.join(EGIS_DIR, "raw")
GPKG_OUT_PATH = os.path.join(EGIS_DIR, "landcover_merged.gpkg")
PARQUET_OUT_TEMPLATE = os.path.join(EGIS_DIR, "landcover_for_join_{}.parquet")
FARM_PATH = os.path.join(ROOT, "ML", "ML_전국_농장현황_1year.csv")

KEEP_COLS = ["L1_CODE", "L1_NAME", "L2_CODE", "L2_NAME", "L3_CODE", "L3_NAME", "INX_NUM", "geometry"]

# DBF가 cp949로 인코딩돼 있는데 .cpg 힌트 파일이 없어서, 명시하지 않으면 한글 컬럼이 깨진다.
DBF_ENCODING = "cp949"

# 농장 근처 몇 km까지 토지피복을 남길지. Databricks에서 쓸 반경(3km 비율, 5km 거리 등)보다
# 넉넉하게 잡아야 경계 근처 농장이 잘려나가지 않는다.
RADIUS_KM = 3


def province_from_path(path):
    """raw/{시도}_토지피복지도/{도엽}/{도엽}.shp 경로에서 시도명을 뽑아낸다.

    macOS는 한글 폴더명을 NFD(분해형)로 저장하는데 이 파일의 문자열 리터럴은
    NFC(결합형)라서, 정규화 없이 .replace()를 하면 매칭이 안 된다.
    """
    rel = os.path.relpath(path, RAW_DIR)
    top = unicodedata.normalize("NFC", rel.split(os.sep)[0])
    return top.replace("_토지피복지도", "")


def load_farm_buffers(target_crs):
    """농장 좌표를 target_crs로 투영하고 RADIUS_KM buffer를 씌운 GeoDataFrame을 반환한다."""
    farm = pd.read_csv(FARM_PATH)
    farm = farm.dropna(subset=["WGS84위도", "WGS84경도"])
    farm_gdf = gpd.GeoDataFrame(
        farm,
        geometry=gpd.points_from_xy(farm["WGS84경도"], farm["WGS84위도"]),
        crs="EPSG:4326",
    ).to_crs(target_crs)
    farm_gdf["geometry"] = farm_gdf.geometry.buffer(RADIUS_KM * 1000)
    return farm_gdf[["geometry"]]


def main():
    shp_paths = sorted(glob.glob(os.path.join(RAW_DIR, "**", "*.shp"), recursive=True))
    if not shp_paths:
        raise FileNotFoundError(
            f"{RAW_DIR} 아래에 SHP가 없다. 도엽 단위로 받은 SHP 세트를 raw/{{도엽번호}}/ 에 넣어야 한다."
        )

    sample = gpd.read_file(shp_paths[0], encoding=DBF_ENCODING)
    buffers = load_farm_buffers(sample.crs)

    # 도엽 6천여 개를 다 합친 뒤에 필터링하면 폴리곤이 수백만~천만 개로 쌓여 메모리가 터진다.
    # 도엽 하나씩 읽어서 그 자리에서 필터링하고, 살아남은 것만 누적한다.
    kept = []
    total_polygons = 0
    for i, path in enumerate(shp_paths, 1):
        gdf = gpd.read_file(path, encoding=DBF_ENCODING)
        gdf = gdf[[c for c in KEEP_COLS if c in gdf.columns]]
        gdf["시도"] = province_from_path(path)
        total_polygons += len(gdf)

        hit_idx = gpd.sjoin(gdf, buffers, how="inner", predicate="intersects").index.unique()
        if len(hit_idx):
            kept.append(gdf.loc[hit_idx])

        if i % 200 == 0 or i == len(shp_paths):
            n_kept = sum(len(k) for k in kept)
            print(f"  {i}/{len(shp_paths)} 도엽 처리, 원본 polygon {total_polygons}개 중 {n_kept}개 통과")

    filtered = gpd.GeoDataFrame(pd.concat(kept, ignore_index=True), geometry="geometry", crs=sample.crs)
    print(f"도엽 {len(shp_paths)}개, 원본 polygon {total_polygons}개 -> 농장 {RADIUS_KM}km 이내 {len(filtered)}개로 필터링")

    filtered_wgs84 = filtered.to_crs("EPSG:4326")

    filtered_wgs84.to_file(GPKG_OUT_PATH, driver="GPKG")
    print(f"✓ 저장 완료(로컬 확인용, EPSG:4326): {GPKG_OUT_PATH}")

    for province, sub in filtered_wgs84.groupby("시도"):
        for_join = pd.DataFrame(sub.drop(columns="geometry"))
        for_join["geometry_wkt"] = sub.geometry.to_wkt()
        out_path = PARQUET_OUT_TEMPLATE.format(province)
        for_join.to_parquet(out_path, index=False)
        print(f"✓ {province}: {len(for_join)}개 polygon -> {out_path}")


if __name__ == "__main__":
    main()
