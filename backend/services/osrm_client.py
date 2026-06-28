from __future__ import annotations

import math
import os
from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class OsrmPoint:
    lat: float
    lng: float


def _haversine_minutes(a: OsrmPoint, b: OsrmPoint) -> int:
    radius_km = 6371.0088
    p1, p2 = math.radians(a.lat), math.radians(b.lat)
    dp, dl = math.radians(b.lat - a.lat), math.radians(b.lng - a.lng)
    value = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    km = radius_km * 2 * math.asin(math.sqrt(value))
    return max(1, int(round(km / 35.0 * 60)))


def fallback_duration_matrix(points: list[OsrmPoint]) -> list[list[int]]:
    return [
        [0 if i == j else _haversine_minutes(source, target) for j, target in enumerate(points)]
        for i, source in enumerate(points)
    ]


async def build_osrm_duration_matrix(points: list[OsrmPoint]) -> list[list[int]]:
    """Return an OSRM driving duration matrix in minutes.

    OSRM is the authoritative source for optimization travel times. The local
    fallback only keeps development usable when the public OSRM endpoint is not
    reachable from the running environment.
    """
    if len(points) <= 1:
        return [[0 for _ in points] for _ in points]

    base_url = os.getenv("OSRM_BASE_URL", "https://router.project-osrm.org").rstrip("/")
    coordinates = ";".join(f"{point.lng:.6f},{point.lat:.6f}" for point in points)
    url = f"{base_url}/table/v1/driving/{coordinates}"

    try:
        async with httpx.AsyncClient(timeout=float(os.getenv("OSRM_TIMEOUT_SECONDS", "12"))) as client:
            response = await client.get(url, params={"annotations": "duration"})
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError):
        return fallback_duration_matrix(points)

    durations = payload.get("durations")
    if not isinstance(durations, list):
        return fallback_duration_matrix(points)

    fallback = fallback_duration_matrix(points)
    matrix: list[list[int]] = []
    for row_index, row in enumerate(durations):
        matrix_row: list[int] = []
        for col_index, seconds in enumerate(row):
            if row_index == col_index:
                matrix_row.append(0)
            elif seconds is None:
                matrix_row.append(fallback[row_index][col_index])
            else:
                matrix_row.append(max(1, int(round(float(seconds) / 60))))
        matrix.append(matrix_row)
    return matrix


async def snap_points_to_osrm(points: list[OsrmPoint]) -> list[OsrmPoint]:
    base_url = os.getenv("OSRM_BASE_URL", "https://router.project-osrm.org").rstrip("/")
    snapped: list[OsrmPoint] = []

    try:
        async with httpx.AsyncClient(timeout=float(os.getenv("OSRM_TIMEOUT_SECONDS", "12"))) as client:
            for point in points:
                url = f"{base_url}/nearest/v1/driving/{point.lng:.6f},{point.lat:.6f}"
                response = await client.get(url, params={"number": 1})
                response.raise_for_status()
                payload = response.json()
                waypoint = payload.get("waypoints", [{}])[0]
                location = waypoint.get("location")
                if isinstance(location, list) and len(location) == 2:
                    snapped.append(OsrmPoint(lat=float(location[1]), lng=float(location[0])))
                else:
                    snapped.append(point)
    except (httpx.HTTPError, ValueError, IndexError, TypeError):
        return points

    return snapped
