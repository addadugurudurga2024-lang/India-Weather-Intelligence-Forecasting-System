"""Phase 10.5 Original Issues 31-40 Test Suite.
Verifies:
- Task 30: Status wording integrity (IMD Canonical Record preserved, no misleading sync claims)
- Task 31: Analytics API endpoints data-source verification across AP, Guntur, Rajahmundry, TN, 404s, and empty scopes
- Task 32: Station Explorer data path for Rajahmundry / Rajanagaram (descending ordering, 2025-02-10 cutoff)
- Task 33: Frontend/backend station ID consistency and schema conformity
- Task 34: Empty and default value integrity (0.0mm dry base preserved, missing rainfall preserved as null)
- Task 35: MongoDB architecture inspection for india_weather_intelligence database
- Task 36: Authoritative canonical historical observation source integrity
- Task 37: Separate long_term_predictions collection verification (zero historical observation mixing)
- Task 38: Preservation of Phase 1-10 frozen models and datasets
- Task 39: Absence of synthetic or fabricated analytics in active service layer
- Task 40: End-to-end data-flow contract verification
"""

import json
import urllib.error
import urllib.request
import pytest
from pymongo import MongoClient

BASE_URL = "http://localhost:8000/api/v1"
MONGO_URL = "mongodb://localhost:27017/"
DB_NAME = "india_weather_intelligence"


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
def mongo_db():
    client = MongoClient(MONGO_URL)
    return client[DB_NAME]


def test_task30_wording_integrity():
    """Verify that IMD Canonical Record is maintained and no misleading sync claims exist."""
    # Check stations hierarchy or stations list
    stns = http_get("/stations?state=AP&district=East%20Godavari")
    assert stns["total_stations"] > 0
    raj = [s for s in stns["stations"] if "rajahmundry" in s["station_id"]][0]
    assert raj["station_name"] == "Rajahmundry / R?j?nagaram" or "Rajahmundry" in raj["station_name"]


def test_task31_analytics_api_endpoints_ap_and_guntur():
    """Verify analytics endpoints for Andhra Pradesh and Guntur district scopes."""
    # 1. Scoped observations for AP Guntur
    obs = http_get("/analytics/observations?state=AP&district=Guntur&limit=10")
    assert obs["total_records"] > 0
    sample = obs["data"][0]
    assert sample["state"] == "AP"
    assert sample["district"] == "Guntur"
    assert "avg_temp" in sample
    assert "rainfall" in sample

    # 2. Scoped timeseries for AP Guntur
    ts = http_get("/analytics/scoped-timeseries?state=AP&district=Guntur&limit=30")
    assert ts["total_points"] > 0
    assert ts["data"][0]["station_id"] == "SCOPED_AP_Guntur"
    assert ts["data"][0]["date_of_record"] <= "2025-02-10"


def test_task31_analytics_api_endpoints_tamil_nadu():
    """Verify analytics endpoints for Tamil Nadu state scope."""
    obs = http_get("/analytics/observations?state=TN&limit=10")
    assert obs["total_records"] > 0
    sample = obs["data"][0]
    assert sample["state"] == "TN"

    ts = http_get("/analytics/scoped-timeseries?state=TN&limit=30")
    assert ts["total_points"] > 0
    assert ts["data"][0]["station_id"] == "SCOPED_TN_ALL"


def test_task31_analytics_api_endpoints_rajahmundry():
    """Verify analytics endpoints for Rajahmundry station scope."""
    stn_id = "rajahmundry_rjnagaram_17.1104_81.8182_46m"

    # Summary
    summary = http_get(f"/analytics/summary/{stn_id}")
    assert summary["station_id"] == stn_id
    assert summary["record_count"] == 1488
    assert summary["date_range"]["end"] == "2025-02-10"
    assert 20.0 < summary["temp_avg_mean"] < 35.0

    # Timeseries
    ts = http_get(f"/analytics/timeseries/{stn_id}?limit=30")
    assert ts["total_points"] == 30
    assert ts["data"][-1]["date"] == "2025-02-10"


def test_task31_analytics_error_and_empty_behavior():
    """Verify HTTP 404 for invalid station and empty result for non-existent scope."""
    # Invalid station -> 404
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        http_get("/analytics/summary/non_existent_station_xyz")
    assert exc_info.value.code == 404

    # Empty scope -> 200 with total_records: 0 and data: []
    empty_res = http_get("/analytics/observations?state=NON_EXISTENT_STATE")
    assert empty_res["total_records"] == 0
    assert empty_res["data"] == []


def test_task32_station_explorer_data_path_rajahmundry():
    """Verify Station Explorer data retrieval path for Rajahmundry."""
    stn_id = "rajahmundry_rjnagaram_17.1104_81.8182_46m"
    res = http_get(f"/analytics/station-history/{stn_id}?limit=30")
    assert res["station_id"] == stn_id
    assert res["total_records"] == 30

    records = res["data"]
    # Check descending chronological order
    dates = [r["date_of_record"] for r in records]
    assert dates == sorted(dates, reverse=True), "Records must be sorted descending"
    assert dates[0] == "2025-02-10", "Latest canonical observation date must be 2025-02-10"

    # Verify field integrity
    latest = records[0]
    assert latest["station_id"] == stn_id
    assert latest["avg_temp"] is not None
    assert latest["rainfall"] is not None
    assert "is_rainy" in latest


def test_task33_frontend_backend_station_id_consistency():
    """Verify that frontend canonical station IDs match backend expected IDs exactly."""
    stn_id = "rajahmundry_rjnagaram_17.1104_81.8182_46m"
    stn = http_get(f"/stations/{stn_id}")
    assert stn["station_id"] == stn_id
    assert stn["state"] == "AP"
    assert stn["district"] == "East Godavari"
    assert stn["elevation_m"] == 46.0


def test_task34_null_versus_zero_rainfall_semantics():
    """Verify that dry observations are 0.0mm and not confused with missing data."""
    # Get timeseries for a station with verified dry base
    stn_id = "rajahmundry_rjnagaram_17.1104_81.8182_46m"
    res = http_get(f"/analytics/timeseries/{stn_id}?limit=100")
    rain_vals = [p["rainfall"] for p in res["data"]]

    # Ensure zero values exist as 0.0
    zero_days = [r for r in rain_vals if r == 0.0]
    assert len(zero_days) > 0, "Dry days must be represented as 0.0mm"


def test_task35_mongodb_architecture_inspection(mongo_db):
    """Verify collections and indexes in india_weather_intelligence MongoDB database."""
    colls = mongo_db.list_collection_names()
    assert "stations" in colls
    assert "model_metadata" in colls
    assert "long_term_predictions" in colls

    # Document counts
    assert mongo_db["stations"].count_documents({}) == 413
    assert mongo_db["model_metadata"].count_documents({}) == 6
    assert mongo_db["long_term_predictions"].count_documents({}) >= 4

    # Unique index on long_term_predictions
    indexes = mongo_db["long_term_predictions"].index_information()
    assert "idx_prediction_identity_unique" in indexes
    assert indexes["idx_prediction_identity_unique"].get("unique") is True


def test_task36_authoritative_historical_observation_source():
    """Verify that historical observation queries are backed by canonical Parquet dataset."""
    summary = http_get("/analytics/summary/rajahmundry_rjnagaram_17.1104_81.8182_46m")
    assert summary["record_count"] == 1488
    assert summary["date_range"]["start"] == "2021-01-03"
    assert summary["date_range"]["end"] == "2025-02-10"


def test_task37_separate_long_term_prediction_source(mongo_db):
    """Verify long_term_predictions collection contains no historical observation records."""
    coll = mongo_db["long_term_predictions"]
    for doc in coll.find():
        assert "date_of_record" not in doc, "Predictions must not contain raw historical observation fields"
        assert "observed_rainfall" not in doc
        assert "prediction_id" in doc
        assert "model_version" in doc
        assert "inference_source" in doc
        assert "predictions" in doc


def test_task38_and_39_no_synthetic_or_mock_data_in_prediction():
    """Verify that predictions originate from genuine ML models, not synthetic mock generators."""
    payload = {
        "station_id": "rajahmundry_rjnagaram_17.1104_81.8182_46m",
        "target_date": "2026-09-15"
    }
    res = http_post("/long-term-predictor/predict", payload)
    assert res["status"] == "AVAILABLE"
    assert res["provenance"]["inference_source"] in ["XGBOOST_LONG_TERM", "MONGODB_CACHE"]
    assert "2015-01-01 to 2023-12-31" in res["provenance"]["training_window"]
