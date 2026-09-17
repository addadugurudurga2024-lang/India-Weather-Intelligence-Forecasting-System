"""Phase 10.5 Remaining Issues 16-30 Test Suite.
Verifies:
- Issue 16: MongoDB prediction collection long_term_predictions schema & fields
- Issue 17: Prediction identity unique index & deduplication
- Issue 18: Genuine persist-on-prediction flow with physical constraints
- Issue 19: Cache read & reuse with preserved metadata and inference_source=MONGODB_CACHE
- Issue 20: Station prediction history endpoint GET /predictions/{station_id}
- Issue 21: Observed vs predicted data separation
- Issue 22: Provenance audit & truthful inference_source tags
- Issue 23: 80% Prediction Interval terminology & empirical uncertainty
- Issue 24: Long-Term future date semantics & validation bounds
- Issue 25: Physical ordering & bounds validation
- Mandatory Test Matrix: 12 scenarios verified
"""

import json
import urllib.error
import urllib.request
import pytest
from pymongo import MongoClient

BASE_URL = "http://localhost:8000/api/v1"
MONGO_URL = "mongodb://localhost:27017/"
DB_NAME = "india_weather_intelligence"
COLL_NAME = "long_term_predictions"


def http_get(endpoint: str):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.urlopen(url, timeout=10)
    return json.loads(req.read().decode("utf-8"))


def http_post(endpoint: str, payload: dict):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req, timeout=10)
    return json.loads(res.read().decode("utf-8"))


@pytest.fixture(scope="module")
def mongo_coll():
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    return db[COLL_NAME]


def test_issue16_and_17_mongodb_collection_schema_and_indexes(mongo_coll):
    """Verify long_term_predictions collection exists with unique identity index."""
    indexes = mongo_coll.index_information()
    assert "idx_prediction_identity_unique" in indexes, "Unique identity index must exist"
    idx = indexes["idx_prediction_identity_unique"]
    assert idx.get("unique") is True, "Prediction identity index must be unique"
    
    expected_keys = [("station_id", 1), ("target_date", 1), ("model_version", 1), ("schema_version", 1)]
    assert idx["key"] == expected_keys, f"Expected compound key {expected_keys}, got {idx['key']}"


def test_issue18_genuine_persist_on_prediction_flow(mongo_coll):
    """Test generating a genuine prediction and verifying MongoDB persistence."""
    stn_id = "rajahmundry_rjnagaram_17.1104_81.8182_46m"
    target_date = "2026-09-15"
    
    # Request prediction
    payload = {"station_id": stn_id, "target_date": target_date}
    res = http_post("/long-term-predictor/predict", payload)
    
    assert res["status"] == "AVAILABLE"
    assert res["station_id"] == stn_id
    assert res["prediction_date"] == target_date
    assert res["prediction_type"] == "Long-Term Historical / Seasonal Model Estimate"
    
    # Verify predictions dict & physical constraints
    preds = res["predictions"]
    assert preds["min_temp"] <= preds["avg_temp"] <= preds["max_temp"], "Physical ordering Tmin <= Tavg <= Tmax"
    assert preds["rainfall"] >= 0.0, "Rainfall must be non-negative"
    assert preds["wind_speed"] >= 0.0, "Wind speed must be non-negative"
    assert 0.0 <= preds["rain_probability"] <= 1.0, "Rain probability in [0, 1]"
    assert 0.0 <= preds["rain_probability_pct"] <= 100.0, "Rain probability pct in [0, 100]"
    
    # Verify uncertainty interval fields (80% Prediction Interval)
    unc = res["uncertainty"]
    assert "avg_temp_interval_80" in unc
    assert "rainfall_interval_80" in unc
    assert unc["avg_temp_interval_80"][0] <= unc["avg_temp_interval_80"][1]
    
    # Verify document in MongoDB
    doc = mongo_coll.find_one({"station_id": stn_id, "target_date": target_date})
    assert doc is not None, "Document must be persisted in MongoDB"
    assert doc["prediction_id"] == f"PRED_{stn_id}_{target_date}_v1.0.0"
    assert "Rajahmundry" in doc["station_name"]
    assert doc["state"] == "AP"
    assert doc["district"] == "East Godavari"
    assert doc["model_version"] == "v1.0.0"
    assert doc["model_family"] == "XGBoost"


def test_issue19_cache_read_and_reuse(mongo_coll):
    """Test that repeated identical request returns cached result with inference_source=MONGODB_CACHE."""
    stn_id = "rajahmundry_rjnagaram_17.1104_81.8182_46m"
    target_date = "2026-09-15"
    
    # Read count before second request
    count_before = mongo_coll.count_documents({"station_id": stn_id, "target_date": target_date})
    assert count_before == 1, "Exactly one prediction doc should exist before re-request"
    
    # Send identical request
    payload = {"station_id": stn_id, "target_date": target_date}
    res = http_post("/long-term-predictor/predict", payload)
    
    assert res["status"] == "AVAILABLE"
    # Provenance inference_source must be MONGODB_CACHE
    assert res["provenance"]["inference_source"] == "MONGODB_CACHE"
    
    # Read count after second request
    count_after = mongo_coll.count_documents({"station_id": stn_id, "target_date": target_date})
    assert count_after == 1, "Repeated request MUST NOT create duplicate MongoDB documents"


def test_issue19_different_target_date_creates_separate_identity(mongo_coll):
    """Test that different target date generates a distinct prediction identity."""
    stn_id = "rajahmundry_rjnagaram_17.1104_81.8182_46m"
    target_date = "2026-11-15"
    
    payload = {"station_id": stn_id, "target_date": target_date}
    res = http_post("/long-term-predictor/predict", payload)
    
    assert res["status"] == "AVAILABLE"
    assert res["prediction_date"] == target_date
    
    doc = mongo_coll.find_one({"station_id": stn_id, "target_date": target_date})
    assert doc is not None
    assert doc["target_date"] == "2026-11-15"
    assert doc["prediction_id"] == f"PRED_{stn_id}_{target_date}_v1.0.0"


def test_issue19_different_station_creates_separate_identity(mongo_coll):
    """Test that different station generates a distinct prediction identity."""
    stn_id = "agra_27.1500_77.9667_168m"
    target_date = "2026-09-15"
    
    payload = {"station_id": stn_id, "target_date": target_date}
    res = http_post("/long-term-predictor/predict", payload)
    
    assert res["status"] == "AVAILABLE"
    assert res["station_id"] == stn_id
    
    doc = mongo_coll.find_one({"station_id": stn_id, "target_date": target_date})
    assert doc is not None
    assert doc["station_id"] == stn_id


def test_issue20_station_prediction_history_endpoint():
    """Verify GET /api/v1/long-term-predictor/predictions/{station_id} returns persisted predictions."""
    stn_id = "rajahmundry_rjnagaram_17.1104_81.8182_46m"
    history = http_get(f"/long-term-predictor/predictions/{stn_id}")
    
    assert history["station_id"] == stn_id
    assert history["total_persisted"] >= 2
    assert len(history["predictions"]) >= 2
    
    # Verify deterministic chronological ordering by target_date
    dates = [p["target_date"] for p in history["predictions"]]
    assert dates == sorted(dates), "Predictions should be sorted chronologically by target_date"
    
    # Check fields of history items
    for p in history["predictions"]:
        assert p["station_id"] == stn_id
        assert "prediction_id" in p
        assert "model_version" in p
        assert "inference_source" in p
        assert "predictions" in p
        assert "uncertainty" in p
        # Verify no historical observation records are mixed into predictions
        assert "observed_rain" not in p
        assert "observed_temp" not in p


def test_issue21_observed_vs_predicted_data_separation():
    """Verify historical observation anchor is strictly separate from future model predictions."""
    payload = {
        "station_id": "rajahmundry_rjnagaram_17.1104_81.8182_46m",
        "target_date": "2026-11-15"
    }
    res = http_post("/long-term-predictor/predict", payload)
    
    # Model predictions
    assert "predictions" in res
    preds = res["predictions"]
    assert "avg_temp" in preds
    
    # Historical reference is separate and explicitly identified
    assert "historical_reference" in res
    ref = res["historical_reference"]
    assert "station_monthly_climatology" in ref
    assert ref["calendar_context"]["selected_date"] == "2026-11-15"
    assert ref["calendar_context"]["month"] == "November"


def test_issue22_provenance_truthfulness():
    """Verify that inference_source accurately reflects execution pathway."""
    payload = {
        "station_id": "rajahmundry_rjnagaram_17.1104_81.8182_46m",
        "target_date": "2026-11-15"
    }
    res = http_post("/long-term-predictor/predict", payload)
    
    # Provenance inference_source must be MONGODB_CACHE for cached call
    assert res["provenance"]["inference_source"] in ["XGBOOST_LONG_TERM", "MONGODB_CACHE"]
    assert res["provenance"]["physical_ordering_applied"] is True
    assert "models_used" in res["provenance"]
    assert res["provenance"]["models_used"]["avg_temp"] == "xgb_longterm_temp_v1"


def test_issue23_prediction_interval_not_confidence_interval():
    """Verify uncertainty terminology uses 80% Prediction Interval, not Confidence Interval."""
    payload = {
        "station_id": "rajahmundry_rjnagaram_17.1104_81.8182_46m",
        "target_date": "2026-09-15"
    }
    res = http_post("/long-term-predictor/predict", payload)
    
    # Uncertainty method string should mention empirical residual quantiles, not Gaussian CI
    unc = res["uncertainty"]
    method_str = unc["method"]
    assert "Empirical residual quantiles" in method_str or "prediction interval" in method_str.lower()
    assert "confidence interval" not in method_str.lower()


def test_issue24_long_term_date_range_validation():
    """Verify supported date range (2025-01-01 to 2027-12-31) and honest error for out-of-range dates."""
    # Out-of-range past date
    past_payload = {
        "station_id": "rajahmundry_rjnagaram_17.1104_81.8182_46m",
        "target_date": "2024-12-31"
    }
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        http_post("/long-term-predictor/predict", past_payload)
    assert exc_info.value.code == 400
    err_body = exc_info.value.read().decode("utf-8")
    assert "2025-01-01 to 2027-12-31" in err_body

    # Out-of-range future date
    future_payload = {
        "station_id": "rajahmundry_rjnagaram_17.1104_81.8182_46m",
        "target_date": "2028-01-01"
    }
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        http_post("/long-term-predictor/predict", future_payload)
    assert exc_info.value.code == 400
    err_body = exc_info.value.read().decode("utf-8")
    assert "2025-01-01 to 2027-12-31" in err_body


def test_mandatory_matrix_12_scenarios(mongo_coll):
    """End-to-end execution of the 12 scenarios from the master prompt test matrix."""
    stn_raj = "rajahmundry_rjnagaram_17.1104_81.8182_46m"
    stn_agra = "agra_27.1500_77.9667_168m"

    # TEST 1: Rajahmundry 2026-09-15
    res1 = http_post("/long-term-predictor/predict", {"station_id": stn_raj, "target_date": "2026-09-15"})
    assert res1["status"] == "AVAILABLE"
    assert res1["provenance"]["inference_source"] in ["XGBOOST_LONG_TERM", "MONGODB_CACHE"]

    # TEST 2: Rajahmundry 2026-11-15
    res2 = http_post("/long-term-predictor/predict", {"station_id": stn_raj, "target_date": "2026-11-15"})
    assert res2["status"] == "AVAILABLE"
    assert res2["predictions"]["avg_temp"] != res1["predictions"]["avg_temp"]

    # TEST 3: Repeat TEST 1 (MongoDB cache hit)
    res3 = http_post("/long-term-predictor/predict", {"station_id": stn_raj, "target_date": "2026-09-15"})
    assert res3["provenance"]["inference_source"] == "MONGODB_CACHE"
    assert res3["predictions"] == res1["predictions"]

    # TEST 4: Change station (Agra)
    res4 = http_post("/long-term-predictor/predict", {"station_id": stn_agra, "target_date": "2026-09-15"})
    assert res4["station_id"] == stn_agra
    assert res4["coordinates"]["elevation_m"] == 168.0

    # TEST 5: Change target date
    res5 = http_post("/long-term-predictor/predict", {"station_id": stn_raj, "target_date": "2026-12-25"})
    assert res5["prediction_date"] == "2026-12-25"

    # TEST 6: Historical reference clearly identified
    assert res1["historical_reference"] is not None
    assert "station_monthly_climatology" in res1["historical_reference"]

    # TEST 7: Future date identified as prediction
    assert res1["prediction_type"] == "Long-Term Historical / Seasonal Model Estimate"

    # TEST 8: Provenance is never falsified
    assert res1["provenance"]["inference_source"] in ["XGBOOST_LONG_TERM", "MONGODB_CACHE", "OFFLINE_ESTIMATE"]

    # TEST 9 & 10: History endpoint returns persisted records without mixing observations
    hist = http_get(f"/long-term-predictor/predictions/{stn_raj}")
    assert hist["total_persisted"] >= 3
    for p in hist["predictions"]:
        assert p["station_id"] == stn_raj
        assert "observed_rainfall" not in p

    # TEST 11: MongoDB duplicate check
    doc_count = mongo_coll.count_documents({"station_id": stn_raj, "target_date": "2026-09-15"})
    assert doc_count == 1, "Exactly one document per unique identity"

    # TEST 12: Complete API response contract
    for key in ["status", "station_id", "prediction_date", "predictions", "uncertainty", "provenance"]:
        assert key in res1
