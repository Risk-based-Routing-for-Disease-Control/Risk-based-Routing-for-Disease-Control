# 가축전염병 방역 배치 시스템 — 프로젝트 구조

## 개요

경기도 축산 농가를 대상으로 AI 위험도 기반 방역 경로를 자동 배치하는 웹 앱.  
방역 담당자가 당일 가용 팀과 대상 농장을 선택하면, 시스템이 팀별 경로를 자동 생성하고 실시간 현황을 추적한다.

## 기술 스택

| 구분 | 기술 |
|------|------|
| 프론트엔드 | React 18 + TypeScript + Vite |
| UI | MUI (Material UI) v6 |
| 상태 관리 | Zustand |
| 라우팅 | React Router v6 |
| 지도 | Naver Maps JavaScript API v3 |
| 백엔드 | FastAPI (Python) |
| DB 연동 준비 | Databricks SQL (미연동, 더미 데이터) |

## 디렉토리 구조

```
livestock/
├── src/
│   ├── App.tsx                        # 라우터 루트, ThemeProvider 설정
│   ├── main.tsx                       # React 진입점
│   ├── index.css                      # 전역 CSS
│   │
│   ├── pages/
│   │   ├── MapPage.tsx                # /map — 농장 지도 + 상세 패널
│   │   ├── DispatchPage.tsx           # /dispatch — 배치 설정 or 결과 (result 유무로 분기)
│   │   └── ConfirmedRoutePage.tsx     # /confirmed — 확정 경로 + 실시간 현황
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx          # 공통 레이아웃 (Header + Sidebar + Outlet)
│   │   │   ├── AppHeader.tsx          # 상단 헤더
│   │   │   └── AppSidebar.tsx         # 좌측 네비게이션 (지도/배치/확정 이동)
│   │   ├── map/
│   │   │   ├── NaverMap.tsx           # Naver Maps 렌더링, 마커/툴팁 관리
│   │   │   ├── MapControls.tsx        # 줌 인/아웃, 현재 위치 버튼
│   │   │   └── MapLegend.tsx          # 위험도 범례
│   │   ├── detail/
│   │   │   └── FarmDetailPanel.tsx    # 우측 농장 상세 정보 패널 (XAI 요인 포함)
│   │   ├── dispatch/
│   │   │   ├── DispatchSettingsView.tsx  # 팀 수 설정 + 농장 선택 테이블
│   │   │   └── DispatchResultView.tsx    # 배치 결과 지도 + 팀별 요약 카드
│   │   └── route/
│   │       ├── RouteMap.tsx           # 배치/확정 결과 지도 (팀별 색상 폴리라인)
│   │       ├── TeamSummaryCard.tsx    # 배치 결과 — 팀별 방문 순서 카드
│   │       ├── UnassignedFarmsCard.tsx # 배치 결과 — 미배정 농장 목록
│   │       ├── LiveTeamCard.tsx       # 확정 현황 — 팀별 완료/예정 진행 카드
│   │       └── RouteLegend.tsx        # 경로 지도 팀 범례
│   │
│   ├── store/
│   │   ├── useFarmStore.ts            # 농장 목록 + 선택 상태 (현재 mockFarms 하드코딩)
│   │   └── useDispatchStore.ts        # 배치 전체 상태 (설정 → 결과 → 확정 → 라이브)
│   │
│   ├── hooks/
│   │   ├── useNaverMapsScript.ts      # Naver Maps SDK 동적 로드
│   │   └── useTeamRoutes.ts           # 팀별 다중 경유지 경로 API 호출 + 캐싱
│   │
│   ├── api/
│   │   └── directions.ts             # /api/directions/multi POST 호출, 경로 flatten 유틸
│   │
│   ├── types/
│   │   ├── farm.ts                   # Farm, RiskLevel, XaiFactor 타입
│   │   ├── dispatch.ts               # DispatchStop, DispatchTeam, DispatchResult 타입
│   │   └── naver-maps.d.ts           # Naver Maps SDK 글로벌 타입 선언
│   │
│   ├── constants/
│   │   ├── risk.ts                   # 위험도 색상/라벨/목록 상수
│   │   └── teamColors.ts             # 팀 색상 팔레트
│   │
│   ├── utils/
│   │   ├── time.ts                   # durationLabel, minutesToTimeLabel, nowTimeLabel
│   │   ├── routeMetrics.ts           # formatDistance, formatDurationFromMs
│   │   └── mapTooltip.ts             # 마커 호버 툴팁 HTML 생성
│   │
│   ├── data/
│   │   └── mockFarms.ts              # 경기도 20개 농장 목업 데이터
│   │
│   └── theme/
│       └── theme.ts                  # MUI 커스텀 테마
│
├── backend/
│   ├── main.py                       # FastAPI 앱, CORS 설정, 라우터 등록
│   ├── requirements.txt              # Python 패키지 목록
│   ├── .env.example                  # 환경변수 예시
│   ├── routers/
│   │   ├── farms.py                  # GET /api/farms
│   │   └── directions.py             # POST /api/directions/multi (Naver Directions 5 프록시)
│   └── services/
│       └── databricks_client.py      # Databricks 연결 준비 + 더미 농장 데이터 반환
│
├── .env                              # 환경변수 (VITE_NAVER_MAP_CLIENT_ID, VITE_API_BASE_URL)
├── vite.config.ts
├── tsconfig.json
└── structure.md                      # 이 파일
```

## 핵심 데이터 흐름

```
[mockFarms / 백엔드 API]
        ↓
  useFarmStore (farms, selectedFarmId)
        ↓
  MapPage → NaverMap (마커 렌더링)
        ↓ 농장 클릭
  FarmDetailPanel (XAI 요인, 위험도)

[DispatchPage 흐름]
  DispatchSettingsView
    팀 수 + 농장 선택 → runDispatch()
        ↓
  useDispatchStore.result (DispatchResult)
        ↓
  DispatchResultView
    → RouteMap (팀 색상 폴리라인)
    → TeamSummaryCard × N
    → UnassignedFarmsCard
    → confirmDispatch() → /confirmed

[ConfirmedRoutePage 흐름]
  useDispatchStore.liveTeams (DispatchTeam[])
        ↓
  useTeamRoutes → /api/directions/multi (Naver Directions 5)
        ↓
  RouteMap + LiveTeamCard × N
  advanceLiveProgress() → 수동 진행도 업데이트
```

## 배치 알고리즘 (현재)

위치: `useDispatchStore.ts` → `buildDispatchResult()`

1. 선택된 농장을 `riskScore` 내림차순 정렬
2. 각 농장을 `totalDurationMinutes`가 가장 낮은 팀에 배정 (greedy)
3. 팀 용량(`TEAM_CAPACITY_MINUTES = 240분`) 초과 시 `unassignedFarms`로 분류
4. 방문 순서 = 배정된 순서 그대로 (지리적 최적화 없음)

## 환경변수

| 변수명 | 위치 | 용도 |
|--------|------|------|
| `VITE_NAVER_MAP_CLIENT_ID` | `.env` (프론트) | Naver Maps SDK 클라이언트 ID |
| `VITE_API_BASE_URL` | `.env` (프론트) | 백엔드 API 주소 (기본: `http://localhost:8000`) |
| `DATABRICKS_HOST` | `backend/.env` | Databricks SQL Warehouse 호스트 |
| `DATABRICKS_HTTP_PATH` | `backend/.env` | Databricks HTTP Path |
| `DATABRICKS_TOKEN` | `backend/.env` | Databricks 액세스 토큰 |

## 미연동/미구현 항목

- `useFarmStore`: 백엔드 `/api/farms` 미연동, `mockFarms` 하드코딩
- `databricks_client.py`: 실제 Databricks 쿼리 미구현, 더미 6개 농장 반환
- 배치 알고리즘: 지리적 클러스터링/경로 순서 최적화 없음
- 상태 persistence: 새로고침 시 배치 결과·확정 경로 초기화
- 실시간 갱신: 수동 버튼 클릭 방식, 자동 폴링 없음
