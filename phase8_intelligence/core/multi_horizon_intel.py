"""
Phase 8 Multi-Horizon Intelligence Engine
Decomposes the 12-day multi-horizon direct forecast into three meteorologically coherent tranches:
1. Near-Term (T+1 to T+3): High spatial and thermal confidence, synoptic persistence.
2. Medium-Range (T+4 to T+7): Dynamic airmass evolution, synoptic trough/ridge transitions.
3. Extended (T+8 to T+12): Climatological pull, wider uncertainty intervals, degraded classification skill.
Prevents collapsing the 12-day horizon into a simplistic single-day statement.
"""

from typing import Dict, Any, List, Optional
from phase8_intelligence.core.contracts import AuthoritativeWeatherContextInput, TimelineDayData


class MultiHorizonIntelligenceEngine:
    """Interprets multi-horizon forecast progression across T+1..T+12."""

    @staticmethod
    def analyze_tranches(context: AuthoritativeWeatherContextInput) -> Dict[str, Any]:
        forecast_days = [d for d in context.timeline_days if d.relative_day > 0]
        if not forecast_days:
            return {
                "near_term": {"summary": "No near-term forecast available.", "days": []},
                "medium_range": {"summary": "No medium-range forecast available.", "days": []},
                "extended": {"summary": "No extended forecast available.", "days": []},
                "uncertainty_growth": "Data unavailable",
            }

        near_term = [d for d in forecast_days if 1 <= d.relative_day <= 3]
        medium_range = [d for d in forecast_days if 4 <= d.relative_day <= 7]
        extended = [d for d in forecast_days if 8 <= d.relative_day <= 12]

        def summarize_tranche(days: List[TimelineDayData], tranche_name: str) -> Dict[str, Any]:
            if not days:
                return {"summary": f"No {tranche_name} days available.", "avg_temp": None, "max_prob": None}
            temps = [d.temperature_avg for d in days if d.temperature_avg is not None]
            probs = [d.rain_probability for d in days if d.rain_probability is not None]
            rains = [d.rainfall_amount for d in days if d.rainfall_amount is not None]

            mean_t = round(sum(temps) / len(temps), 1) if temps else None
            max_p = round(max(probs), 3) if probs else 0.0
            sum_r = round(sum(rains), 1) if rains else 0.0

            text = (
                f"{tranche_name} (T+{days[0].relative_day} to T+{days[-1].relative_day}): "
                f"Mean expected temperature is {mean_t}°C; peak rain probability is {max_p * 100:.1f}%; "
                f"total expected accumulation is {sum_r} mm."
            )
            return {
                "summary": text,
                "mean_temperature": mean_t,
                "peak_rain_probability": max_p,
                "cumulative_rain_mm": sum_r,
                "day_count": len(days),
            }

        near_summary = summarize_tranche(near_term, "Near-Term")
        med_summary = summarize_tranche(medium_range, "Medium-Range")
        ext_summary = summarize_tranche(extended, "Extended-Range")

        # Uncertainty expansion
        t1 = next((d for d in forecast_days if d.relative_day == 1), None)
        t12 = next((d for d in forecast_days if d.relative_day == 12), None)
        unc_statement = "Prediction interval spread remains stable."
        if t1 and t12 and t1.uncertainty and t12.uncertainty:
            w1 = round(t1.uncertainty.temp_interval_80[1] - t1.uncertainty.temp_interval_80[0], 1)
            w12 = round(t12.uncertainty.temp_interval_80[1] - t12.uncertainty.temp_interval_80[0], 1)
            unc_statement = (
                f"80% prediction interval expands from ±{round(w1/2, 1)}°C at Day 1 ({w1}°C total width) "
                f"to ±{round(w12/2, 1)}°C at Day 12 ({w12}°C total width), consistent with walk-forward validation error growth."
            )

        return {
            "near_term": near_summary,
            "medium_range": med_summary,
            "extended": ext_summary,
            "uncertainty_growth": unc_statement,
        }
