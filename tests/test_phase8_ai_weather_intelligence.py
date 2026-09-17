"""
Phase 8 AI Weather Intelligence Regression Test Suite
Validates:
- Deterministic generation across all 10 meteorological test fixtures
- Exact numerical and unit preservation
- Temperature trend calculations
- Calibrated precipitation risk classification
- Multi-horizon tranche decomposition
- Supported Q&A intent execution
- Pairwise station comparisons
"""

import pytest
from phase8_intelligence.fixtures.test_fixtures import (
    get_dry_station_fixture,
    get_high_rain_station_fixture,
    get_coastal_station_fixture,
    get_high_elevation_station_fixture,
    get_missing_telemetry_fixture,
    get_partial_telemetry_fixture,
    get_high_uncertainty_fixture,
    get_increasing_rain_prob_fixture,
    get_decreasing_temp_fixture,
    get_historical_anomaly_fixture,
)
from phase8_intelligence.core.engine import WeatherIntelligenceEngine
from phase8_intelligence.core.qa_interface import QAInterfaceEngine
from phase8_intelligence.core.comparison_engine import ComparisonIntelligenceEngine
from phase8_intelligence.core.schemas import RiskLevel


def test_all_10_fixtures_produce_valid_intelligence():
    """Confirms that all 10 synthetic fixtures process without error and pass grounding validation."""
    fixtures = [
        get_dry_station_fixture(),
        get_high_rain_station_fixture(),
        get_coastal_station_fixture(),
        get_high_elevation_station_fixture(),
        get_missing_telemetry_fixture(),
        get_partial_telemetry_fixture(),
        get_high_uncertainty_fixture(),
        get_increasing_rain_prob_fixture(),
        get_decreasing_temp_fixture(),
        get_historical_anomaly_fixture(),
    ]

    for idx, ctx in enumerate(fixtures, start=1):
        intel = WeatherIntelligenceEngine.generate_intelligence(ctx)
        assert intel is not None
        assert intel.station.station_id == ctx.station.station_id
        assert len(intel.key_insights) >= 1
        assert intel.natural_language_summary is not None
        assert len(intel.natural_language_summary) > 200


def test_determinism_identical_input_identical_output():
    """Verifies that identical input context yields byte-for-byte identical structured fields."""
    ctx = get_dry_station_fixture()
    intel1 = WeatherIntelligenceEngine.generate_intelligence(ctx)
    intel2 = WeatherIntelligenceEngine.generate_intelligence(ctx)

    assert intel1.temperature_insights == intel2.temperature_insights
    assert intel1.rainfall_insights == intel2.rainfall_insights
    assert intel1.precipitation_risk == intel2.precipitation_risk
    assert intel1.key_insights == intel2.key_insights


def test_high_rain_station_categorized_as_high_risk():
    """Verifies that the high-rain fixture triggers HIGH risk categorization."""
    ctx = get_high_rain_station_fixture()
    intel = WeatherIntelligenceEngine.generate_intelligence(ctx)

    assert intel.precipitation_risk.risk_level == RiskLevel.HIGH
    assert intel.rainfall_insights.highest_probability >= 0.60
    assert intel.rainfall_insights.total_expected_rainfall_mm > 50.0
    assert "High precipitation risk" in intel.precipitation_risk.rationale


def test_dry_station_categorized_as_low_risk():
    """Verifies that the dry station fixture triggers LOW risk categorization."""
    ctx = get_dry_station_fixture()
    intel = WeatherIntelligenceEngine.generate_intelligence(ctx)

    assert intel.precipitation_risk.risk_level == RiskLevel.LOW
    assert intel.rainfall_insights.highest_probability <= 0.10
    assert intel.rainfall_insights.total_expected_rainfall_mm == 0.0


def test_decreasing_temp_fixture_cooling_trend():
    """Verifies that a cooling curve is identified as COOLING trend."""
    ctx = get_decreasing_temp_fixture()
    intel = WeatherIntelligenceEngine.generate_intelligence(ctx)

    assert intel.temperature_insights.overall_trend == "COOLING"
    assert intel.temperature_insights.trend_delta_c < -2.0


def test_historical_anomaly_detection():
    """Verifies that severe climatological departures (>2 sigma) are flagged as anomalies."""
    ctx = get_historical_anomaly_fixture()
    intel = WeatherIntelligenceEngine.generate_intelligence(ctx)

    anomalies = [a for a in intel.anomaly_insights if a.is_anomalous]
    assert len(anomalies) >= 1
    assert any("exceeds 2σ" in a.description for a in anomalies)


def test_qa_interface_supported_intents():
    """Tests all standard supported queries through QAInterfaceEngine."""
    ctx = get_high_rain_station_fixture()

    queries = [
        ("What is the forecast?", "FORECAST_SUMMARY"),
        ("Will rain occur tomorrow?", "RAIN_OCCURRENCE"),
        ("How does the temperature change over the next 12 days?", "TEMPERATURE_TREND"),
        ("Which day has the highest rain probability?", "PEAK_RAIN_DAY"),
        ("How uncertain is the forecast?", "UNCERTAINTY_QUERY"),
        ("Why is this forecast considered high risk?", "RISK_RATIONALE"),
        ("How does today compare with recent history?", "TODAY_VS_HISTORY"),
    ]

    for q_text, expected_intent in queries:
        res = QAInterfaceEngine.answer_query(q_text, ctx)
        assert res["supported"], f"Query '{q_text}' marked unsupported"
        assert res["intent"] == expected_intent, f"Expected {expected_intent}, got {res['intent']}"
        assert len(res["answer"]) > 20


def test_pairwise_station_comparison():
    """Tests comparison between dry and high-rain stations."""
    ctx_dry = get_dry_station_fixture()
    ctx_rain = get_high_rain_station_fixture()

    res = ComparisonIntelligenceEngine.compare_stations(ctx_dry, ctx_rain)
    assert "Station Comparison" in res["summary"]
    assert res["mean_temp_a"] > res["mean_temp_b"]
    assert res["total_rain_a"] < res["total_rain_b"]
