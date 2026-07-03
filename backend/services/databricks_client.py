"""Databricks SQL 연결 준비. 실제 키가 발급되기 전까지는 더미 데이터를 리턴한다."""

import os
from collections import defaultdict
from decimal import Decimal
from typing import Any


def get_connection():
    """Databricks SQL Warehouse 커넥션을 생성한다.

    DATABRICKS_HOST, DATABRICKS_HTTP_PATH, DATABRICKS_TOKEN 환경변수가 필요하다.
    아직 실제 쿼리에서는 사용하지 않고, 연결 준비 용도로만 존재한다.
    """
    host = os.getenv("DATABRICKS_HOST")
    http_path = os.getenv("DATABRICKS_HTTP_PATH")
    token = os.getenv("DATABRICKS_TOKEN")

    missing = [
        name
        for name, value in (
            ("DATABRICKS_HOST", host),
            ("DATABRICKS_HTTP_PATH", http_path),
            ("DATABRICKS_TOKEN", token),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(
            "Databricks 연결에 필요한 환경변수가 설정되지 않았습니다: "
            f"{', '.join(missing)}. backend/.env 파일에 값을 채운 뒤 다시 시도하세요."
        )

    from databricks import sql

    return sql.connect(server_hostname=host, http_path=http_path, access_token=token)


_DUMMY_XAI_FACTORS: list[list[dict[str, Any]]] = [
    [
        {
            "id": "dummy-xai-001-bird",
            "factorCode": "bird_obs_count_30d_10km",
            "label": "최근 30일 반경 10km 내 철새 관측 증가",
            "icon": "/xai-icons/bird.png",
            "weight": 0.42,
        },
        {
            "id": "dummy-xai-001-virus",
            "factorCode": "infected_farm_count_3km",
            "label": "반경 3km 내 감염농장 증가",
            "icon": "/xai-icons/virus.png",
            "weight": 0.31,
        },
        {
            "id": "dummy-xai-001-wetland",
            "factorCode": "within_migratory_bird_site_10km",
            "label": "철새도래지 10km 이내 위치",
            "icon": "/xai-icons/wetland.png",
            "weight": 0.24,
        },
    ],
    [
        {
            "id": "dummy-xai-002-duck",
            "factorCode": "duck_obs_count_30d_5km",
            "label": "최근 30일 반경 5km 내 오리류 관측 증가",
            "icon": "/xai-icons/duck.png",
            "weight": 0.38,
        },
        {
            "id": "dummy-xai-002-humidity",
            "factorCode": "humidity",
            "label": "습도 증가",
            "icon": "/xai-icons/humidity.png",
            "weight": 0.28,
        },
        {
            "id": "dummy-xai-002-rain",
            "factorCode": "precipitation_7d",
            "label": "최근 7일 강수량 증가",
            "icon": "/xai-icons/rain.png",
            "weight": 0.21,
        },
    ],
    [
        {
            "id": "dummy-xai-003-chicken",
            "factorCode": "poultry_species_0",
            "label": "닭 농장 여부",
            "icon": "/xai-icons/chicken.png",
            "weight": 0.36,
        },
        {
            "id": "dummy-xai-003-flock",
            "factorCode": "flock_size",
            "label": "농장 사육 규모",
            "icon": "/xai-icons/chicken.png",
            "weight": 0.27,
        },
        {
            "id": "dummy-xai-003-wind",
            "factorCode": "wind_speed_avg_7d",
            "label": "최근 7일 평균 풍속 영향",
            "icon": "/xai-icons/wind.png",
            "weight": 0.18,
        },
    ],
]


_DUMMY_FARMS: list[dict[str, Any]] = [
    {
        "id": "farm-001",
        "name": "행복한농장",
        "lat": 37.619,
        "lng": 127.181,
        "riskLevel": "critical",
        "riskScore": 0.78,
        "xaiFactors": _DUMMY_XAI_FACTORS[0],
    },
    {
        "id": "farm-002",
        "name": "의정부농장",
        "lat": 37.74,
        "lng": 127.03,
        "riskLevel": "critical",
        "riskScore": 0.81,
        "xaiFactors": _DUMMY_XAI_FACTORS[1],
    },
    {
        "id": "farm-003",
        "name": "광주농장",
        "lat": 37.432,
        "lng": 127.255,
        "riskLevel": "critical",
        "riskScore": 0.74,
        "xaiFactors": _DUMMY_XAI_FACTORS[2],
    },
    {
        "id": "farm-004",
        "name": "양주농장",
        "lat": 37.832,
        "lng": 127.05,
        "riskLevel": "high",
        "riskScore": 0.55,
        "xaiFactors": _DUMMY_XAI_FACTORS[0],
    },
    {
        "id": "farm-005",
        "name": "고양농장",
        "lat": 37.662,
        "lng": 126.834,
        "riskLevel": "high",
        "riskScore": 0.48,
        "xaiFactors": _DUMMY_XAI_FACTORS[1],
    },
    {
        "id": "farm-006",
        "name": "파주농장",
        "lat": 37.76,
        "lng": 126.78,
        "riskLevel": "warning",
        "riskScore": 0.18,
        "xaiFactors": _DUMMY_XAI_FACTORS[2],
    },
]


def _icon_path(icon: str | None) -> str:
    filename = (icon or "poultry.png").strip()
    return filename if filename.startswith("/") else f"/xai-icons/{filename}"


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _query_xai_factors_by_risk_score_ids(risk_score_ids: list[int]) -> dict[int, list[dict[str, Any]]]:
    if not risk_score_ids:
        return {}

    from services.db import get_cursor

    with get_cursor() as cur:
        cur.execute(
            """
            SELECT
                risk_score_id,
                xai_factor_id AS id,
                factor_code AS "factorCode",
                label,
                icon,
                weight
            FROM farm_xai_factors
            WHERE risk_score_id = ANY(%s)
            ORDER BY risk_score_id, weight DESC, created_at DESC
            """,
            (risk_score_ids,),
        )
        rows = cur.fetchall()

    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        risk_score_id = row.get("risk_score_id")
        if risk_score_id is None or len(grouped[int(risk_score_id)]) >= 3:
            continue
        grouped[int(risk_score_id)].append(
            {
                "id": str(row["id"]),
                "factorCode": row.get("factorCode") or "",
                "label": row.get("label") or row.get("factorCode") or "위험 요인",
                "icon": _icon_path(row.get("icon")),
                "weight": _to_float(row.get("weight")),
            }
        )

    return dict(grouped)


def _query_farms_from_postgres() -> list[dict[str, Any]]:
    from services.db import get_cursor
    with get_cursor() as cur:
        cur.execute("""
            SELECT
                f.farm_id                     AS id,
                f.farm_code                   AS "farmCode",
                f.name,
                f.address,
                f.lat,
                f.lng,
                f.livestock_type              AS "livestockType",
                f.livestock_count             AS "livestockCount",
                f.livestock_unit              AS "livestockUnit",
                f.estimated_duration_minutes  AS "estimatedDurationMinutes",
                frs.risk_score_id AS "riskScoreId",
                frs.risk_score   AS "riskScore",
                frs.risk_level   AS "riskLevel",
                frs.risk_date    AS "riskDate"
            FROM farms f
            LEFT JOIN LATERAL (
                SELECT risk_score_id, risk_score, risk_level, risk_date
                FROM farm_risk_scores
                WHERE farm_id = f.farm_id
                ORDER BY risk_date DESC
                LIMIT 1
            ) frs ON true
        """)
        rows = cur.fetchall()

    farms = [dict(row) for row in rows]
    risk_score_ids = [
        int(farm["riskScoreId"])
        for farm in farms
        if farm.get("riskScoreId") is not None
    ]
    xai_factors_by_risk_score_id = _query_xai_factors_by_risk_score_ids(risk_score_ids)

    for farm in farms:
        risk_score_id = farm.get("riskScoreId")
        farm["xaiFactors"] = (
            xai_factors_by_risk_score_id.get(int(risk_score_id), [])
            if risk_score_id is not None
            else []
        )

    return farms


def get_farms_from_db() -> list[dict[str, Any]]:
    """농장 목록을 조회한다.

    PostgreSQL farms 테이블에 데이터가 있으면 DB값을 반환하고,
    비어있거나 오류 시 더미 데이터를 fallback으로 반환한다.
    배차 실행 등 내부 로직에서 조회 실패 원인을 신경 쓸 필요가 없는
    경우에 사용한다. 화면에 폴백 여부를 알려야 하는 경우에는
    get_farms_with_status()를 사용할 것.
    """
    try:
        rows = _query_farms_from_postgres()
        if rows:
            return rows
    except Exception:
        pass
    return _DUMMY_FARMS


def get_farms_with_status() -> tuple[list[dict[str, Any]], str, str | None]:
    """농장 목록과 함께 실제 DB 조회 성공 여부를 반환한다.

    (farms, source, error) 튜플을 반환하며 source는 "db" 또는 "dummy".
    DB 조회가 실패하거나 비어있을 때 화면에서 폴백 여부를 알 수 있도록
    원인을 숨기지 않는다.
    """
    try:
        rows = _query_farms_from_postgres()
    except Exception as exc:
        return _DUMMY_FARMS, "dummy", str(exc)
    if rows:
        return rows, "db", None
    return _DUMMY_FARMS, "dummy", "DB에 farms 데이터가 없습니다."
