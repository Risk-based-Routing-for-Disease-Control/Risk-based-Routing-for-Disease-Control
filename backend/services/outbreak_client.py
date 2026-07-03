"""가축전염병 발생 로그 수집 Azure Function 호출 wrapper."""

import os
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx


class OutbreakLogsError(Exception):
    """발생 로그 수집 API 호출 중 발생한 오류."""


def _today_kst() -> str:
    return datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y%m%d")


async def fetch_outbreak_logs(date: str | None = None) -> dict:
    """발생 로그 수집 Azure Function을 호출해 지정 날짜(기본: 오늘, KST)의 발생 로그를 조회한다.

    OUTBREAK_LOGS_FUNCTION_URL, OUTBREAK_LOGS_FUNCTION_KEY 환경변수가 필요하다.
    """
    base_url = os.getenv("OUTBREAK_LOGS_FUNCTION_URL")
    function_key = os.getenv("OUTBREAK_LOGS_FUNCTION_KEY")
    if not base_url or not function_key:
        raise OutbreakLogsError(
            "OUTBREAK_LOGS_FUNCTION_URL / OUTBREAK_LOGS_FUNCTION_KEY 환경변수가 설정되지 않았습니다. "
            "backend/.env 파일을 확인하세요."
        )

    target_date = date or _today_kst()
    headers = {"x-functions-key": function_key}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(base_url, params={"date": target_date}, headers=headers)
    except httpx.TimeoutException as exc:
        raise OutbreakLogsError("발생 로그 API 요청이 시간 초과되었습니다.") from exc
    except httpx.RequestError as exc:
        raise OutbreakLogsError(f"발생 로그 API 요청 중 네트워크 오류가 발생했습니다: {exc}") from exc

    if response.status_code != 200:
        raise OutbreakLogsError(f"발생 로그 API 오류 응답 (status={response.status_code}): {response.text}")

    return response.json()
