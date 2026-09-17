"""Long-Term Predictor schemas."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class LongTermPredictRequest(BaseModel):
    station_id: str = Field(..., description="Canonical station ID")
    target_date: str = Field(..., description="Target date in YYYY-MM-DD format (2025-01-01 to 2027-12-31)")


class LongTermPredictions(BaseModel):
    avg_temp: float
    min_temp: float
    max_temp: float
    rainfall: float
    rain_probability: float
    rain_probability_pct: float
    wind_speed: float
    air_pressure: float


class LongTermUncertainty(BaseModel):
    avg_temp_interval_80: List[float]
    min_temp_interval_80: List[float]
    max_temp_interval_80: List[float]
    rainfall_interval_80: List[float]
    wind_speed_interval_80: List[float]
    air_pressure_interval_80: List[float]
    method: str


class LongTermCoordinates(BaseModel):
    latitude: float
    longitude: float
    elevation_m: float


class LongTermPredictResponse(BaseModel):
    status: str
    prediction_type: str
    prediction_date: str
    station_id: str
    station_name: str
    state: str
    district: str
    coordinates: LongTermCoordinates
    predictions: Optional[LongTermPredictions] = None
    uncertainty: Optional[LongTermUncertainty] = None
    historical_reference: Optional[Dict[str, Any]] = None
    how_prediction_made: Optional[List[Dict[str, Any]]] = None
    provenance: Optional[Dict[str, Any]] = None
    limitations: Optional[List[str]] = None
    error: Optional[str] = None


class PersistedPredictionSummary(BaseModel):
    prediction_id: str
    station_id: str
    station_name: str
    state: str
    district: str
    target_date: str
    generated_at: str
    model_version: str
    inference_source: str
    predictions: LongTermPredictions
    uncertainty: LongTermUncertainty


class StationPredictionHistoryResponse(BaseModel):
    station_id: str
    total_persisted: int
    predictions: List[PersistedPredictionSummary]
