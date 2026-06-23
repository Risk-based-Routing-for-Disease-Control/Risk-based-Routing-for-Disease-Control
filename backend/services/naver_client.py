"""네이버 클라우드 플랫폼 Directions 5 API 호출 wrapper."""

import os
from typing import Any

import httpx

NAVER_DIRECTIONS_URL = "https://maps.apigw.ntruss.com/map-direction/v1/driving"


class NaverDirectionsError(Exception):
    """네이버 Directions API 호출 중 발생한 오류."""


async def get_route(start: str, goal: str, waypoints: str | None = None) -> dict[str, Any]:
    """네이버 Directions 5 API로 자동차 경로를 조회한다.

    Args:
        start: "경도,위도" 형식 문자열
        goal: "경도,위도" 형식 문자열
        waypoints: "경도,위도:경도,위도" 형식의 경유지 문자열 (선택, 최대 5개)

    Returns:
        {"path": [[lng, lat], ...], "distance": 미터, "duration": 밀리초}
    """
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise NaverDirectionsError(
            "NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 환경변수가 설정되지 않았습니다. "
            "backend/.env 파일을 확인하세요."
        )

    params: dict[str, str] = {"start": start, "goal": goal, "option": "trafast"}
    if waypoints:
        params["waypoints"] = waypoints

    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(NAVER_DIRECTIONS_URL, params=params, headers=headers)
    except httpx.TimeoutException as exc:
        raise NaverDirectionsError("네이버 Directions API 요청이 시간 초과되었습니다.") from exc
    except httpx.RequestError as exc:
        raise NaverDirectionsError(f"네이버 Directions API 요청 중 네트워크 오류가 발생했습니다: {exc}") from exc

    if response.status_code != 200:
        raise NaverDirectionsError(
            f"네이버 Directions API 오류 응답 (status={response.status_code}): {response.text}"
        )

    payload = response.json()
    code = payload.get("code")
    if code != 0:
        message = payload.get("message", "알 수 없는 오류")
        raise NaverDirectionsError(f"네이버 Directions API 오류 (code={code}): {message}")

    try:
        route = payload["route"]
        route_key = "trafast" if "trafast" in route else next(iter(route))
        summary_route = route[route_key][0]
        path = summary_route["path"]
        summary = summary_route["summary"]
        distance = summary["distance"]
        duration = summary["duration"]
    except (KeyError, IndexError, StopIteration) as exc:
        raise NaverDirectionsError(f"네이버 Directions API 응답 형식이 예상과 다릅니다: {payload}") from exc

    return {"path": path, "distance": distance, "duration": duration}


async def get_multi_stop_route(points: list[dict[str, Any]]) -> dict[str, Any]:
    """여러 지점을 순서대로 방문하는 경로를 구간(레그)별로 계산한다.

    네이버 Directions API는 waypoints를 한 번에 넣어도 구간별 거리/시간을 따로 주지
    않고 전체 합산 summary만 준다. 그래서 인접한 두 지점씩 끊어 get_route()를 순차
    호출(레이트 리밋 고려, asyncio.gather 사용하지 않음)하고 결과를 합산한다.

    Args:
        points: 방문 순서대로 정렬된 좌표 리스트. 각 항목은
            {"lat": float, "lng": float, "name": str (선택)} 형태.

    Returns:
        {
            "totalDistance": float,  # 전체 합산 거리(m)
            "totalDuration": float,  # 전체 합산 시간(get_route와 동일 단위, 밀리초)
            "legs": [
                {
                    "from": {"lat": .., "lng": .., "name": ..},
                    "to": {"lat": .., "lng": .., "name": ..},
                    "distance": float,
                    "duration": float,
                    "path": [{"lat": .., "lng": ..}, ...],
                },
                ...
            ],
        }

    Raises:
        ValueError: points가 2개 미만인 경우
        NaverDirectionsError: 구간 계산 중 하나라도 실패한 경우. 메시지에 몇 번째
            구간, 어느 지점에서 실패했는지 포함한다.
    """
    if len(points) < 2:
        raise ValueError("points는 최소 2개 이상이어야 합니다.")

    legs: list[dict[str, Any]] = []
    total_distance = 0.0
    total_duration = 0.0

    for index in range(len(points) - 1):
        origin = points[index]
        destination = points[index + 1]
        origin_label = origin.get("name") or f"지점 {index + 1}"
        destination_label = destination.get("name") or f"지점 {index + 2}"

        try:
            result = await get_route(
                start=f"{origin['lng']},{origin['lat']}",
                goal=f"{destination['lng']},{destination['lat']}",
            )
        except NaverDirectionsError as exc:
            raise NaverDirectionsError(
                f"{index + 1}번째 구간({origin_label} → {destination_label}) "
                f"경로 계산에 실패했습니다: {exc}"
            ) from exc

        leg_distance = result["distance"]
        leg_duration = result["duration"]

        legs.append(
            {
                "from": {"lat": origin["lat"], "lng": origin["lng"], "name": origin.get("name")},
                "to": {"lat": destination["lat"], "lng": destination["lng"], "name": destination.get("name")},
                "distance": leg_distance,
                "duration": leg_duration,
                "path": [{"lat": point[1], "lng": point[0]} for point in result["path"]],
            }
        )
        total_distance += leg_distance
        total_duration += leg_duration

    return {"totalDistance": total_distance, "totalDuration": total_duration, "legs": legs}
