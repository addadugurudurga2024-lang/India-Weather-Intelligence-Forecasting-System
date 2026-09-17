"""
Phase 8 Recommendation-Safe Intelligence Engine
Generates conservative, evidence-based practical implications.
CRITICAL SAFETY BOUNDARY:
Never issues medical, emergency evacuation, high-stakes agricultural chemical,
or aviation flight dispatch instructions.
Limits implications strictly to general planning caveats grounded in verified weather data.
"""

from typing import List
from phase8_intelligence.core.contracts import AuthoritativeWeatherContextInput
from phase8_intelligence.core.schemas import RiskLevel
from phase8_intelligence.core.risk_engine import PrecipitationRiskEngine


class RecommendationSafeEngine:
    """Produces safe, conservative observational guidance."""

    @staticmethod
    def generate_safe_implications(context: AuthoritativeWeatherContextInput) -> List[str]:
        risk = PrecipitationRiskEngine.evaluate(context)
        forecast_days = [d for d in context.timeline_days if d.relative_day > 0 and d.temperature_avg is not None]

        implications: List[str] = []

        if risk.risk_level == RiskLevel.HIGH:
            implications.append(
                f"Rain probability is elevated (peak {risk.max_rain_probability * 100:.1f}%, accumulation {risk.max_predicted_rainfall_mm:.1f} mm). "
                f"Outdoor activities should account for a high likelihood of wet weather on {risk.peak_risk_day}."
            )
        elif risk.risk_level == RiskLevel.MODERATE:
            implications.append(
                f"The forecast indicates a moderate likelihood of precipitation (peak {risk.max_rain_probability * 100:.1f}%). "
                f"Scattered rain events may occur."
            )
        else:
            implications.append(
                "Dry weather is expected to persist across the near-term forecast horizons."
            )

        # Temperature extremes caution (purely observational)
        if forecast_days:
            max_t = max((d.temperature_max or d.temperature_avg) for d in forecast_days)
            min_t = min((d.temperature_min or d.temperature_avg) for d in forecast_days)

            if max_t >= 40.0:
                implications.append(
                    f"Daytime maximum temperatures are forecast to reach {max_t:.1f}°C. High heat conditions are expected."
                )
            elif min_t <= 5.0:
                implications.append(
                    f"Overnight minimum temperatures are forecast to drop to {min_t:.1f}°C. Cool conditions are anticipated."
                )

        implications.append(
            "Forecast uncertainty increases toward Day 12; extended planning should be updated as near-term updates arrive."
        )

        return implications
