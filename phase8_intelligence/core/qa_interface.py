"""
Phase 8 Question-Answering Interface Contract
Handles structured meteorological Q&A routing.
SUPPORTED INTENTS:
1. FORECAST_SUMMARY ("What is the forecast?")
2. RAIN_OCCURRENCE ("Will rain occur?")
3. TEMPERATURE_TREND ("How does the temperature change?")
4. PEAK_RAIN_DAY ("Which day has the highest rain probability?")
5. UNCERTAINTY_QUERY ("How uncertain is the forecast?")
6. TODAY_VS_HISTORY ("How does today compare with recent observations?")
7. RISK_RATIONALE ("Why is this forecast considered high risk?")
UNSUPPORTED INTENTS:
Humidity, cloud cover, hourly timing, satellite/radar, medical/aviation advice.
Transparently emits structured limitation response with 'Data unavailable'.
"""

import re
from typing import Dict, Any, List, Optional
from phase8_intelligence.core.contracts import AuthoritativeWeatherContextInput
from phase8_intelligence.core.schemas import WeatherIntelligenceOutput
from phase8_intelligence.core.temperature_intel import TemperatureIntelligenceEngine
from phase8_intelligence.core.rainfall_intel import RainfallIntelligenceEngine
from phase8_intelligence.core.risk_engine import PrecipitationRiskEngine
from phase8_intelligence.core.comparison_engine import ComparisonIntelligenceEngine
from phase8_intelligence.core.confidence_language import ConfidenceLanguageEngine


UNSUPPORTED_TOPICS = [
    "humidity",
    "relative humidity",
    "cloud cover",
    "clouds",
    "sunshine",
    "solar radiation",
    "uv index",
    "air quality",
    "aqi",
    "pollution",
    "hourly",
    "hour by hour",
    "radar",
    "satellite",
    "cyclone tracking",
    "typhoon",
    "flood warning",
    "medical",
    "health advice",
    "stock",
    "flight delay",
]


class QAInterfaceEngine:
    """Answers weather queries with strict zero-hallucination routing."""

    @staticmethod
    def answer_query(query: str, context: AuthoritativeWeatherContextInput) -> Dict[str, Any]:
        query_clean = query.strip().lower()

        # 1. Check for unsupported variables/topics first
        for topic in UNSUPPORTED_TOPICS:
            pattern = rf"\b{re.escape(topic)}\b"
            if re.search(pattern, query_clean):
                return {
                    "supported": False,
                    "query": query,
                    "intent": "UNSUPPORTED_TOPIC",
                    "unsupported_variable": topic,
                    "answer": (
                        f"Query regarding '{topic}' cannot be answered. The India Weather Forecasting & Intelligence System "
                        f"is strictly validated for daily temperature, precipitation occurrence & amount, wind speed, and surface pressure. "
                        f"Variable '{topic}' is not modeled by the Phase 7 multi-horizon engine. Data unavailable."
                    ),
                }

        # 2. Match supported intents
        # Intent: PEAK_RAIN_DAY
        if any(k in query_clean for k in ["highest rain", "peak rain", "which day", "most rain", "maximum rain"]):
            rain = RainfallIntelligenceEngine.analyze(context)
            answer = (
                f"Peak rain occurrence probability is {rain.highest_probability * 100:.1f}% "
                f"at horizon {rain.highest_prob_horizon} ({rain.highest_prob_day}). "
                f"Maximum predicted single-day accumulation is {rain.max_single_day_rainfall_mm:.1f} mm "
                f"on {rain.max_rainfall_day}."
            )
            return {"supported": True, "query": query, "intent": "PEAK_RAIN_DAY", "answer": answer}

        # Intent: RAIN_OCCURRENCE
        if any(k in query_clean for k in ["will rain", "rain occur", "rainfall", "chance of rain", "precipitation"]):
            rain = RainfallIntelligenceEngine.analyze(context)
            risk = PrecipitationRiskEngine.evaluate(context)
            answer = (
                f"{'Rain is predicted' if rain.rain_expected else 'No significant rain is predicted'}. "
                f"Peak occurrence probability reaches {rain.highest_probability * 100:.1f}% on {rain.highest_prob_day} "
                f"({rain.highest_prob_horizon}) with cumulative 12-day accumulation of {rain.total_expected_rainfall_mm:.1f} mm. "
                f"Precipitation risk category is evaluated as {risk.risk_level.value}."
            )
            return {"supported": True, "query": query, "intent": "RAIN_OCCURRENCE", "answer": answer}

        # Intent: TEMPERATURE_TREND
        if any(k in query_clean for k in ["temperature", "temp", "warm", "cool", "heat", "cold"]):
            temp = TemperatureIntelligenceEngine.analyze(context)
            answer = (
                f"Temperature outlook: {temp.overall_trend.title()} trend with {temp.trend_delta_c or 0.0:+.1f}°C expected change. "
                f"Daily average temperatures range from {temp.forecast_avg_min:.1f}°C to {temp.forecast_avg_max:.1f}°C "
                f"across the 12-day forecast. Mean diurnal spread is {temp.diurnal_range_mean:.1f}°C."
            )
            return {"supported": True, "query": query, "intent": "TEMPERATURE_TREND", "answer": answer}

        # Intent: UNCERTAINTY_QUERY
        if any(k in query_clean for k in ["uncertain", "confidence", "prediction interval", "accurate", "reliability"]):
            t1 = next((d for d in context.timeline_days if d.relative_day == 1), None)
            t12 = next((d for d in context.timeline_days if d.relative_day == 12), None)
            w1 = 2.4
            w12 = 4.2
            if t1 and t1.uncertainty:
                w1 = t1.uncertainty.temp_interval_80[1] - t1.uncertainty.temp_interval_80[0]
            if t12 and t12.uncertainty:
                w12 = t12.uncertainty.temp_interval_80[1] - t12.uncertainty.temp_interval_80[0]
            conf = ConfidenceLanguageEngine.generate_confidence_statement(w1, w12)
            return {"supported": True, "query": query, "intent": "UNCERTAINTY_QUERY", "answer": conf.statement}

        # Intent: TODAY_VS_HISTORY
        if any(k in query_clean for k in ["today compare", "compare with recent", "history", "past", "yesterday"]):
            comp = ComparisonIntelligenceEngine.compare_today_vs_history(context)
            return {"supported": True, "query": query, "intent": "TODAY_VS_HISTORY", "answer": comp["summary"]}

        # Intent: RISK_RATIONALE
        if any(k in query_clean for k in ["risk", "why is this", "danger", "hazard"]):
            risk = PrecipitationRiskEngine.evaluate(context)
            answer = f"Precipitation risk is categorized as {risk.risk_level.value}. {risk.rationale} Basis: {risk.threshold_basis}"
            return {"supported": True, "query": query, "intent": "RISK_RATIONALE", "answer": answer}

        # Intent: FORECAST_SUMMARY (Default supported fallback)
        if any(k in query_clean for k in ["forecast", "weather", "outlook", "overview", "what is"]):
            t1 = next((d for d in context.timeline_days if d.relative_day == 1), None)
            temp = TemperatureIntelligenceEngine.analyze(context)
            rain = RainfallIntelligenceEngine.analyze(context)
            answer = (
                f"12-day forecast for {context.station.station_name}: Daily average temperatures span "
                f"{temp.forecast_avg_min:.1f}°C to {temp.forecast_avg_max:.1f}°C ({temp.overall_trend.lower()} trend). "
                f"Peak rain probability is {rain.highest_probability * 100:.1f}% with {rain.total_expected_rainfall_mm:.1f} mm "
                f"total predicted rain."
            )
            return {"supported": True, "query": query, "intent": "FORECAST_SUMMARY", "answer": answer}

        # Catch-all unsupported
        return {
            "supported": False,
            "query": query,
            "intent": "UNSUPPORTED_INTENT",
            "answer": (
                f"The question '{query}' is outside the structured capability of the weather intelligence system. "
                f"Please ask about 12-day temperature trends, rainfall probability, precipitation risk, "
                f"uncertainty intervals, or station comparisons."
            ),
        }
