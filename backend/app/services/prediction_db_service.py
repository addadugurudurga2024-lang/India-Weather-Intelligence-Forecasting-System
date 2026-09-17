"""MongoDB persistence and caching service for Long-Term Weather Predictions."""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import pymongo
from pymongo.collection import Collection
from backend.app.config import settings

logger = logging.getLogger("prediction_db_service")

_CLIENT: Optional[pymongo.MongoClient] = None
_COLLECTION: Optional[Collection] = None
_INDEXES_INITIALIZED = False

MODEL_VERSION = "v1.0.0"
PREDICTION_SCHEMA_VERSION = "v1"


def get_mongo_collection() -> Optional[Collection]:
    """Retrieves or initializes the long_term_predictions collection in MongoDB."""
    global _CLIENT, _COLLECTION, _INDEXES_INITIALIZED
    if _COLLECTION is not None:
        return _COLLECTION

    try:
        if _CLIENT is None:
            _CLIENT = pymongo.MongoClient(
                settings.DATABASE_URL,
                serverSelectionTimeoutMS=1500,
                connectTimeoutMS=1500
            )
            # Ping database to confirm connection
            _CLIENT.admin.command("ping")

        db = _CLIENT.get_database()
        _COLLECTION = db["long_term_predictions"]

        if not _INDEXES_INITIALIZED:
            # Deterministic unique identity: station_id + target_date + model_version + schema_version
            _COLLECTION.create_index(
                [
                    ("station_id", pymongo.ASCENDING),
                    ("target_date", pymongo.ASCENDING),
                    ("model_version", pymongo.ASCENDING),
                    ("schema_version", pymongo.ASCENDING),
                ],
                unique=True,
                name="idx_prediction_identity_unique"
            )
            # Index for querying predictions by station ordered by target_date or generated_at
            _COLLECTION.create_index(
                [("station_id", pymongo.ASCENDING), ("target_date", pymongo.ASCENDING)],
                name="idx_station_target_date"
            )
            _COLLECTION.create_index(
                [("generated_at", pymongo.DESCENDING)],
                name="idx_generated_at"
            )
            _INDEXES_INITIALIZED = True

        return _COLLECTION
    except Exception as e:
        logger.warning(f"MongoDB connection/initialization unavailable: {e}. Running in ephemeral memory/inference mode.")
        return None


def get_cached_prediction(station_id: str, target_date: str) -> Optional[Dict[str, Any]]:
    """Looks up a previously persisted prediction by its deterministic identity.
    
    Returns the persisted result with explicit provenance inference_source = 'MONGODB_CACHE'.
    """
    coll = get_mongo_collection()
    if coll is None:
        return None

    try:
        doc = coll.find_one(
            {
                "station_id": station_id,
                "target_date": target_date,
                "model_version": MODEL_VERSION,
                "schema_version": PREDICTION_SCHEMA_VERSION,
            },
            {"_id": 0}
        )
        if not doc:
            return None

        # Reconstruct API response from persisted document with explicit provenance
        cached_result = {
            "status": "AVAILABLE",
            "prediction_type": doc.get("prediction_type", "Long-Term Historical / Seasonal Model Estimate"),
            "prediction_date": doc["target_date"],
            "station_id": doc["station_id"],
            "station_name": doc["station_name"],
            "state": doc["state"],
            "district": doc["district"],
            "coordinates": doc["coordinates"],
            "predictions": doc["predictions"],
            "uncertainty": doc["uncertainty"],
            "historical_reference": doc.get("historical_reference"),
            "how_prediction_made": doc.get("how_prediction_made"),
            "provenance": {
                **(doc.get("provenance") or {}),
                "inference_source": "MONGODB_CACHE",
                "cached_from_generated_at": doc.get("generated_at"),
                "model_version": doc.get("model_version", MODEL_VERSION),
                "prediction_id": doc.get("prediction_id"),
            },
            "limitations": doc.get("limitations"),
        }
        return cached_result
    except Exception as e:
        logger.warning(f"Failed to read from MongoDB cache for {station_id} on {target_date}: {e}")
        return None


def persist_prediction(prediction_res: Dict[str, Any]) -> bool:
    """Persists a genuine Long-Term prediction into MongoDB with deduplication.
    
    Generates a deterministic prediction_id and stores complete reproduction metadata.
    """
    if not prediction_res or prediction_res.get("status") != "AVAILABLE":
        return False

    coll = get_mongo_collection()
    if coll is None:
        return False

    station_id = prediction_res["station_id"]
    target_date = prediction_res["prediction_date"]
    prediction_id = f"PRED_{station_id}_{target_date}_{MODEL_VERSION}"
    now_iso = datetime.now(timezone.utc).isoformat()

    doc = {
        "prediction_id": prediction_id,
        "station_id": station_id,
        "station_name": prediction_res["station_name"],
        "state": prediction_res["state"],
        "district": prediction_res["district"],
        "coordinates": prediction_res["coordinates"],
        "target_date": target_date,
        "generated_at": now_iso,
        "model_version": MODEL_VERSION,
        "schema_version": PREDICTION_SCHEMA_VERSION,
        "model_family": "XGBoost",
        "inference_source": "XGBOOST_LONG_TERM",
        "prediction_type": prediction_res.get("prediction_type", "Long-Term Historical / Seasonal Model Estimate"),
        "predictions": prediction_res["predictions"],
        "uncertainty": prediction_res["uncertainty"],
        "historical_reference": prediction_res.get("historical_reference"),
        "how_prediction_made": prediction_res.get("how_prediction_made"),
        "provenance": {
            **(prediction_res.get("provenance") or {}),
            "inference_source": "XGBOOST_LONG_TERM",
            "model_version": MODEL_VERSION,
            "prediction_id": prediction_id,
        },
        "limitations": prediction_res.get("limitations"),
    }

    try:
        # Upsert using unique identity to prevent duplicate documents
        coll.replace_one(
            {
                "station_id": station_id,
                "target_date": target_date,
                "model_version": MODEL_VERSION,
                "schema_version": PREDICTION_SCHEMA_VERSION,
            },
            doc,
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"Failed to persist prediction into MongoDB: {e}")
        return False


def get_station_prediction_history(station_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieves persisted prediction summaries for a station sorted by target_date."""
    coll = get_mongo_collection()
    if coll is None:
        return []

    try:
        cursor = coll.find(
            {"station_id": station_id},
            {"_id": 0}
        ).sort("target_date", pymongo.ASCENDING).limit(limit)

        results = []
        for doc in cursor:
            results.append({
                "prediction_id": doc.get("prediction_id", ""),
                "station_id": doc["station_id"],
                "station_name": doc["station_name"],
                "state": doc["state"],
                "district": doc["district"],
                "target_date": doc["target_date"],
                "generated_at": doc.get("generated_at", ""),
                "model_version": doc.get("model_version", MODEL_VERSION),
                "inference_source": doc.get("inference_source", "XGBOOST_LONG_TERM"),
                "predictions": doc["predictions"],
                "uncertainty": doc["uncertainty"],
            })
        return results
    except Exception as e:
        logger.warning(f"Failed to retrieve prediction history for {station_id}: {e}")
        return []
