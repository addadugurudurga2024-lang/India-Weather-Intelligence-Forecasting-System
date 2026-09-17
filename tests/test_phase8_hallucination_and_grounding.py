"""
Phase 8 Hallucination & Fabrication Test Suite
Tests anti-hallucination guards, strict grounding, forbidden certainty rejection,
and safe handling of unsupported topics.
"""

import pytest
from phase8_intelligence.fixtures.test_fixtures import (
    get_missing_telemetry_fixture,
    get_dry_station_fixture,
    get_high_rain_station_fixture,
)
from phase8_intelligence.core.engine import WeatherIntelligenceEngine
from phase8_intelligence.core.qa_interface import QAInterfaceEngine
from phase8_intelligence.core.confidence_language import ConfidenceLanguageEngine
from phase8_intelligence.core.grounding_validator import GroundingValidator, GroundingValidationError
from phase8_intelligence.core.contracts import DataStatus, TimelineDayStatus


def test_missing_current_telemetry_no_fabrication():
    """Confirms that when D0 is missing, the AI explicitly reports 'UNAVAILABLE' and does NOT invent a reading."""
    ctx = get_missing_telemetry_fixture()
    intel = WeatherIntelligenceEngine.generate_intelligence(ctx)

    assert intel.data_status == DataStatus.PARTIAL
    assert intel.observation_context.current_telemetry_status == "UNAVAILABLE"
    assert intel.observation_context.current_temp is None
    assert "UNAVAILABLE" in intel.observation_context.summary_text
    assert "No synthetic observations are substituted" in intel.observation_context.summary_text


def test_unsupported_humidity_question_rejected():
    """Confirms that querying about relative humidity returns a transparent limitation response."""
    ctx = get_dry_station_fixture()
    res = QAInterfaceEngine.answer_query("What is the relative humidity for tomorrow?", ctx)

    assert not res["supported"]
    assert res["intent"] == "UNSUPPORTED_TOPIC"
    assert "humidity" in res["unsupported_variable"]
    assert "Data unavailable" in res["answer"]


def test_unsupported_cloud_cover_question_rejected():
    """Confirms that querying about cloud cover returns a transparent limitation response."""
    ctx = get_dry_station_fixture()
    res = QAInterfaceEngine.answer_query("How much cloud cover will be present on Day 3?", ctx)

    assert not res["supported"]
    assert res["intent"] == "UNSUPPORTED_TOPIC"
    assert "Data unavailable" in res["answer"]


def test_unsupported_hourly_timing_question_rejected():
    """Confirms that hourly rain timing questions fail safely."""
    ctx = get_high_rain_station_fixture()
    res = QAInterfaceEngine.answer_query("What is the hourly precipitation schedule at 3 PM?", ctx)

    assert not res["supported"]
    assert res["intent"] == "UNSUPPORTED_TOPIC"
    assert "Data unavailable" in res["answer"]


def test_forbidden_certainty_words_rejected():
    """Confirms that forbidden certainty terms (e.g. 'guaranteed', '100% accurate') are detected and rejected."""
    clean_text = "The forecast indicates high likelihood of rain with widening uncertainty intervals."
    is_clean, violations = ConfidenceLanguageEngine.audit_text(clean_text)
    assert is_clean
    assert len(violations) == 0

    bad_text = "The rain forecast is guaranteed and 100% accurate without any doubt."
    is_clean, violations = ConfidenceLanguageEngine.audit_text(bad_text)
    assert not is_clean
    assert "guaranteed" in violations
    assert "100% accurate" in violations


def test_grounding_validator_blocks_invented_station():
    """Confirms that an output referencing an inconsistent station ID is caught by the validator."""
    ctx = get_dry_station_fixture()
    intel = WeatherIntelligenceEngine.generate_intelligence(ctx)

    # Corrupt station ID in output
    intel.station = intel.station.model_copy(update={"station_id": "FAKE_STATION_999"})
    is_valid, errors = GroundingValidator.validate(intel, ctx)
    assert not is_valid
    assert any("Station ID mismatch" in e for e in errors)


def test_grounding_validator_blocks_probability_exceedance():
    """Confirms that an output with probability > 1.0 is rejected."""
    ctx = get_dry_station_fixture()
    intel = WeatherIntelligenceEngine.generate_intelligence(ctx)

    # Corrupt probability to 1.50
    intel.rainfall_insights.highest_probability = 1.50
    is_valid, errors = GroundingValidator.validate(intel, ctx)
    assert not is_valid
    assert any("outside [0, 1]" in e for e in errors)


def test_external_benchmark_not_labeled_ground_truth():
    """Confirms external benchmark comparisons explicitly disclaim being ground truth."""
    from phase8_intelligence.core.comparison_engine import ComparisonIntelligenceEngine
    text = ComparisonIntelligenceEngine.compare_with_external_benchmark(24.5, 23.0, 1)
    assert "external benchmark" in text.lower()
    assert "NOT verified ground truth" in text
