# Risk-based-Routing-for-Disease-Control

가금류 농장의 고병원성 조류인플루엔자(HPAI) 발생 위험도를 예측하여 방역 경로를 최적화하기 위한 Databricks 데이터 파이프라인입니다.

## 아키텍처

Medallion(Bronze → Silver → Gold) 구조로 원본 API/CSV 데이터를 정제·피처화하고, 최종적으로 LightGBM 모델로 농장별 위험도를 예측해 PostgreSQL에 서비스용 결과를 적재합니다.

```
Azure Blob Storage (raw)
  │  bird / outbreak / weather / disinfection
  ▼
01_bronze  →  02_silver  →  03_gold  →  05_MLforJob
                                              │
                                    04_transfer (PostgreSQL / Blob 아카이브)
```

## 폴더 구조

| 폴더 | 역할 |
|---|---|
| [00_shared](00_shared/) | 공용 설정(`utils_config.py`), Blob/PostgreSQL 연결 가이드 및 테스트 노트북 |
| [01_bronze](01_bronze/) | 철새·농장·발생이력·기상 원본 데이터를 API/CSV로 수집해 Bronze Delta 테이블로 적재 |
| [02_silver](02_silver/) | Bronze 데이터 정제 — 축종 코드 전처리, 주소 지오코딩, 농장 마스터/기상 조인 |
| [03_gold](03_gold/) | ML 학습·서비스용 피처 생성 — 철새 노출도, 철새도래지 거리, 역학 피처, 기상 피처, 통합 피처 테이블 |
| [04_transfer](04_transfer/) | 방역시설 정보 PostgreSQL 적재, 30일 경과 데이터 Cold Blob 아카이빙 |
| [05_MLforJob](05_MLforJob/) | LightGBM 기반 농장별 위험도 예측(SHAP 상위 3개 요인 포함) 및 결과 PostgreSQL 적재 |
| [Job](Job/) | Databricks Workflow(Job) 오케스트레이션 정의 및 실패/성공 알림 설정 |

## 참고

- 모든 자격 증명은 Databricks Secret Scope(`dbutils.secrets.get`)로 관리하며 코드에 하드코딩하지 않습니다.
- 데이터 카탈로그·경로 등 환경 값은 [00_shared/utils_config.py](00_shared/utils_config.py)에서 관리합니다.
