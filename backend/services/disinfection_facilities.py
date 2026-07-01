from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from services.db import get_cursor
from services.osrm_client import OsrmPoint


@dataclass(frozen=True)
class DisinfectionFacility:
    id: str
    name: str
    address: str
    lat: float
    lng: float
    operating_hours: str = ""
    phone: str = ""

    @property
    def point(self) -> OsrmPoint:
        return OsrmPoint(lat=self.lat, lng=self.lng)


@lru_cache(maxsize=1)
def load_disinfection_facilities() -> tuple[DisinfectionFacility, ...]:
    with get_cursor() as cur:
        cur.execute(
            "SELECT facility_id, name, address, lat, lng, operating_hours, phone "
            "FROM disinfection_facilities ORDER BY facility_id"
        )
        rows = cur.fetchall()
    return tuple(
        DisinfectionFacility(
            id=r["facility_id"],
            name=r["name"],
            address=r["address"] or "",
            lat=float(r["lat"]),
            lng=float(r["lng"]),
            operating_hours=r["operating_hours"] or "",
            phone=r["phone"] or "",
        )
        for r in rows
    )


def nearest_disinfection_facility(lat: float, lng: float) -> DisinfectionFacility:
    facilities = load_disinfection_facilities()
    return min(facilities, key=lambda facility: (facility.lat - lat) ** 2 + (facility.lng - lng) ** 2)
