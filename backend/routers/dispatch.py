from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.databricks_client import get_farms_from_db
from services.dispatch_optimizer import DispatchOptions, farm_from_dict, solve_dispatch

router = APIRouter(tags=["dispatch"])


class DispatchSolveRequest(BaseModel):
    selectedFarmIds: list[str] = Field(default_factory=list)
    teamCount: int = Field(3, ge=1)
    farms: list[dict[str, Any]] | None = None
    depotName: str | None = None
    depotLat: float | None = None
    depotLng: float | None = None


@router.post("/dispatch/solve")
async def solve_dispatch_route(request: DispatchSolveRequest):
    source_farms = request.farms if request.farms is not None else get_farms_from_db()
    selected_ids = set(request.selectedFarmIds)
    selected = [
        farm_from_dict(farm)
        for farm in source_farms
        if not selected_ids or str(farm.get("id")) in selected_ids
    ]

    try:
        options_kwargs: dict[str, Any] = {"team_count": request.teamCount}
        if request.depotName is not None:
            options_kwargs["depot_name"] = request.depotName
        if request.depotLat is not None:
            options_kwargs["depot_lat"] = request.depotLat
        if request.depotLng is not None:
            options_kwargs["depot_lng"] = request.depotLng
        return await solve_dispatch(selected, DispatchOptions(**options_kwargs))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
