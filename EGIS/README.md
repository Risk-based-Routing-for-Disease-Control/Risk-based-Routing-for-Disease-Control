# EGIS 토지피복지도 파이프라인

농장 주변 환경(논·밭·시설재배지·과수원·산림·습지·수역 비율, 수역/습지 최단거리)을 Feature로 만들기 위한
환경공간정보서비스(EGIS, https://aid.mcee.go.kr/api/land.do) 토지피복지도 연동 파이프라인.

**Databricks Sedona 공간조인이 계속 에러나서, 최종 Feature 계산까지 이 폴더(로컬 geopandas)에서 끝낸다.**
Databricks는 결과 테이블(`ML_농장_토지피복_feature.csv`)을 farm_master에 조인해서 저장만 하면 된다 — GIS 연산 불필요.

흐름: 도엽 단위 SHP 병합 → 용량 절감용 사전 컷(3km/거리무제한) → 농장별 정확한 buffer ∩ polygon
intersection과 최단거리 계산까지 전부 여기서 수행.

## 데이터 입수 (수동)

토지피복지도 원본 SHP는 도엽(Map Sheet) 단위로 배포되며, 온라인 자료신청을 거쳐야 받을 수 있다.

1. https://aid.mcee.go.kr/api/land.do 에서 로그인 → 자료검색 → 신청서 등록 → 설문조사 완료 → 도엽 단위 SHP 다운로드
2. 농장이 위치한 시/도를 덮는 도엽들을 모두 받아 압축을 풀어 `EGIS/raw/{도엽번호}/` 에 넣는다 (SHP/DBF/SHX/PRJ/XML 세트 전부)
   - 검증용 샘플: 평택(014), 도엽번호 `36701014`

**범위**: 세분류 [2025] 전국, 농장이 있는 5개 시/도(경기도·전라북도·전라남도·충청북도·충청남도)만 — 전국 전체를 한 번에 받으면 용량이 너무 커서 시/도별로 나눠 받는다. 연도는 농장 조사날짜 분포·기존 검증 샘플과 맞춰 2025 한 해만 정적 스냅샷으로 쓴다 (토지피복은 단기간에 크게 안 바뀌므로 연도별로 따로 받지 않음).

`raw/` 는 도엽 수가 많아지면 용량이 커지므로 `.gitignore`로 제외했다. 커밋 대상은 가공 결과물(`landcover_merged.gpkg`, `landcover_for_join_{시도}.parquet`)뿐이다.

## 실행 순서

```
1. merge_landcover.py        -> landcover_merged.gpkg                  (로컬 QGIS 확인용, 농장 3km 이내로 필터링된 결과, 전체 시도 한 파일)
                              -> landcover_for_join_{시도}.parquet      (면적비율 계산용 중간 산출물, 시도별로 분리)
2. extract_water_wetland.py  -> landcover_water_wetland_{시도}.parquet  (수역·습지만, 거리 제한 없음 — 최단거리 계산용)
3. compute_features.py       -> ML_농장_토지피복_feature.csv            (최종 결과, Databricks Volume 업로드용)
```

`landcover_for_join_{시도}.parquet`(3km 컷)은 면적비율(`paddy_area_ratio_3km`, `water_area_ratio_3km` 등)에는 정확하지만,
반경 제한이 없는 `dist_nearest_water_km`(최단거리)에는 부족할 수 있다 — 농장 근처 3km 안에 수역·습지가 전혀 없으면
진짜 최단거리를 알 수 없기 때문이다. 실제로 경기도 농장 3,665건 중 394건이 3km 안에 수역·습지가 없었다
(검증 결과 이 경우들도 우연히 다른 농장의 3km 버퍼에 걸려 정답이 데이터에 남아있었지만, 구조적으로 보장되는 게 아니다).
그래서 `dist_nearest_water_km`는 거리 제한 없는 `landcover_water_wetland_{시도}.parquet`을 입력으로 쓴다.

농장 좌표는 `ML/ML_전국_농장현황_1year.csv`를 그대로 읽어서 쓴다. 따로 파일로 저장하지 않는다.

## 파일별 설명

### merge_landcover.py -> landcover_merged.gpkg, landcover_for_join_{시도}.parquet
`raw/` 아래 모든 도엽 SHP를 재귀적으로 찾아 `L1~L3 CODE/NAME`, `INX_NUM`, `geometry`만 남기고 하나로 합친 뒤,
농장 좌표 기준 `RADIUS_KM`(기본 3km) 이내에 있는 polygon만 남기고 WGS84(EPSG:4326)로 투영한다.
면적비율 계산의 입력이 되는 중간 산출물이라, 정확한 buffer ∩ polygon intersection은 여기서 안 하고 `compute_features.py`가 한다.

- 행 단위: Polygon(토지피복 구역) 1개, 농장 3km 이내인 것만
- `landcover_merged.gpkg`: 로컬 QGIS 확인용, 시도 구분 없이 전체 한 파일

### extract_water_wetland.py -> landcover_water_wetland_{시도}.parquet
`raw/` 아래 모든 도엽 SHP에서 수역·습지(`L3_CODE` 511/521/711/712/721)만 거리 제한 없이 전부 모은다.
공간조인이 없어서 `merge_landcover.py`보다 빠르고, 용량도 작다(5개 시도 합쳐 204MB, polygon 453,474개).

### compute_features.py -> ML_농장_토지피복_feature.csv
농장별로 정확한 buffer ∩ polygon intersection(면적비율)과 최단거리를 직접 계산해서 최종 Feature 테이블을 만든다.
Databricks는 이 결과를 farm_master에 `farm_id`(= `MD5(농장명|소재지지번주소)`, 기상/철새 Feature와 동일한 surrogate key)로
조인해서 저장만 하면 된다.

- 행 단위: 농장(`farm_id`) 1건
- 출력 컬럼: `farm_id`, `시도명`, `시군명`, `농장명`, `조사날짜`, `paddy_area_ratio_3km`, `field_area_ratio_3km`,
  `greenhouse_area_ratio_3km`, `orchard_area_ratio_3km`, `forest_area_ratio_3km`, `wetland_area_ratio_3km`,
  `water_area_ratio_3km`(습지+수역 합산, Feature 카탈로그 정의와 동일), `dist_nearest_water_km`
- **처리 방식**: 농장 전체 × polygon 전체를 한 번에 `gpd.overlay`로 돌리면 농장이 밀집된 지역에서 교차 조각이
  수백만~천만 개로 불어나 메모리가 터진다(첫 시도 실패 사례). 농장 하나씩, `lc_gdf.sindex.query()`로 후보
  polygon만 추려서 그 농장의 buffer와만 intersection을 계산하고 바로 버린다.
- **시군 단위로 쪼개서 처리**하고 시군이 끝날 때마다 결과를 csv에 바로 append한다. 중간에 죽어도 그동안
  처리한 시군은 남고, 재실행하면 이미 끝난 (시도,시군)은 자동으로 건너뛴다.
- **geometry 오류 처리**: `buffer(0)`보다 `shapely.make_valid()`가 "구멍을 shell에 못 붙이는" 류의 토폴로지
  오류를 더 잘 고친다. 그래도 안 고쳐지는 경우(실제로 전라북도에서 1건 발생)는 그 polygon만 0으로 처리하고
  건너뛴다 — 전체 작업을 죽이지 않는다.
- 소요 시간: 5개 시도(농장 5,829건, polygon 약 780만 개) 처리에 총 2~3시간 (경기도 화성시처럼 농장이
  밀집된 지역은 유독 오래 걸림).

## L3_CODE 그룹 (전체 41개 세분류 중 우선 활용, `compute_features.py`의 출력 컬럼명)

| 출력 컬럼 | L3_CODE | 설명 |
| --- | --- | --- |
| `paddy_area_ratio_3km` | 211, 212 | 논 (경지정리 여부) |
| `field_area_ratio_3km` | 221, 222 | 밭 (경지정리 여부) |
| `greenhouse_area_ratio_3km` | 231 | 시설재배지 |
| `orchard_area_ratio_3km` | 241 | 과수원 |
| `forest_area_ratio_3km` | 311, 321, 331 | 산림 (활엽수/침엽수/혼효림) |
| `wetland_area_ratio_3km` | 511, 521 | 습지 (내륙습지/갯벌) |
| `water_area_ratio_3km` | 511, 521, 711, 712, 721 | 습지+수역 합산 (Feature 카탈로그의 `water_area_ratio_3km` 정의와 동일) |

## 알려진 한계

- `geopandas`/`pyarrow` 의존성을 가상환경에 설치해야 한다 (`pip install geopandas pyarrow`).
- 도엽 SHP의 `.prj`는 GRS80/TM이지만 **False_Northing이 600000**이다 — EPSG:5181(False_Northing 500000)과 다른 좌표계라, EPSG 코드로 가정하면 위도가 약 0.9도(100km) 북쪽으로 틀리게 계산된다. `+proj=tmerc +lat_0=38 +lon_0=127 +k=1 +x_0=200000 +y_0=600000 +ellps=GRS80` 커스텀 CRS를 써야 한다.
- 도엽 수천 개를 한꺼번에 `pd.concat`으로 합친 뒤 필터링하면 폴리곤이 수백만~천만 개로 쌓여 메모리가 터진다(처음 시도가 23분 만에 OOM으로 죽었음) — `merge_landcover.py`는 도엽 하나씩 읽어서 그 자리에서 5km 필터링하고 살아남은 것만 누적하도록 고쳤다.
- 5개 시/도 전체(도엽 9,098개)를 RADIUS_KM=3으로 돌린 결과: 원본 polygon 23,342,370개 → 3km 필터링 후 7,829,088개(66% 감소). 농장이 5개 도 전역에 넓게 퍼져있어서 반경을 줄이는 것만으로는 용량 절감 효과가 크지 않다 — `landcover_merged.gpkg` 7.3GB.

  | 시도 | polygon 수 | parquet 용량 |
  | --- | --- | --- |
  | 경기도 | 3,730,509 | 1.1GB |
  | 전라남도 | 1,859,696 | 694MB |
  | 전라북도 | 911,528 | 268MB |
  | 충청남도 | 704,988 | 214MB |
  | 충청북도 | 622,367 | 220MB |

- macOS는 한글 폴더명을 NFD(분해형)로 저장하는데 소스 코드의 한글 문자열 리터럴은 NFC(결합형)라서, `unicodedata.normalize("NFC", ...)` 없이 `.replace()`나 `glob` 패턴 매칭을 하면 조용히 매칭이 안 된다 (`province_from_path`가 처음엔 `"경기도_토지피복지도"`를 못 잘라내서 파일명에 접미사가 그대로 남는 버그가 있었음).
- `data/내륙습지_2704_EPSG5186.gpkg`는 본 파이프라인의 입력이 아니다 — 국가습지인벤토리(`inland_wetlands_2704` 테이블) 데이터로, 토지피복지도와 출처·스키마가 다른 별도 데이터다.
- 최단거리(`dist_nearest_water_km`) 계산은 폴리곤 경계(boundary) 기준 — `geometry.distance()`는 점이 polygon 밖에 있으면 경계까지 거리와 같으므로 별도 처리 불필요. 로그 변환 적용 여부는 모델링 담당자 협의 후 결정.
- `gpd.overlay`로 농장 전체 × polygon 전체를 한 번에 처리하면 농장 밀집 지역에서 교차 조각이 폭증해 메모리가 터진다 — 충청북도(농장 261건, 가장 작은 시도)만 해도 overlay 결과가 557만 개였다. `compute_features.py`는 농장 하나씩 spatial index로 후보만 추려서 처리하도록 고쳤다.
- GEOS는 "구멍을 shell에 못 붙이는" 류의 토폴로지 오류가 있는 polygon을 만나면 `intersection()` 자체가 예외를 던진다(전라북도에서 실제 발생). `buffer(0)`보다 `shapely.make_valid()`가 더 잘 고치고, 그래도 안 되면 해당 polygon만 0으로 건너뛴다.
- `compute_features.py`는 시군 단위로 끝날 때마다 결과를 csv에 append하고, 재실행 시 이미 처리된 (시도,시군)은 건너뛴다 — 중간에 죽어도 처음부터 다시 돌릴 필요가 없다.
