"""
Phase 8 Rainfall Intelligence Engine
Generates grounded rainfall insights from calibrated occurrence probabilities
and regression amounts.
CRITICAL RULE:
Strictly distinguishes Probability of Occurrence (P(rain > 0)) from Predicted Rainfall Amount (mm).
Never conflates percentage probability with physical accumulation.
"""

from typing import List, Optional, Tuple
from phase8_intelligence.core.contracts import AuthoritativeWeatherContextInput, DataStatus
from phase8_intelligence.core.schemas import RainfallInsights
from phase8_intelligence.core.availability import DataAvailabilityAssessment


class RainfallIntelligenceEngine:
    """Interprets multi-horizon precipitation models."""

    @staticmethod
    def analyze(context: AuthoritativeWeatherContextInput) -> RainfallInsights:
        availability = DataAvailabilityAssessment(context.timeline_days)
        forecast_days = [d for d in context.timeline_days if d.relative_day > 0]

        if not forecast_days:
            return RainfallInsights(
                data_status=DataStatus.UNAVAILABLE,
                rain_expected=False,
                highest_probability=0.0,
                total_expected_rainfall_mm=0.0,
                max_single_day_rainfall_mm=0.0,
                insights=["Rainfall forecast data is unavailable."]
            )

        # Probabilities and amounts
        probs = [(d.relative_day, d.date, d.rain_probability or 0.0) for d in forecast_days]
        amounts = [(d.relative_day, d.date, d.rainfall_amount or 0.0) for d in forecast_days]

        # Max probability
        max_prob_item = max(probs, key=lambda x: x[2]) if probs else (1, "", 0.0)
        highest_prob = round(max_prob_item[2], 3)
        highest_prob_day = max_prob_item[1]
        highest_prob_horizon = f"T+{max_prob_item[0]}"

        # Max and total amount
        max_amt_item = max(amounts, key=lambda x: x[2]) if amounts else (1, "", 0.0)
        max_single_amt = round(max_amt_item[2], 1)
        max_amt_day = max_amt_item[1]
        total_amt = round(sum(a[2] for a in amounts), 1)

        # Wet/dry spells (using standard classification threshold tau = 0.30 or rain_binary)
        rain_flags = [(d.rain_binary if d.rain_binary is not None else (d.rain_probability or 0.0) >= 0.30) for d in forecast_days]

        # Calculate max consecutive rain days and dry days
        max_consec_rain = 0
        curr_rain = 0
        max_consec_dry = 0
        curr_dry = 0

        for r in rain_flags:
            if r:
                curr_rain += 1
                curr_dry = 0
                max_consec_rain = max(max_consec_rain, curr_rain)
            else:
                curr_dry += 1
                curr_rain = 0
                max_consec_dry = max(max_consec_dry, curr_dry)

        rain_expected = any(r for r in rain_flags) or total_amt > 0.5

        # Narrative insights
        insights: List[str] = []

        if highest_prob >= 0.50:
            insights.append(
                f"Elevated rain probability observed: peak occurrence probability is {highest_prob * 100:.1f}% "
                f"at horizon {highest_prob_horizon} ({highest_prob_day}). Note that probability indicates likelihood of occurrence, not rainfall volume."
            )
        elif highest_prob >= 0.25:
            insights.append(
                f"Moderate rain probability indicated: peak occurrence probability is {highest_prob * 100:.1f}% "
                f"at horizon {highest_prob_horizon} ({highest_prob_day})."
            )
        else:
            insights.append(
                f"Dry conditions dominant: peak rain occurrence probability remains low across all 12 days "
                f"(maximum {highest_prob * 100:.1f}% at {highest_prob_horizon})."
            )

        if total_amt > 0.0:
            insights.append(
                f"Total cumulative predicted rainfall over the 12-day window is {total_amt:.1f} mm, "
                f"with maximum single-day accumulation of {max_single_amt:.1f} mm expected on {max_amt_day}."
            )
        else:
            insights.append(
                "No measurable precipitation accumulation (0.0 mm) is predicted across the 12-day forecast period."
            )

        if max_consec_rain >= 2:
            insights.append(
                f"Forecast exhibits a wet spell pattern with up to {max_consec_rain} consecutive days of elevated rain probability."
            )
        elif max_consec_dry >= 5:
            insights.append(
                f"Forecast exhibits sustained dry persistence with at least {max_consec_dry} consecutive dry days."
            )

        return RainfallInsights(
            data_status=availability.overall_system_status,
            rain_expected=rain_expected,
            highest_probability=highest_prob,
            highest_prob_day=highest_prob_day,
            highest_prob_horizon=highest_prob_horizon,
            total_expected_rainfall_mm=total_amt,
            max_single_day_rainfall_mm=max_single_amt,
            max_rainfall_day=max_amt_day,
            consecutive_rain_days=max_consec_rain,
            consecutive_dry_days=max_consec_dry,
            insights=insights,
        )
