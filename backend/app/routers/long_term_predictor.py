"""Long-Term Weather Predictor router."""

from fastapi import APIRouter, HTTPException, Query
from backend.app.schemas.long_term_predictor import (
    LongTermPredictRequest,
    LongTermPredictResponse,
    StationPredictionHistoryResponse,
)
from backend.app.services.data_service import get_station_by_id
from backend.app.services.long_term_predictor_service import (
    run_long_term_prediction,
    get_station_long_term_climatology,
    get_long_term_model_metadata,
    get_prediction_history,
)

router = APIRouter(prefix="/long-term-predictor", tags=["Long-Term Predictor"])


@router.post("/predict", response_model=LongTermPredictResponse)
def predict_long_term(request: LongTermPredictRequest):
    """Generates Phase 9 long-term predictions across 7 targets with 80% prediction intervals.
    
    Persists genuine predictions to MongoDB and reuses cached predictions under the same identity.
    """
    stn = get_station_by_id(request.station_id)
    if not stn:
        raise HTTPException(
            status_code=404,
            detail=f"Station '{request.station_id}' not found in the 413 canonical station registry.",
        )
    
    # Run prediction (with MongoDB cache/persist)
    res = run_long_term_prediction(request.station_id, request.target_date)
    if res.get("status") == "UNAVAILABLE" and "error" in res:
        raise HTTPException(status_code=400, detail=res["error"])
    if res.get("status") in ("INVALID_DATE", "ERROR"):
        raise HTTPException(status_code=400, detail=res.get("message") or res.get("error", "Prediction engine error."))
        
    return res


@router.get("/predictions/{station_id}", response_model=StationPredictionHistoryResponse)
def get_persisted_predictions(station_id: str, limit: int = Query(default=50, ge=1, le=200)):
    """Retrieves persisted genuine Long-Term predictions for a station from MongoDB."""
    stn = get_station_by_id(station_id)
    if not stn:
        raise HTTPException(
            status_code=404,
            detail=f"Station '{station_id}' not found in the 413 canonical station registry.",
        )
    history = get_prediction_history(station_id, limit=limit)
    return {
        "station_id": station_id,
        "total_persisted": len(history),
        "predictions": history,
    }


@router.get("/climatology/{station_id}")
def get_climatology(station_id: str):
    """Retrieves 413-station climatological reference and monthly statistics."""
    stn = get_station_by_id(station_id)
    if not stn:
        raise HTTPException(
            status_code=404,
            detail=f"Station '{station_id}' not found in the 413 canonical station registry.",
        )
    climatology = get_station_long_term_climatology(station_id)
    if not climatology:
        raise HTTPException(status_code=404, detail="Climatology data unavailable for station.")
    return climatology


@router.get("/metadata")
def get_metadata():
    """Returns Phase 9 models metadata and empirical uncertainty validation statistics."""
    return get_long_term_model_metadata()
