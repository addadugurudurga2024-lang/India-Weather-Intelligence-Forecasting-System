"""
Phase 8 Intelligence Output Schema
Defines the comprehensive structured JSON output format for AI Weather Intelligence.
Every natural language output is generated strictly from this representation.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field
from phase8_intelligence.core.contracts import DataStatus, StationMetadata, PredictionIntervals


class RiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"


class PrecipitationRiskOutput(BaseModel):
    risk_level: RiskLevel
    max_rain_probability: float = Field(..., ge=0.0, le=1.0)
    max_predicted_rainfall_mm: float = Field(..., ge=0.0)
    peak_risk_day: Optional[str] = None
    peak_risk_horizon: Optional[str] = None
    rationale: str
    threshold_basis: str


class TemperatureInsights(BaseModel):
    data_status: DataStatus
    current_temp: Optional[float] = None
    forecast_avg_min: Optional[float] = None
    forecast_avg_max: Optional[float] = None
    overall_trend: str  # e.g., "WARMING", "COOLING", "STABLE", "UNAVAILABLE"
    trend_delta_c: Optional[float] = None
    diurnal_range_mean: Optional[float] = None
    interval_widening_c: Optional[float] = None  # difference between T+12 interval and T+1 interval
    insights: List[str] = Field(default_factory=list)


class RainfallInsights(BaseModel):
    data_status: DataStatus
    rain_expected: bool
    highest_probability: float = Field(..., ge=0.0, le=1.0)
    highest_prob_day: Optional[str] = None
    highest_prob_horizon: Optional[str] = None
    total_expected_rainfall_mm: float = Field(..., ge=0.0)
    max_single_day_rainfall_mm: float = Field(..., ge=0.0)
    max_rainfall_day: Optional[str] = None
    consecutive_rain_days: int = 0
    consecutive_dry_days: int = 0
    insights: List[str] = Field(default_factory=list)


class ConfidenceLanguageOutput(BaseModel):
    near_term_confidence_descriptor: str
    extended_uncertainty_descriptor: str
    calibration_basis: str
    statement: str
    forbidden_terms_checked: bool = True


class ModelContextOutput(BaseModel):
    primary_architecture: str = "Direct Multi-Horizon XGBoost Gradient Boosted Trees"
    supported_horizons: str = "T+1 to T+12 days ahead"
    attribution_methodology: str = "Phase 6 TreeSHAP Feature Attributions (Statistical Predictive Contribution)"
    top_predictive_features: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)


class ObservationContextSummary(BaseModel):
    data_status: DataStatus
    historical_days_available: int
    current_telemetry_status: str  # "AVAILABLE" or "UNAVAILABLE"
    recent_mean_temp: Optional[float] = None
    recent_total_rain_mm: Optional[float] = None
    current_temp: Optional[float] = None
    summary_text: str


class ForecastContextSummary(BaseModel):
    horizons_available: int = 12
    t1_forecast_temp: Optional[float] = None
    t1_rain_probability: Optional[float] = None
    t1_rain_amount_mm: Optional[float] = None
    t3_trend_summary: str
    t12_trend_summary: str
    summary_text: str


class AnomalyReport(BaseModel):
    is_anomalous: bool
    temperature_anomaly_c: Optional[float] = None
    rainfall_anomaly_percent: Optional[float] = None
    baseline_reference: Optional[str] = None
    description: str


class WeatherIntelligenceOutput(BaseModel):
    station: StationMetadata
    forecast_origin: str
    generated_at: str
    data_status: DataStatus
    observation_context: ObservationContextSummary
    forecast_context: ForecastContextSummary
    key_insights: List[str]
    temperature_insights: TemperatureInsights
    rainfall_insights: RainfallInsights
    precipitation_risk: PrecipitationRiskOutput
    trend_insights: List[str]
    anomaly_insights: List[AnomalyReport]
    confidence_language: ConfidenceLanguageOutput
    model_context: ModelContextOutput
    limitations: List[str]
    provenance: Dict[str, Any]
    natural_language_summary: Optional[str] = None
