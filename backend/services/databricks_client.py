"""Databricks SQL 연결 준비. 실제 키가 발급되기 전까지는 더미 데이터를 리턴한다."""

import os
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


_DUMMY_FARMS: list[dict[str, Any]] = [
    {"id": "farm-001", "name": "행복한농장", "lat": 37.619, "lng": 127.181, "riskLevel": "critical", "riskScore": 0.78},
    {"id": "farm-002", "name": "의정부농장", "lat": 37.74, "lng": 127.03, "riskLevel": "critical", "riskScore": 0.81},
    {"id": "farm-003", "name": "광주농장", "lat": 37.432, "lng": 127.255, "riskLevel": "critical", "riskScore": 0.74},
    {"id": "farm-004", "name": "양주농장", "lat": 37.832, "lng": 127.05, "riskLevel": "high", "riskScore": 0.55},
    {"id": "farm-005", "name": "고양농장", "lat": 37.662, "lng": 126.834, "riskLevel": "high", "riskScore": 0.48},
    {"id": "farm-006", "name": "파주농장", "lat": 37.76, "lng": 126.78, "riskLevel": "warning", "riskScore": 0.18},
]


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
                frs.risk_score   AS "riskScore",
                frs.risk_level   AS "riskLevel",
                frs.risk_date    AS "riskDate"
            FROM farms f
            LEFT JOIN LATERAL (
                SELECT risk_score, risk_level, risk_date
                FROM farm_risk_scores
                WHERE farm_id = f.farm_id
                ORDER BY risk_date DESC
                LIMIT 1
            ) frs ON true
        """)
        rows = cur.fetchall()
    return [dict(row) for row in rows]


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
