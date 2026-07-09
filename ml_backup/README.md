# HPAI 농장 위험도 예측 ML 백업 리소스

## 1. 개요

이 폴더는 HPAI 농장 위험도 예측 ML 파이프라인의 Public 공유용 백업 리소스를 정리한 폴더입니다.

기존 파이프라인은 Databricks 환경에서 실행되었으며, Signed LightGBM 모델을 사용해 농장별 HPAI 위험도 예측 결과를 생성했습니다.

이 Public 저장소에는 코드 구조와 실행 흐름을 설명하기 위한 파일만 포함합니다.  
실제 최종 모델 artifact와 농장 단위 데이터는 포함하지 않습니다.

---

## 2. 폴더 구조

```text
ml_backup/
├─ README.md
├─ notebooks/
│  └─ 02_ml_public_sanitized.ipynb
├─ config/
│  └─ model_input_features.json
├─ sql/
│  └─ create_farm_risk_predictions.sql
└─ logs/
   └─ model_backup_test_log.txt
```

---

## 3. 포함 파일 설명

### notebooks/02_ml_public_sanitized.ipynb

Job2 배치 예측 노트북의 Public 공개용 버전입니다.

Public 공개를 위해 아래 항목을 제거하거나 placeholder로 변경했습니다.

- 실행 결과 output
- execution count
- 실제 Databricks 테이블명
- 실제 MLflow 모델 URI
- 내부 Run ID 및 모델 식별자

이 노트북은 모델 예측 흐름을 설명하기 위한 참고용 파일이며, 그대로 실행하는 용도는 아닙니다.

---

### config/model_input_features.json

최종 Signed LightGBM 모델에 입력되는 Feature 30개 목록과 순서를 저장한 파일입니다.

다른 환경에서 모델을 실행할 경우 입력 DataFrame은 이 Feature 목록과 순서를 기준으로 맞춰야 합니다.

---

### sql/create_farm_risk_predictions.sql

Supabase/PostgreSQL에 농장별 위험도 예측 결과를 저장하기 위한 테이블 생성 SQL입니다.

이 SQL 파일은 테이블 구조만 생성하며, 실제 예측 데이터는 포함하지 않습니다.

---

### logs/model_backup_test_log.txt

백업한 모델 artifact가 정상적으로 로드되고, 샘플 입력 데이터로 예측이 성공했는지 확인한 로그입니다.

---

## 4. Public 저장소에서 제외한 파일

아래 파일들은 Public GitHub에 포함하지 않습니다.

```text
signed_lightgbm_model_backup.zip
farm_risk_predictions_20251216.csv
ml_dataset_radius_all_20251216.csv
sample_ml_dataset_radius_all_20251216.csv
02_ml.ipynb
02_ml.html
02_ml_public.ipynb
```

제외 이유는 다음과 같습니다.

- 실제 최종 모델 artifact 포함
- 농장 단위 예측 결과 포함
- 농장 단위 Feature 데이터 포함
- 원본 Databricks 실행 결과 포함
- 내부 Databricks/MLflow 식별자 포함 가능성

위 파일들은 팀 내부 비공개 공유 폴더에서 별도로 관리합니다.

---

## 5. Databricks 리소스 대체 안내

기존 Databricks 리소스가 삭제될 경우, 아래 파일들로 대체할 수 있습니다.

```text
Databricks MLflow 모델 URI
→ signed_lightgbm_model_backup.zip

Databricks Gold Feature Table
→ ml_dataset_radius_all_20251216.csv

Databricks Delta Prediction Table
→ farm_risk_predictions_20251216.csv
```

Public 노트북에서는 실제 값을 아래와 같은 placeholder로 변경했습니다.

```text
models:/<signed_model_uri>
<catalog>.<schema>.ml_dataset_radius_all_YYYYMMDD
<catalog>.<schema>.farm_risk_predictions_YYYYMMDD
```

실제 실행 시에는 위 placeholder를 로컬 경로, DB 연결 정보, 클라우드 스토리지 경로 등 목표 환경에 맞게 변경해야 합니다.

---

## 6. 이전 후 활용 방법

### 6.1 기존 예측 결과를 웹앱에서 사용하는 경우

모델을 다시 실행하지 않고, 이미 생성된 예측 결과 CSV를 사용하는 방식입니다.

```text
1. sql/create_farm_risk_predictions.sql을 Supabase SQL Editor에서 실행
2. farm_risk_predictions_20251216.csv를 생성된 테이블에 import
3. Render 백엔드에서 Supabase/PostgreSQL 조회 API 구성
4. Vercel 프론트엔드에서 riskScore, riskLevel, riskRank, riskFactors 표시
```

단, `farm_risk_predictions_20251216.csv`는 Public 저장소에 포함하지 않고 팀 내부에서 비공개 공유합니다.

---

### 6.2 모델을 다시 실행하는 경우

Databricks 외부 환경에서 모델을 다시 실행할 경우 다음 흐름으로 사용합니다.

```text
1. signed_lightgbm_model_backup.zip 압축 해제
2. 압축 해제된 모델 폴더를 mlflow.sklearn.load_model로 로드
3. model_input_features.json 로드
4. ml_dataset_radius_all_20251216.csv 로드
5. Feature 30개 순서대로 입력 DataFrame 생성
6. predict_proba 실행
7. 예측 결과를 CSV 또는 Supabase/PostgreSQL에 저장
```

예시:

```python
import json
import pandas as pd
import mlflow.sklearn

model = mlflow.sklearn.load_model("./signed_lightgbm_model")

with open("config/model_input_features.json", "r", encoding="utf-8") as f:
    feature_columns = json.load(f)

df = pd.read_csv("ml_dataset_radius_all_20251216.csv")
X = df[feature_columns]

proba = model.predict_proba(X)
df["riskScore"] = proba[:, 1]
```

---

## 7. 주의사항

- 이 저장소에는 실제 최종 모델 artifact가 포함되어 있지 않습니다.
- 이 저장소에는 농장 단위 예측 결과와 Feature 데이터가 포함되어 있지 않습니다.
- Public용 노트북은 구조 설명용이며 그대로 실행하는 파일이 아닙니다.
- 원본 실행 노트북과 HTML 결과 파일은 팀 내부에서 비공개로 관리합니다.
- 실제 배포 시에는 비공개 모델/데이터 파일과 환경별 경로를 사용해야 합니다.