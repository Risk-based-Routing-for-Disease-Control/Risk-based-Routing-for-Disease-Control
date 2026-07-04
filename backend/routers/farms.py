from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.databricks_client import get_farms_from_db, get_farms_with_status
from services.db import get_cursor

router = APIRouter(tags=["farms"])

_RISK_LEVEL_MAP = {"critical": "HIGH", "high": "MEDIUM", "warning": "LOW"}
_VALID_RISK_LEVELS = {"HIGH", "MEDIUM", "LOW"}


def _normalize_risk_level(raw: str) -> str:
    """더미 데이터(critical/high/warning)와 DB 데이터(HIGH/MEDIUM/LOW)를 모두 처리한다."""
    if raw in _VALID_RISK_LEVELS:
        return raw
    return _RISK_LEVEL_MAP.get(raw, "LOW")

_FARM_DETAILS: dict[str, dict] = {
    "farm-001": {
        "farmCode": "FARM-2024-000001",
        "address": "경기도 남양주시 진접읍 부평리 123-4",
        "livestockType": "한우",
        "livestockCount": 120,
        "livestockUnit": "두",
        "estimatedDurationMinutes": 45,
        "modelVersion": "v1.2.0",
        "riskDate": "2026-06-28",
        "riskFactors": [
            {"factorCode": "MIGRATORY_BIRD", "label": "철새 도래지 근접", "icon": "bird", "weight": 0.32},
            {"factorCode": "RISK_VEHICLE", "label": "위험 차량 방문", "icon": "truck", "weight": 0.21},
        ],
        "lastUpdated": "2026-06-28T14:30:00+09:00",
    },
    "farm-002": {
        "farmCode": "FARM-2024-000002",
        "address": "경기도 의정부시 가능동 산 12-3",
        "livestockType": "돼지",
        "livestockCount": 850,
        "livestockUnit": "두",
        "estimatedDurationMinutes": 60,
        "modelVersion": "v1.2.0",
        "riskDate": "2026-06-28",
        "riskFactors": [
            {"factorCode": "HIGH_DENSITY", "label": "고밀도 사육", "icon": "pig", "weight": 0.41},
            {"factorCode": "RISK_VEHICLE", "label": "위험 차량 방문", "icon": "truck", "weight": 0.27},
        ],
        "lastUpdated": "2026-06-28T14:30:00+09:00",
    },
    "farm-003": {
        "farmCode": "FARM-2024-000003",
        "address": "경기도 광주시 초월읍 용수리 56-7",
        "livestockType": "육계",
        "livestockCount": 30000,
        "livestockUnit": "마리",
        "estimatedDurationMinutes": 50,
        "modelVersion": "v1.2.0",
        "riskDate": "2026-06-28",
        "riskFactors": [
            {"factorCode": "MIGRATORY_BIRD", "label": "철새 도래지 근접", "icon": "bird", "weight": 0.38},
            {"factorCode": "HIGH_DENSITY", "label": "고밀도 사육", "icon": "bird", "weight": 0.29},
        ],
        "lastUpdated": "2026-06-28T14:30:00+09:00",
    },
    "farm-004": {
        "farmCode": "FARM-2024-000004",
        "address": "경기도 양주시 은현면 선암리 89-1",
        "livestockType": "한우",
        "livestockCount": 65,
        "livestockUnit": "두",
        "estimatedDurationMinutes": 35,
        "modelVersion": "v1.2.0",
        "riskDate": "2026-06-28",
        "riskFactors": [
            {"factorCode": "NEARBY_OUTBREAK", "label": "인근 발생 농장 존재", "icon": "warning", "weight": 0.35},
        ],
        "lastUpdated": "2026-06-28T14:30:00+09:00",
    },
    "farm-005": {
        "farmCode": "FARM-2024-000005",
        "address": "경기도 고양시 덕양구 원신동 234-5",
        "livestockType": "젖소",
        "livestockCount": 90,
        "livestockUnit": "두",
        "estimatedDurationMinutes": 40,
        "modelVersion": "v1.2.0",
        "riskDate": "2026-06-28",
        "riskFactors": [
            {"factorCode": "RISK_VEHICLE", "label": "위험 차량 방문", "icon": "truck", "weight": 0.22},
        ],
        "lastUpdated": "2026-06-28T14:30:00+09:00",
    },
    "farm-006": {
        "farmCode": "FARM-2024-000006",
        "address": "경기도 파주시 적성면 구읍리 310-2",
        "livestockType": "한우",
        "livestockCount": 40,
        "livestockUnit": "두",
        "estimatedDurationMinutes": 30,
        "modelVersion": "v1.2.0",
        "riskDate": "2026-06-28",
        "riskFactors": [],
        "lastUpdated": "2026-06-28T14:30:00+09:00",
    },
}


@router.get("/farms")
def list_farms():
    """농장 목록을 리턴한다.

    DB 조회가 실패하거나 비어있으면 더미 데이터로 폴백하되,
    source/error 필드로 폴백 여부를 프론트가 알 수 있게 한다.
    """
    farms, source, error = get_farms_with_status()
    return {"farms": farms, "source": source, "error": error}


@router.get("/farms/{farm_id}")
def get_farm(farm_id: str):
    """농장 상세 정보를 리턴한다."""
    farms = get_farms_from_db()
    base = next((f for f in farms if str(f.get("id")) == farm_id), None)
    if base is None:
        raise HTTPException(status_code=404, detail=f"농장을 찾을 수 없습니다: {farm_id}")

    detail = _FARM_DETAILS.get(farm_id, {})
    return {
        "farmId": base["id"],
        "farmName": base["name"],
        "lat": base["lat"],
        "lng": base["lng"],
        "riskScore": round(float(base["riskScore"]) * 100, 1),
        "riskScoreId": base.get("riskScoreId"),
        "riskLevel": _normalize_risk_level(str(base["riskLevel"])),
        "xaiFactors": base.get("xaiFactors", []),
        **detail,
    }


class SuspectedFarmRequest(BaseModel):
    suspected: bool


@router.patch("/farms/{farm_id}/suspected")
def set_suspected_farm(farm_id: str, request: SuspectedFarmRequest):
    """비상모드 중 담당자가 지정/해제하는 의심 농장 플래그를 반영한다."""
    with get_cursor() as cur:
        cur.execute(
            "UPDATE farms SET suspected_farm = %s WHERE farm_id = %s RETURNING farm_id, suspected_farm",
            (request.suspected, farm_id),
        )
        row = cur.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"농장을 찾을 수 없습니다: {farm_id}")
    return {"farmId": row["farm_id"], "suspectedFarm": row["suspected_farm"]}
