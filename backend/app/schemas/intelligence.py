"""AI Weather Intelligence schemas."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    station_id: str = Field(..., description="Target canonical station ID")
    question: str = Field(..., description="User question to weather intelligence engine")


class QuestionResponse(BaseModel):
    station_id: str
    question: str
    intent: str
    answer: str
    grounding_status: str
    evidence: List[str]
    limitations: Optional[str] = None


class IntelligenceSummaryResponse(BaseModel):
    station_id: str
    station_name: str
    executive_summary: str
    precipitation_risk: Dict[str, Any]
    temperature_insights: Dict[str, Any]
    rainfall_insights: Dict[str, Any]
    confidence_language: Dict[str, Any]
    grounding_verified: bool


class RiskAssessmentResponse(BaseModel):
    station_id: str
    station_name: str
    risk_level: str
    max_rain_probability: float
    max_predicted_rainfall_mm: float
    peak_risk_day: Optional[str] = None
    rationale: str
    threshold_basis: str
