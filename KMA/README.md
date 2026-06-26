# KMA 날씨 데이터 파이프라인

농장의 조사날짜 기준 최근 30일 날씨를 붙이기 위한 기상청 API Hub 연동 파이프라인.

## 실행 순서

```
1. fetch_weather.py    -> weather_daily_raw.csv  (전국 관측소 일별 원자료)
2. fetch_stn_info.py   -> stn_info.csv            (관측소 위경도 메타데이터)
3. match_farm_weather.py -> ML_농장_날씨.csv       (농장별 최근접 관측소 매칭 + 날씨 병합)
```

`fetch_stn_info.py`는 `weather_daily_raw.csv`에 등장하는 관측소 번호 목록을 먼저 읽으므로 1번 다음에 실행해야 한다.

## 파일별 설명

### fetch_weather.py -> weather_daily_raw.csv
`ML/ML_전국_농장현황_1year.csv`의 조사날짜마다 (조사날짜-30일 ~ 조사날짜) 구간을 모아, 그 구간을 커버하는 전체 관측소(`stn=0`) ASOS 일자료(`kma_sfcdd3`)를 조회한다.

- 행 단위: (관측소, 날짜) 조합 1개
- API의 결측 sentinel 값(`-9`, `-99`, `-999`)은 `NaN`으로 치환
- 결측치 대부분은 수집 실패가 아니라 "그 관측소에 장비가 없음"(예: 지중온도 `TE_*`) 또는 "그 현상 자체가 없음"(예: 비 안 온 날의 `RN_DAY`)에서 발생

### fetch_stn_info.py -> stn_info.csv
관측소 번호별 위경도를 가져온다. ASOS 목록(`inf=SFC`)이 기본이고, `weather_daily_raw.csv`에는 있지만 ASOS 목록에는 없는 관측소(AWS 보조관측소로 운영되는 경우)는 `inf=AWS` 목록에서 보충한다.

- 행 단위: 관측소 1개
- 컬럼: `STN`, `STN_KO`, `LAT`, `LON`
- 알려진 한계: 관측소 176번은 ASOS/AWS 목록 어디에도 메타데이터가 없어 제외됨 (폐쇄/이전된 옛 관측소로 추정, `weather_daily_raw.csv` 121,139행 중 10행만 해당해 영향 미미)
- 지점정보(`stn_inf`) API는 기상청 API Hub에서 ASOS 일자료(`kma_sfcdd3`)와 별도로 활용신청이 필요하다.

### match_farm_weather.py -> ML_농장_날씨.csv
농장 좌표와 관측소 좌표 사이 하버사인 거리로 최근접 관측소를 찾고, 그 관측소의 (조사날짜-30일 ~ 조사날짜) 구간 일별 날씨를 그대로 붙인다.

- 행 단위: (농장, 날씨를 가져온 날짜) 조합 1개 — 농장 1건당 최대 31행
- 좌표 없는 농장은 매칭에서 제외 (5,831건 중 4건)
- `matched_STN`/`matched_STN_KO`/`matched_dist_km` 컬럼으로 어느 관측소가 매칭됐고 거리가 얼마인지 확인 가능 (전국 평균 16.0km, 최대 34.7km — 관측소가 100개뿐이라 일부는 멀리 매칭됨)
- 조사날짜가 같아도 농장 위치(=최근접 관측소)가 다르면 서로 다른 날씨 시계열이 붙으므로, 농장현황(5,827건) 대비 결과 행 수(180,343행)가 크게 늘어난다 — 농장당 1행으로 집계가 필요하면 별도 요약 단계가 필요하다.

## 환경 변수

`.env`에 `KMA_API_KEY` 필요 (기상청 API Hub, ASOS 일자료 + 지점정보 두 API 모두 활용신청 필요).
