"""Stations router."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from backend.app.schemas.station import StationBase, StationListResponse
from backend.app.services.data_service import (
    load_stations,
    get_station_by_id,
    get_geographic_hierarchy,
)

router = APIRouter(prefix="/stations", tags=["Stations"])


@router.get("", response_model=StationListResponse)
def list_stations(state: Optional[str] = None, district: Optional[str] = None):
    """Lists all 413 canonical monitoring stations, optionally filtered by state or district."""
    stations = load_stations()
    filtered = stations
    if state:
        filtered = [s for s in filtered if s["state"].lower() == state.lower()]
    if district:
        filtered = [s for s in filtered if s["district"].lower() == district.lower()]
    return {
        "total_stations": len(filtered),
        "stations": filtered,
    }


@router.get("/hierarchy")
def get_hierarchy():
    """Returns State -> District -> Stations hierarchy for cascading dropdowns."""
    return get_geographic_hierarchy()


@router.get("/{station_id}", response_model=StationBase)
def get_station(station_id: str):
    """Gets details for a specific canonical station ID."""
    stn = get_station_by_id(station_id)
    if not stn:
        raise HTTPException(
            status_code=404,
            detail=f"Station '{station_id}' not found in the 413 canonical station registry.",
        )
    return stn
