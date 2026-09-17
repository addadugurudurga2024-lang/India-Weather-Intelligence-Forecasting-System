"""Model registry and performance metadata schemas."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class PhaseModelInfo(BaseModel):
    phase: str
    architecture: str
    total_models: int
    targets: List[str]
    description: str


class ModelRegistryResponse(BaseModel):
    authoritative_phase3_metrics: Dict[str, Any]
    phase7_multi_horizon_models_count: int = 84
    phase9_long_term_models_count: int = 7
    models: List[PhaseModelInfo]
