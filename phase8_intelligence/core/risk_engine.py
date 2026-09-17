"""
Phase 8 Precipitation Risk Interpretation Engine
Maps calibrated rain probabilities and regression rainfall accumulations to
deterministic risk categories (LOW, MODERATE, HIGH) based on documented project thresholds.
Does not invent scientifically unsupported risk claims.
"""

from typing import Tuple, Optional
from phase8_intelligence.core.contracts import AuthoritativeWeatherContextInput
from phase8_intelligence.core.schemas import RiskLevel, PrecipitationRiskOutput


# Documented meteorological thresholds
PROB_MODERATE_THRESHOLD = 0.25   # Below 25% is Low occurrence likelihood
PROB_HIGH_THRESHOLD = 0.60       # Above 60% is High occurrence likelihood
AMT_MODERATE_MM = 2.5            # 2.5 mm/day IMD threshold for measurable precipitation event
AMT_HIGH_MM = 15.5               # 15.5 mm/day IMD threshold for rather heavy precipitation


class PrecipitationRiskEngine:
    """Interprets precipitation risk deterministically."""

    @staticmethod
    def evaluate(context: AuthoritativeWeatherContextInput) -> PrecipitationRiskOutput:
        forecast_days = [d for d in context.timeline_days if d.relative_day > 0]

        if not forecast_days:
            return PrecipitationRiskOutput(
                risk_level=RiskLevel.LOW,
                max_rain_probability=0.0,
                max_predicted_rainfall_mm=0.0,
                rationale="No forecast days available to assess precipitation risk.",
                threshold_basis="Default minimal baseline (Data unavailable).",
            )

        max_prob = 0.0
        max_amt = 0.0
        peak_day: Optional[str] = None
        peak_h: Optional[str] = None

        for d in forecast_days:
            p = d.rain_probability or 0.0
            amt = d.rainfall_amount or 0.0
            if p > max_prob:
                max_prob = p
                peak_day = d.date
                peak_h = f"T+{d.relative_day}"
            if amt > max_amt:
                max_amt = amt

        max_prob = round(max_prob, 3)
        max_amt = round(max_amt, 1)

        # Categorization logic
        if max_prob >= PROB_HIGH_THRESHOLD or max_amt >= AMT_HIGH_MM:
            level = RiskLevel.HIGH
            rationale = (
                f"High precipitation risk driven by elevated probability of {max_prob * 100:.1f}% "
                f"or expected peak accumulation of {max_amt:.1f} mm at horizon {peak_h} ({peak_day}). "
                f"Indicates high likelihood of impactful wet weather."
            )
        elif max_prob >= PROB_MODERATE_THRESHOLD or max_amt >= AMT_MODERATE_MM:
            level = RiskLevel.MODERATE
            rationale = (
                f"Moderate precipitation risk with peak occurrence probability of {max_prob * 100:.1f}% "
                f"and peak daily accumulation of {max_amt:.1f} mm at horizon {peak_h} ({peak_day}). "
                f"Scattered light-to-moderate showers are possible."
            )
        else:
            level = RiskLevel.LOW
            rationale = (
                f"Low precipitation risk across the forecast window. Peak occurrence probability is {max_prob * 100:.1f}% "
                f"and maximum daily accumulation is {max_amt:.1f} mm. Substantial rainfall is unlikely."
            )

        threshold_basis = (
            f"Evaluated against IMD meteorological benchmarks: "
            f"Low (Prob < {PROB_MODERATE_THRESHOLD*100:.0f}%, Rain < {AMT_MODERATE_MM}mm), "
            f"Moderate (Prob {PROB_MODERATE_THRESHOLD*100:.0f}–{PROB_HIGH_THRESHOLD*100:.0f}%, Rain {AMT_MODERATE_MM}–{AMT_HIGH_MM}mm), "
            f"High (Prob > {PROB_HIGH_THRESHOLD*100:.0f}% or Rain >= {AMT_HIGH_MM}mm)."
        )

        return PrecipitationRiskOutput(
            risk_level=level,
            max_rain_probability=max_prob,
            max_predicted_rainfall_mm=max_amt,
            peak_risk_day=peak_day,
            peak_risk_horizon=peak_h,
            rationale=rationale,
            threshold_basis=threshold_basis,
        )
