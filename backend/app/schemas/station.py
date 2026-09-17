"""Station schemas."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class StationBase(BaseModel):
    station_id: str = Field(..., description="Unique canonical station ID")
    station_name: str = Field(..., description="Canonical station name")
    state: str = Field(..., description="State name")
    district: str = Field(..., description="District name")
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    elevation_m: float = Field(..., description="Elevation in meters")


class StationDetail(StationBase):
    record_count: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class StationListResponse(BaseModel):
    total_stations: int = 413
    stations: List[StationBase]


class DistrictHierarchyResponse(BaseModel):
    states: Dict[str, Dict[str, List[StationBase]]]
