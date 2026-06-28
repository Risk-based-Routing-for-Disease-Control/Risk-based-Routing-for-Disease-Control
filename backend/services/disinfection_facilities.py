from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path

from services.osrm_client import OsrmPoint


HWASEONG_ADDRESS_PREFIX = "경기도 화성시"


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


def _default_facility_csv_path() -> Path:
    project_root = Path(__file__).resolve().parents[2]
    candidates = [
        path
        for path in project_root.glob("*20260623.csv")
        if "소독" in path.name or "소독" in path.name
    ]
    if not candidates:
        return project_root / "거점소독시설_20260623.csv"
    return candidates[0]


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    last_error: UnicodeDecodeError | None = None
    for encoding in ("utf-8-sig", "cp949"):
        try:
            with path.open(encoding=encoding, newline="") as csv_file:
                return list(csv.DictReader(csv_file))
        except UnicodeDecodeError as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    return []


@lru_cache(maxsize=1)
def load_hwaseong_disinfection_facilities() -> tuple[DisinfectionFacility, ...]:
    csv_path = Path(os.getenv("DISINFECTION_FACILITY_CSV", _default_facility_csv_path()))
    if not csv_path.exists():
        raise FileNotFoundError(f"거점소독시설 CSV를 찾을 수 없습니다: {csv_path}")

    facilities: list[DisinfectionFacility] = []
    for row in _read_csv_rows(csv_path):
        address = (row.get("주소") or "").strip()
        if HWASEONG_ADDRESS_PREFIX not in address:
            continue
        lat_value = (row.get("위도") or "").strip()
        lng_value = (row.get("경도") or "").strip()
        if not lat_value or not lng_value:
            continue
        facilities.append(
            DisinfectionFacility(
                id=f"disinfection-{(row.get('거점소독장소순번') or '').strip()}",
                name=(row.get("거점소독장소명") or "거점소독시설").strip(),
                address=address,
                operating_hours=(row.get("운영시간") or "").strip(),
                phone=(row.get("담당자_전화번호") or "").strip(),
                lat=float(lat_value),
                lng=float(lng_value),
            )
        )

    if not facilities:
        raise ValueError(f"화성시 거점소독시설을 찾지 못했습니다: {csv_path}")
    return tuple(facilities)


def nearest_disinfection_facility(lat: float, lng: float) -> DisinfectionFacility:
    facilities = load_hwaseong_disinfection_facilities()
    return min(facilities, key=lambda facility: (facility.lat - lat) ** 2 + (facility.lng - lng) ** 2)

