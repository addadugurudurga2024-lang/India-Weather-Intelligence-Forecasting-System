"""Historical Analytics schemas."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class AnalyticsSummary(BaseModel):
    station_id: str
    station_name: str
    record_count: int
    date_range: Dict[str, str]
    temp_avg_mean: Optional[float] = None
    temp_min_record: Optional[float] = None
    temp_max_record: Optional[float] = None
    annual_rainfall_mean_mm: Optional[float] = None
    max_single_day_rain_mm: Optional[float] = None
    wind_speed_mean_kmh: Optional[float] = None
    air_pressure_mean_hpa: Optional[float] = None


class TimeSeriesPoint(BaseModel):
    date: str
    temp_avg: Optional[float] = None
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    rainfall: Optional[float] = None
    wind_speed: Optional[float] = None
    air_pressure: Optional[float] = None


class HistoricalTimeSeriesResponse(BaseModel):
    station_id: str
    total_points: int
    data: List[TimeSeriesPoint]


class ScopedObservationItem(BaseModel):
    station_id: str
    station_name: str
    state: str
    district: str
    date_of_record: str
    avg_temp: Optional[float] = None
    min_temp: Optional[float] = None
    max_temp: Optional[float] = None
    rainfall: Optional[float] = None  # null = missing, 0.0 = dry day
    wind_speed: Optional[float] = None
    air_pressure: Optional[float] = None
    is_rainy: Optional[bool] = None


class ScopedObservationsResponse(BaseModel):
    scope: Dict[str, Optional[str]]
    total_records: int
    data: List[ScopedObservationItem]
