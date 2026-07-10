# BioRoute Infrastructure

BioRoute 프로젝트에서 사용하는 Azure 인프라 정의 파일입니다.

이 저장소에는 동일한 Azure 인프라를 서로 다른 Infrastructure as Code 방식으로 표현한 파일이 포함되어 있습니다.

* Terraform
* Bicep
* ARM Template

각 파일은 별도의 인프라가 아니라, 기존 Azure 환경을 코드 형태로 정리한 결과물입니다.

---

## 파일 구성

```text
infra/
├── dt4-team1-infra.terraform
├── dt4-team1-infra.bicep
├── azuredeploy.json
└── README.md
```

| 파일                        | 설명                            |
| ------------------------- | ----------------------------- |
| `dt4-team1-infra.terraform`       | Terraform 형식의 Azure 인프라 정의    |
| `dt4-team1-infra.bicep`    | Bicep 형식의 Azure 인프라 정의        |
| `azuredeploy.json` | ARM Template 형식의 Azure 인프라 정의 |
| `README.md`               | 인프라 구성 및 사용 방법 설명             |

---

## 주요 Azure 리소스

이 인프라에는 다음과 같은 Azure 리소스가 포함되어 있습니다.

| Azure 리소스                                     | 역할                            |
| --------------------------------------------- | ----------------------------- |
| Azure Databricks                              | 데이터 처리, 분석 및 머신러닝 파이프라인 실행    |
| Azure Databricks Access Connector             | Databricks와 Azure 리소스 간 인증 연결 |
| Azure Database for PostgreSQL Flexible Server | 서비스 및 분석 결과 저장                |
| Azure Storage Account                         | 원천 데이터 및 파일 저장                |
| Azure Functions                               | 데이터 수집 및 서버리스 처리              |
| Azure App Service                             | 웹 애플리케이션 실행                   |
| Azure Logic Apps                              | 알림 및 외부 서비스 연동                |
| Application Insights                          | 애플리케이션 로그 및 성능 모니터링           |
| Azure Monitor Action Group                    | 장애 및 수집 실패 알림 전송              |
| Microsoft Teams Connector                     | Teams 채널 알림 전송                |
| Office 365 Connector                          | 이메일 알림 전송                     |
| Managed Identity                              | Azure 리소스 간 안전한 인증            |

---

## 전체 처리 흐름

```text
외부 데이터
    │
    ▼
Azure Functions
데이터 수집
    │
    ▼
Azure Storage Account
원천 데이터 저장
    │
    ▼
Azure Databricks
전처리 · 분석 · 머신러닝
    │
    ├───────────────┐
    ▼               ▼
PostgreSQL       예측 결과 생성
결과 저장
    │
    ▼
Azure App Service
웹 서비스 및 결과 제공
    │
    ▼
Logic Apps · Teams · Email
장애 및 처리 결과 알림
```

---

## 파일별 특징

### 1. Terraform

파일:

```text
dt4-team1-infar.terragorm
```

Terraform을 사용해 Azure 리소스를 선언하는 파일입니다.

현재 저장소는 하나의 Terraform 파일로 구성되어 있으며, 별도의 다음 파일은 포함되어 있지 않습니다.

```text
variables.tf
outputs.tf
terraform.tfvars
```

민감한 값은 Terraform 변수로 분리되어 있으며, 실행 시 환경 변수 또는 별도 변수 파일을 통해 전달해야 합니다.

Terraform 실행 예시는 다음과 같습니다.

```bash
terraform init
terraform validate
terraform plan
terraform apply
```

Terraform 변수는 환경 변수 방식으로 전달할 수 있습니다.

```bash
export TF_VAR_collector_webhook_service_uri="<WEBHOOK_URL>"
export TF_VAR_office365_email="<OFFICE365_EMAIL>"
export TF_VAR_teams_email="<TEAMS_EMAIL>"
```

Windows PowerShell에서는 다음과 같이 설정할 수 있습니다.

```powershell
$env:TF_VAR_collector_webhook_service_uri="<WEBHOOK_URL>"
$env:TF_VAR_office365_email="<OFFICE365_EMAIL>"
$env:TF_VAR_teams_email="<TEAMS_EMAIL>"
```

실제 변수명은 `main_sanitized.tf`에 선언된 이름을 기준으로 입력해야 합니다.

---

### 2. Bicep

파일:

```text
dt4-team1-infra.bicep
```

Azure Bicep 문법으로 작성된 인프라 정의 파일입니다.

배포 예시는 다음과 같습니다.

```bash
az deployment group create \
  --resource-group <RESOURCE_GROUP_NAME> \
  --template-file main_sanitized.bicep
```

민감한 값은 Bicep의 `@secure()` 파라미터로 분리되어 있습니다.

배포 시 명령어에서 직접 전달할 수 있습니다.

```bash
az deployment group create \
  --resource-group <RESOURCE_GROUP_NAME> \
  --template-file main_sanitized.bicep \
  --parameters \
    collectorWebhookServiceUri="<WEBHOOK_URL>" \
    office365Email="<OFFICE365_EMAIL>" \
    teamsEmail="<TEAMS_EMAIL>"
```

---

### 3. ARM Template

파일:

```text
azuredeploy.json
```

Azure Resource Manager에서 직접 사용할 수 있는 JSON 형식의 배포 템플릿입니다.

배포 예시는 다음과 같습니다.

```bash
az deployment group create \
  --resource-group <RESOURCE_GROUP_NAME> \
  --template-file template_sanitized.json
```

필요한 파라미터는 배포 시 직접 전달할 수 있습니다.

```bash
az deployment group create \
  --resource-group <RESOURCE_GROUP_NAME> \
  --template-file template_sanitized.json \
  --parameters \
    collectorWebhookServiceUri="<WEBHOOK_URL>" \
    office365Email="<OFFICE365_EMAIL>" \
    teamsEmail="<TEAMS_EMAIL>"
```

---

## 민감정보 처리

공개 저장소 업로드를 위해 다음 정보는 코드에서 제거하거나 외부 파라미터로 분리했습니다.

* Logic App Webhook URL
* Logic App Webhook 서명값
* Office 365 이메일 주소
* Microsoft Teams 이메일 주소
* PostgreSQL 허용 IP 주소
* Teams Team ID
* Teams Channel ID
* Azure Principal ID
* App Service Domain Verification ID
* Azure Subscription ID
* 사용자 이름 또는 이니셜이 포함된 방화벽 규칙명

민감한 값은 Git 저장소에 직접 업로드하지 않아야 합니다.

---

## 주의사항

### Webhook URL

Logic App Webhook URL에는 일반적으로 다음과 같은 서명값이 포함됩니다.

```text
sig=<SIGNATURE>
```

이 값이 외부에 노출된 경우 기존 URL을 그대로 사용하지 말고 Azure Portal에서 새 Webhook URL을 발급하는 것이 안전합니다.

### PostgreSQL Firewall

PostgreSQL Firewall IP는 실제 접속이 필요한 환경의 공인 IP만 허용해야 합니다.

다음과 같이 전체 인터넷을 허용하는 설정은 피해야 합니다.

```text
0.0.0.0 - 255.255.255.255
```

### API Connection

Office 365, Outlook 및 Teams API Connection은 ARM 또는 Bicep 배포 후에도 Azure Portal에서 사용자 로그인을 통한 재인증이 필요할 수 있습니다.

### 리소스 이름 중복

Storage Account, App Service, Function App 등의 일부 Azure 리소스 이름은 전 세계에서 고유해야 합니다.

기존 이름이 이미 사용 중인 경우 배포 전에 이름을 변경해야 합니다.

---

## 배포 전 준비사항

Azure CLI 로그인:

```bash
az login
```

현재 구독 확인:

```bash
az account show
```

사용할 구독 선택:

```bash
az account set --subscription "<SUBSCRIPTION_ID>"
```

리소스 그룹이 없다면 생성합니다.

```bash
az group create \
  --name <RESOURCE_GROUP_NAME> \
  --location koreacentral
```

---

## 권장 사용 방식

세 파일을 모두 배포할 필요는 없습니다.

아래 중 하나의 방식만 선택하여 사용할 수 있습니다.

| 방식           | 적합한 경우                                   |
| ------------ | ---------------------------------------- |
| Terraform    | 여러 환경을 반복적으로 관리하고 상태를 추적할 때              |
| Bicep        | Azure 중심으로 간결하게 인프라를 관리할 때               |
| ARM Template | Azure Portal에서 내보낸 원본 구조를 확인하거나 직접 배포할 때 |

현재 세 파일은 같은 인프라를 서로 다른 형식으로 표현한 것이므로, 동시에 실행하면 동일하거나 유사한 리소스가 중복 생성될 수 있습니다.

---

## 보안 권장사항

운영 환경에서는 다음 구성을 권장합니다.

* Azure Key Vault에 비밀값 저장
* Managed Identity 사용
* PostgreSQL Public Network Access 제한
* Storage Account Public Access 제한
* 최소 권한 원칙에 따른 RBAC 적용
* Logic App Webhook 주기적 재발급
* `.tfvars` 및 파라미터 파일 Git 제외
* 운영 환경과 개발 환경의 리소스 분리

---

## 프로젝트 목적

이 인프라는 BioRoute 프로젝트의 데이터 수집, 저장, 분석, 머신러닝, 웹 서비스 및 알림 기능을 Azure 환경에서 운영하기 위한 기반을 제공합니다.

애플리케이션 코드, Databricks Notebook, 머신러닝 모델, 데이터셋 및 실제 인증정보는 이 저장소에 포함되어 있지 않습니다.
