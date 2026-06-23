from fastapi import APIRouter

from services.databricks_client import get_farms_from_db

router = APIRouter(tags=["farms"])


@router.get("/farms")
def list_farms():
    """농장 목록을 리턴한다. 현재는 더미 데이터, 추후 Databricks 쿼리로 교체."""
    return get_farms_from_db()
