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


def get_farms_from_db() -> list[dict[str, Any]]:
    """농장 목록을 조회한다.

    TODO: 여기를 실제 Databricks 쿼리로 교체
        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, lat, lng, risk_level, risk_score FROM farms"
            )
            rows = cursor.fetchall()
        return [dict(zip([c[0] for c in cursor.description], row)) for row in rows]
    """
    return _DUMMY_FARMS
