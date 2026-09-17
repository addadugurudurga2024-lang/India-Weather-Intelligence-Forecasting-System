"""Long-Term Predictor service adapter wrapping Phase 9 models and MongoDB cache."""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from backend.app.config import settings
from backend.app.services.prediction_db_service import (
    get_cached_prediction,
    persist_prediction,
    get_station_prediction_history,
)

sys.path.insert(0, str(settings.ROOT_PATH / "phase9_long_term_predictor" / "services"))
from long_term_predictor_engine import (
    predict_long_term as _engine_predict,
    get_climatology as _engine_climatology,
    get_metadata as _engine_metadata,
)


def run_long_term_prediction(station_id: str, target_date: str) -> Dict[str, Any]:
    """Generates Phase 9 long-term prediction for a station and target date.
    
    Checks MongoDB for a previously persisted prediction under the same deterministic identity.
    If cached, returns with explicit provenance inference_source = 'MONGODB_CACHE'.
    Otherwise, executes genuine XGBoost inference, persists to MongoDB, and returns with
    provenance inference_source = 'XGBOOST_LONG_TERM'.
    """
    # 1. Attempt cache retrieval
    cached = get_cached_prediction(station_id, target_date)
    if cached is not None:
        return cached

    # 2. Execute genuine Phase 9 XGBoost inference
    res = _engine_predict(station_id, target_date)
    if res and res.get("status") == "AVAILABLE":
        # Tag explicit inference source
        if "provenance" in res and isinstance(res["provenance"], dict):
            res["provenance"]["inference_source"] = "XGBOOST_LONG_TERM"
        # 3. Persist to MongoDB for caching and audit history
        persist_prediction(res)

    return res


def get_station_long_term_climatology(station_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves 413-station climatological reference and monthly statistics."""
    climatology = _engine_climatology()
    return climatology.get(station_id)


def get_long_term_model_metadata() -> Dict[str, Any]:
    """Returns Phase 9 models metadata."""
    return _engine_metadata()


def get_prediction_history(station_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves persisted prediction history for a station from MongoDB."""
    return get_station_prediction_history(station_id, limit)
