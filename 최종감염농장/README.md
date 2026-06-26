# 최종감염농장

시/도별 최종 감염농장 결과(루트 `README.md`의 감염농장 전처리 파이프라인 출력)를 모아두고, 전국 단위로 통합하는 폴더. 시/도별 매칭 로직(정확매칭/유사매칭/주소 보완, 60% 임계값 등)은 루트 `README.md`를 참고.

## 파일 구성

```
{시/도}_최종감염농장.csv   감염농장_전처리.ipynb의 출력 (12컬럼, 시/도별)
전국_최종감염농장.ipynb    위 5개 파일을 통합 + 코드 매핑 + 컬럼 영문화
전국_최종감염농장.csv      전국_최종감염농장.ipynb의 출력
```

`{시/도}_최종감염농장.csv`는 시군명·농장명·축종명·상세구분·사육두수(마리)·소재지지번주소·WGS84위도·WGS84경도·FARM_NM·FARM_LOCPLC·OCCRRNC_DE·LVSTCKSPC_CODE 12컬럼.

## 전국_최종감염농장.ipynb

1. **통합**: `*_최종감염농장.csv` 5개를 그대로 concat. 한글이 들어간 glob 패턴은 macOS의 NFD/NFC 파일명 정규화 문제로 일부 파일이 누락될 수 있어, `*.csv`(ASCII 패턴)로 전체를 잡은 뒤 합친다.
2. **축종명/상세구분 재확정**: `LVSTCKSPC_CODE`로 `livestock_codes.csv`(루트, 정부 API 원본 코드표)를 조회해 `축종명`/`상세구분`을 코드 기준 값으로 덮어쓴다. 시/도별 전처리 단계에서 채운 값이 있어도 코드가 더 신뢰도 높은 출처이므로 무조건 덮어쓰며, 코드표에 없는 코드는 원본 값을 유지하고 별도로 보고한다.
3. **FARM_LOCPLC 보정**: 시/도별 전처리는 농장명이 **정확히** 같을 때만 주소를 덮어썼기 때문에, 유사매칭(이름 유사도 ≥60%)으로만 연결된 농장은 `소재지지번주소`는 채워져 있어도 `FARM_LOCPLC`는 덜 정확한 원본 주소로 남아있었다. `소재지지번주소`가 있는(=매칭에 성공한) 행은 모두 `FARM_LOCPLC`를 그 값으로 덮어쓴다.
4. **컬럼 영문화 + 저장**: 시군명→county, 농장명→farm_name, 축종명→livestock_name, 상세구분→livestock_type, 사육두수(마리)→head_count, 소재지지번주소→jibun_address, WGS84위도→latitude, WGS84경도→longitude, FARM_NM→farm_alias, FARM_LOCPLC→farm_address, OCCRRNC_DE→outbreak_date, LVSTCKSPC_CODE→livestock_code로 이름을 바꿔 `전국_최종감염농장.csv`로 저장.

## 알려진 한계

- 현재 저장된 `전국_최종감염농장.csv`는 10컬럼(`county, farm_name, livestock_name, livestock_type, head_count, farm_address, latitude, longitude, outbreak_date, livestock_code`)인데, 노트북의 `COLUMN_RENAME`에는 `jibun_address`(소재지지번주소)·`farm_alias`(FARM_NM) 두 컬럼이 더 정의돼 있다. 노트북을 마지막으로 실행한 시점 이후 `COLUMN_RENAME`이 12개 키로 확장됐는데 재실행은 안 된 상태로, 노트북을 다시 돌리면 출력이 12컬럼으로 바뀐다.
