"""Operational forecast schemas."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TimelineRecord(BaseModel):
    date: str
    day_offset: int
    horizon_label: str
    status: str = Field(default="UNAVAILABLE", description="'OBSERVED', 'CURRENT', 'MODEL ESTIMATE', 'FORECAST', or 'UNAVAILABLE'")
    provenance: str = Field(..., description="'OBSERVED', 'CURRENT', 'MODEL ESTIMATE', 'FORECAST', or authoritative engine string")
    is_observed: bool = False
    temp_avg_c: Optional[float] = None
    temp_min_c: Optional[float] = None
    temp_max_c: Optional[float] = None
    rainfall_mm: Optional[float] = None
    rain_probability: Optional[float] = None
    wind_kmh: Optional[float] = None
    pressure_hpa: Optional[float] = None
    model_name: Optional[str] = None
    uncertainty: Optional[Dict[str, Any]] = None
    model_metadata: Optional[Dict[str, Any]] = None


class OperationalTimelineResponse(BaseModel):
    station_id: str
    station_name: str
    state: str
    district: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    elevation_m: Optional[float] = None
    forecast_origin: str
    timeline_days_count: int = 25
    timeline: List[TimelineRecord]


class HorizonForecast(BaseModel):
    horizon: int = Field(..., ge=1, le=12)
    target_date: str
    temp_avg_c: float
    temp_min_c: float
    temp_max_c: float
    rainfall_mm: float
    rain_probability: float
    wind_kmh: float
    pressure_hpa: float
    models_used: Dict[str, str]


class MultiHorizonForecastResponse(BaseModel):
    station_id: str
    forecast_origin: str
    horizons: List[HorizonForecast]


class CurrentTelemetryResponse(BaseModel):
    station_id: str
    observation_date: str
    provenance: str = Field(..., description="'CURRENT' or 'UNAVAILABLE'")
    temp_avg_c: Optional[float] = None
    temp_min_c: Optional[float] = None
    temp_max_c: Optional[float] = None
    rainfall_mm: Optional[float] = None
    wind_kmh: Optional[float] = None
    pressure_hpa: Optional[float] = None


class HorizonDiagnosticRecord(BaseModel):
    station_id: str
    d0: str
    horizon: int
    target_date: str
    model_name: str
    feature_signature: str
    raw_prediction: Dict[str, Any]
    final_prediction: Dict[str, Any]
    provenance: str
    calendar_features: Dict[str, float]


class HorizonDiagnosticsResponse(BaseModel):
    station_id: str
    forecast_origin: str
    mode: str
    horizons_count: int
    diagnostics: List[HorizonDiagnosticRecord]

