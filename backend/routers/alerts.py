from typing import Any

from fastapi import APIRouter

from services.outbreak_client import OutbreakLogsError, fetch_outbreak_logs

router = APIRouter(tags=["alerts"])


def _extract_cases(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """items[].new_items[]를 평탄화해 화면에 필요한 필드만 추린다."""
    cases: list[dict[str, Any]] = []
    for item in items:
        item_is_test = bool(item.get("is_test"))
        for new_item in item.get("new_items", []):
            farm_id = new_item.get("farm_id") or new_item.get("farmId") or new_item.get("id")
            cases.append(
                {
                    "farmId": farm_id,
                    "farmName": new_item.get("farm_name"),
                    "disease": new_item.get("disease"),
                    "region": new_item.get("region"),
                    "confirmedAt": new_item.get("confirmed_at"),
                    "isTest": bool(new_item.get("is_test")) or item_is_test,
                }
            )
    return cases


@router.get("/alerts/outbreaks")
async def get_outbreak_alerts(date: str | None = None):
    """오늘(또는 지정 날짜) 발생 로그 건수와 상세 항목을 조회한다.

    보조 알림 기능이므로 외부 함수 호출이 실패해도 500을 던지지 않고
    ok=False로 응답해 다른 화면에 영향을 주지 않는다.
    """
    try:
        result = await fetch_outbreak_logs(date)
        return {
            "ok": bool(result.get("ok", True)),
            "date": result.get("date"),
            "count": result.get("count", 0),
            "cases": _extract_cases(result.get("items", [])),
        }
    except OutbreakLogsError as exc:
        return {"ok": False, "date": date, "count": 0, "cases": [], "error": str(exc)}
