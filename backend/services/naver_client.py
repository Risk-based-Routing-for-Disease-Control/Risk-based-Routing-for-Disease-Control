"""네이버 클라우드 플랫폼 Directions 5 API 호출 wrapper."""

import asyncio
import os
import time
from collections import OrderedDict
from typing import Any

import httpx

NAVER_DIRECTIONS_URL = "https://maps.apigw.ntruss.com/map-direction/v1/driving"
NAVER_DIRECTIONS_MAX_WAYPOINTS = 5
NAVER_DIRECTIONS_MAX_LEGS_PER_REQUEST = NAVER_DIRECTIONS_MAX_WAYPOINTS + 1
NAVER_DIRECTIONS_CACHE_TTL_SECONDS = int(os.getenv("NAVER_DIRECTIONS_CACHE_TTL_SECONDS", str(6 * 60 * 60)))
NAVER_DIRECTIONS_CACHE_MAX_SIZE = int(os.getenv("NAVER_DIRECTIONS_CACHE_MAX_SIZE", "512"))

# Naver Map API 중 Directions 5를 사용중 (경유지 최대 5개)
# 경유지 15개까지 설정 가능한 Directions 15를 사용하는 경우 링크 변경
# https://maps.apigw.ntruss.com/map-direction-15/v1/driving


class NaverDirectionsError(Exception):
    """네이버 Directions API 호출 중 발생한 오류."""


_route_cache: OrderedDict[tuple[str, str, str | None], tuple[float, dict[str, Any]]] = OrderedDict()
_inflight_requests: dict[tuple[str, str, str | None], asyncio.Task[dict[str, Any]]] = {}
_cache_lock = asyncio.Lock()


def _normalize_coordinate(coordinate: str) -> str:
    lng, lat = coordinate.split(",", maxsplit=1)
    return f"{float(lng):.6f},{float(lat):.6f}"


def _normalize_waypoints(waypoints: str | None) -> str | None:
    if not waypoints:
        return None
    return "|".join(_normalize_coordinate(point) for point in waypoints.split("|") if point)


def _route_cache_key(start: str, goal: str, waypoints: str | None) -> tuple[str, str, str | None]:
    return (_normalize_coordinate(start), _normalize_coordinate(goal), _normalize_waypoints(waypoints))


def _copy_route_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": [point[:] for point in result["path"]],
        "distance": result["distance"],
        "duration": result["duration"],
        "waypoints": [waypoint.copy() for waypoint in result.get("waypoints", [])],
        "goal": result.get("goal", {}).copy() if isinstance(result.get("goal"), dict) else result.get("goal"),
    }


async def _get_cached_route(key: tuple[str, str, str | None]) -> dict[str, Any] | None:
    if NAVER_DIRECTIONS_CACHE_TTL_SECONDS <= 0 or NAVER_DIRECTIONS_CACHE_MAX_SIZE <= 0:
        return None

    now = time.monotonic()
    async with _cache_lock:
        cached = _route_cache.get(key)
        if not cached:
            return None

        expires_at, result = cached
        if expires_at <= now:
            _route_cache.pop(key, None)
            return None

        _route_cache.move_to_end(key)
        return _copy_route_result(result)


async def _set_cached_route(key: tuple[str, str, str | None], result: dict[str, Any]) -> None:
    if NAVER_DIRECTIONS_CACHE_TTL_SECONDS <= 0 or NAVER_DIRECTIONS_CACHE_MAX_SIZE <= 0:
        return

    expires_at = time.monotonic() + NAVER_DIRECTIONS_CACHE_TTL_SECONDS
    async with _cache_lock:
        _route_cache[key] = (expires_at, _copy_route_result(result))
        _route_cache.move_to_end(key)
        while len(_route_cache) > NAVER_DIRECTIONS_CACHE_MAX_SIZE:
            _route_cache.popitem(last=False)


async def get_route(start: str, goal: str, waypoints: str | None = None) -> dict[str, Any]:
    """네이버 Directions 5 API로 자동차 경로를 조회한다.

    Args:
        start: "경도,위도" 형식 문자열
        goal: "경도,위도" 형식 문자열
        waypoints: "경도,위도|경도,위도" 형식의 경유지 문자열 (선택, 최대 5개)

    Returns:
        {"path": [[lng, lat], ...], "distance": 미터, "duration": 밀리초}
    """
    cache_key = _route_cache_key(start, goal, waypoints)
    cached = await _get_cached_route(cache_key)
    if cached is not None:
        return cached

    async with _cache_lock:
        inflight = _inflight_requests.get(cache_key)
        if inflight is None:
            inflight = asyncio.create_task(_fetch_route_from_naver(*cache_key))
            _inflight_requests[cache_key] = inflight

    try:
        result = await asyncio.shield(inflight)
    finally:
        if inflight.done():
            async with _cache_lock:
                if _inflight_requests.get(cache_key) is inflight:
                    _inflight_requests.pop(cache_key, None)

    await _set_cached_route(cache_key, result)
    return _copy_route_result(result)


async def _fetch_route_from_naver(start: str, goal: str, waypoints: str | None = None) -> dict[str, Any]:
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

    return {
        "path": path,
        "distance": distance,
        "duration": duration,
        "waypoints": summary.get("waypoints", []),
        "goal": summary.get("goal"),
    }


def _point_to_naver_coordinate(point: dict[str, Any]) -> str:
    return f"{point['lng']},{point['lat']}"


def _point_to_response(point: dict[str, Any]) -> dict[str, Any]:
    return {"lat": point["lat"], "lng": point["lng"], "name": point.get("name")}


def _path_to_response(path: list[list[float]]) -> list[dict[str, float]]:
    return [{"lat": point[1], "lng": point[0]} for point in path]


def _leg_path(path: list[list[float]], from_index: int, to_index: int) -> list[dict[str, float]]:
    if not path:
        return []
    start = max(0, min(from_index, len(path) - 1))
    end = max(start, min(to_index, len(path) - 1))
    return _path_to_response(path[start : end + 1])


def _leg_summaries_from_result(result: dict[str, Any], expected_leg_count: int) -> list[dict[str, Any]]:
    leg_summaries = [*result.get("waypoints", []), result.get("goal")]
    leg_summaries = [summary for summary in leg_summaries if summary is not None]

    if expected_leg_count == 1 and (
        len(leg_summaries) != 1 or "distance" not in leg_summaries[0] or "duration" not in leg_summaries[0]
    ):
        return [
            {
                "distance": result["distance"],
                "duration": result["duration"],
                "pointIndex": len(result["path"]) - 1,
            }
        ]

    return leg_summaries


async def get_multi_stop_route(points: list[dict[str, Any]]) -> dict[str, Any]:
    """여러 지점을 순서대로 방문하는 경로를 구간(레그)별로 계산한다.

    네이버 Directions 5 API의 경유지 최대 5개 제한에 맞춰 최대 6개 leg씩 묶어
    호출한다. 응답의 summary.waypoints와 summary.goal에 담긴 leg별 거리/시간,
    pointIndex를 이용해 기존 MultiStopRouteResponse 형태로 재구성한다.

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

    for chunk_start in range(0, len(points) - 1, NAVER_DIRECTIONS_MAX_LEGS_PER_REQUEST):
        chunk = points[chunk_start : chunk_start + NAVER_DIRECTIONS_MAX_LEGS_PER_REQUEST + 1]
        origin = chunk[0]
        destination = chunk[-1]
        waypoint_points = chunk[1:-1]
        origin_label = origin.get("name") or f"지점 {chunk_start + 1}"
        destination_label = destination.get("name") or f"지점 {chunk_start + len(chunk)}"
        waypoints = "|".join(_point_to_naver_coordinate(point) for point in waypoint_points) or None

        try:
            result = await get_route(
                start=_point_to_naver_coordinate(origin),
                goal=_point_to_naver_coordinate(destination),
                waypoints=waypoints,
            )
        except NaverDirectionsError as exc:
            raise NaverDirectionsError(
                f"{chunk_start + 1}번째 지점부터 {chunk_start + len(chunk)}번째 지점까지"
                f"({origin_label} → {destination_label}) 경로 계산에 실패했습니다: {exc}"
            ) from exc

        expected_leg_count = len(chunk) - 1
        leg_summaries = _leg_summaries_from_result(result, expected_leg_count)
        if len(leg_summaries) != expected_leg_count:
            raise NaverDirectionsError(
                f"네이버 Directions API 응답의 구간 수가 예상과 다릅니다. "
                f"expected={expected_leg_count}, actual={len(leg_summaries)}"
            )

        path = result["path"]
        previous_point_index = 0
        for offset, summary in enumerate(leg_summaries):
            point_index = int(summary.get("pointIndex", len(path) - 1))
            leg_distance = summary["distance"]
            leg_duration = summary["duration"]
            from_point = chunk[offset]
            to_point = chunk[offset + 1]

            legs.append(
                {
                    "from": _point_to_response(from_point),
                    "to": _point_to_response(to_point),
                    "distance": leg_distance,
                    "duration": leg_duration,
                    "path": _leg_path(path, previous_point_index, point_index),
                }
            )
            total_distance += leg_distance
            total_duration += leg_duration
            previous_point_index = point_index

    return {"totalDistance": total_distance, "totalDuration": total_duration, "legs": legs}
