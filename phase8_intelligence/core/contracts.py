"""
Phase 8 Authoritative Data Contract
Defines strict Pydantic v2 input schemas containing verified project data.
No fabricated fields; complete provenance enforcement.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field, field_validator, model_validator


class DataStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    PARTIAL = "PARTIAL"
    UNAVAILABLE = "UNAVAILABLE"


class TimelineDayStatus(str, Enum):
    OBSERVED = "OBSERVED"
    CURRENT = "CURRENT"
    FORECAST = "FORECAST"
    DERIVED = "DERIVED"
    UNAVAILABLE = "UNAVAILABLE"


class StationMetadata(BaseModel):
    station_id: str = Field(..., description="Canonical IMD alphanumeric identifier")
    station_name: str = Field(..., description="Official station designation")
    state: str = Field(..., description="Indian State or Union Territory")
    district: str = Field(..., description="Administrative district")
    latitude: float = Field(..., ge=6.0, le=38.0, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=68.0, le=98.0, description="Longitude in decimal degrees")
    elevation_m: float = Field(..., ge=-100.0, le=9000.0, description="Station elevation in meters")


class PredictionIntervals(BaseModel):
    temp_interval_80: Tuple[float, float] = Field(..., description="80% nominal temperature interval [P10, P90]")
    temp_interval_95: Tuple[float, float] = Field(..., description="95% nominal temperature interval [P2.5, P97.5]")
    rainfall_interval_80: Tuple[float, float] = Field(..., description="80% nominal rainfall interval [0, P90]")
    methodology: str = Field("Empirical Validation Residual Quantiles (Fold 2)", description="Calibration source")

    @field_validator("temp_interval_80", "temp_interval_95")
    @classmethod
    def validate_interval_order(cls, v: Tuple[float, float]) -> Tuple[float, float]:
        if v[0] > v[1]:
            raise ValueError(f"Lower bound {v[0]} exceeds upper bound {v[1]}")
        return v


class ModelMetadata(BaseModel):
    model_id: str
    model_version: str
    horizon_name: str
    training_period: str


class TimelineDayData(BaseModel):
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    relative_day: int = Field(..., ge=-12, le=12, description="Timeline day offset (-12 to +12)")
    status: TimelineDayStatus
    is_observed: bool
    provenance: str = Field(..., min_length=3)
    temperature_avg: Optional[float] = None
    temperature_min: Optional[float] = None
    temperature_max: Optional[float] = None
    rainfall_amount: Optional[float] = None
    rain_probability: Optional[float] = Field(None, ge=0.0, le=1.0)
    rain_binary: Optional[bool] = None
    wind_speed: Optional[float] = None
    air_pressure: Optional[float] = None
    uncertainty: Optional[PredictionIntervals] = None
    model_metadata: Optional[ModelMetadata] = None

    @model_validator(mode="after")
    def validate_temporal_boundary_and_ranges(self) -> "TimelineDayData":
        # Check temperature physical consistency if all present
        if self.temperature_min is not None and self.temperature_avg is not None:
            if self.temperature_min > self.temperature_avg + 0.1:  # Allow 0.1 float precision
                raise ValueError(f"Tmin ({self.temperature_min}) cannot exceed Tavg ({self.temperature_avg})")
        if self.temperature_max is not None and self.temperature_avg is not None:
            if self.temperature_max < self.temperature_avg - 0.1:
                raise ValueError(f"Tmax ({self.temperature_max}) cannot be less than Tavg ({self.temperature_avg})")

        # Check observed vs forecast boundary
        if self.relative_day < 0:
            if self.status not in (TimelineDayStatus.OBSERVED, TimelineDayStatus.UNAVAILABLE):
                raise ValueError(f"Negative relative_day ({self.relative_day}) must be OBSERVED or UNAVAILABLE")
        elif self.relative_day == 0:
            if self.status not in (TimelineDayStatus.CURRENT, TimelineDayStatus.UNAVAILABLE):
                raise ValueError(f"Relative_day 0 must be CURRENT or UNAVAILABLE")
        else:
            if self.status not in (TimelineDayStatus.FORECAST, TimelineDayStatus.UNAVAILABLE):
                raise ValueError(f"Positive relative_day ({self.relative_day}) must be FORECAST or UNAVAILABLE")
        return self


class HistoricalBaseline(BaseModel):
    month: int = Field(..., ge=1, le=12)
    avg_temp_mean: float
    avg_temp_std: float
    rainfall_mean: float
    rainfall_std: float
    sample_count: int = Field(..., ge=1)


class AuthoritativeWeatherContextInput(BaseModel):
    station: StationMetadata
    forecast_origin: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    timeline_days: List[TimelineDayData] = Field(..., min_length=1, max_length=25)
    historical_baseline: Optional[HistoricalBaseline] = None
    evaluation_summary: Optional[Dict[str, Any]] = None
    generated_at: str
    provenance: str = "Phase 7 Operational 25-Day Weather Timeline Engine"
