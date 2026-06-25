# 방역로 (BioRoute)

가축전염병 방역 경로 자동 배치 시스템.
AI 위험도 기반으로 방역 팀의 농장 방문 경로를 자동 생성하고 실시간 현황을 추적한다.

---

## 기술 스택

- **프론트엔드**: React 18 + TypeScript + Vite + MUI + Zustand
- **백엔드**: FastAPI (Python 3.11)
- **지도**: Naver Maps JavaScript API v3

---

## 로컬 개발 환경 설정

### 1. 환경변수 설정

루트에 `.env` 파일 생성:

```env
VITE_NAVER_MAP_CLIENT_ID=your-naver-cloud-platform-maps-client-id
VITE_API_BASE_URL=http://localhost:8000
```

`backend/.env` 파일 생성:

```env
NAVER_CLIENT_ID=your-naver-client-id
NAVER_CLIENT_SECRET=your-naver-client-secret
DATABRICKS_HOST=
DATABRICKS_HTTP_PATH=
DATABRICKS_TOKEN=
```

---

### 2. 프론트엔드 개발 서버

Node.js 18 이상 필요.

```bash
# 의존성 설치 (최초 1회)
npm install

# 개발 서버 시작 (http://localhost:5173)
npm run dev
```

---

### 3. 백엔드 서버

Python 3.11 이상 필요.

```bash
# backend 디렉토리로 이동
cd backend

# 가상환경 생성 및 활성화 (최초 1회)
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

# 패키지 설치 (최초 1회)
pip install -r requirements.txt

# 서버 시작 (http://localhost:8000)
uvicorn main:app --reload
```

백엔드가 실행되면 아래 주소에서 API 문서를 확인할 수 있다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 주요 API

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/farms` | 농장 목록 조회 |
| POST | `/api/directions/multi` | 다중 경유지 경로 계산 (Naver Directions 5 프록시) |

---

## 프로젝트 구조

자세한 구조는 [structure.md](structure.md) 참고.

---

## Azure 배포

배포 방법은 [.claude/plans](../.claude/plans/) 내 플랜 문서 참고.

`main` 브랜치에 push하면 GitHub Actions가 자동으로 Azure App Service에 배포한다.
