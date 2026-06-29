"""EGIS/raw/{도엽번호}/*.shp 에서 수역·습지(L3_CODE 511/521/711/712/721)만 거리 제한 없이 모두 모은다.

merge_landcover.py의 농장 3km 필터는 면적비율(paddy_area_ratio_3km 등)엔 정확히 맞지만,
반경 제한이 없는 dist_nearest_water(최단거리)에는 부족하다 — 농장 근처 3km 안에
수역·습지가 전혀 없으면 진짜 최단거리를 알 수 없다(경기도 394개 농장이 이 경우였음).
수역·습지는 전체 41개 세분류 중 일부라 용량이 작으므로, 거리 제한 없이 5개 시도 전체를
그냥 다 모은다.

- landcover_water_wetland_{시도}.parquet  Databricks Volume 업로드용 (geometry -> WKT 문자열)
"""
import glob
import os
import unicodedata

import geopandas as gpd
import pandas as pd

EGIS_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(EGIS_DIR, "raw")
PARQUET_OUT_TEMPLATE = os.path.join(EGIS_DIR, "landcover_water_wetland_{}.parquet")

KEEP_COLS = ["L1_CODE", "L1_NAME", "L2_CODE", "L2_NAME", "L3_CODE", "L3_NAME", "INX_NUM", "geometry"]
WATER_CODES = {"511", "521", "711", "712", "721"}

DBF_ENCODING = "cp949"


def province_from_path(path):
    """raw/{시도}_토지피복지도/{도엽}/{도엽}.shp 경로에서 시도명을 뽑아낸다.

    macOS는 한글 폴더명을 NFD(분해형)로 저장하는데 이 파일의 문자열 리터럴은
    NFC(결합형)라서, 정규화 없이 .replace()를 하면 매칭이 안 된다.
    """
    rel = os.path.relpath(path, RAW_DIR)
    top = unicodedata.normalize("NFC", rel.split(os.sep)[0])
    return top.replace("_토지피복지도", "")


def main():
    shp_paths = sorted(glob.glob(os.path.join(RAW_DIR, "**", "*.shp"), recursive=True))
    if not shp_paths:
        raise FileNotFoundError(f"{RAW_DIR} 아래에 SHP가 없다.")

    kept = []
    for i, path in enumerate(shp_paths, 1):
        gdf = gpd.read_file(path, encoding=DBF_ENCODING)
        gdf = gdf[gdf["L3_CODE"].isin(WATER_CODES)]
        if len(gdf):
            gdf = gdf[[c for c in KEEP_COLS if c in gdf.columns]]
            gdf["시도"] = province_from_path(path)
            kept.append(gdf)

        if i % 500 == 0 or i == len(shp_paths):
            n_kept = sum(len(k) for k in kept)
            print(f"  {i}/{len(shp_paths)} 도엽 처리, 수역/습지 {n_kept}개 누적")

    merged = gpd.GeoDataFrame(pd.concat(kept, ignore_index=True), crs=gpd.read_file(shp_paths[0], encoding=DBF_ENCODING).crs)
    merged_wgs84 = merged.to_crs("EPSG:4326")
    print(f"총 {len(merged_wgs84)}개 수역/습지 polygon (도엽 {len(shp_paths)}개 중)")

    for province, sub in merged_wgs84.groupby("시도"):
        for_join = pd.DataFrame(sub.drop(columns="geometry"))
        for_join["geometry_wkt"] = sub.geometry.to_wkt()
        out_path = PARQUET_OUT_TEMPLATE.format(province)
        for_join.to_parquet(out_path, index=False)
        print(f"✓ {province}: {len(for_join)}개 -> {out_path}")


if __name__ == "__main__":
    main()
