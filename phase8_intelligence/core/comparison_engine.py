"""
Phase 8 Comparison Intelligence Engine
Supports controlled meteorological comparisons:
1. Station vs Station
2. Today vs Recent History (D0 vs D-12..D-1)
3. Near-Term vs Mid-Term (T+1 vs T+7)
4. Model Forecast vs External Benchmark (strictly labeled as 'external benchmark', never ground truth)
"""

from typing import Dict, Any, Optional
from phase8_intelligence.core.contracts import AuthoritativeWeatherContextInput, TimelineDayStatus


class ComparisonIntelligenceEngine:
    """Performs pairwise, grounded meteorological comparisons."""

    @staticmethod
    def compare_today_vs_history(context: AuthoritativeWeatherContextInput) -> Dict[str, Any]:
        past_days = [d for d in context.timeline_days if d.relative_day < 0 and d.temperature_avg is not None]
        d0 = next((d for d in context.timeline_days if d.relative_day == 0), None)

        if not d0 or d0.temperature_avg is None:
            return {
                "comparison_possible": False,
                "summary": "Cannot compare today vs history: today's (D0) observation is UNAVAILABLE.",
            }

        if not past_days:
            return {
                "comparison_possible": False,
                "summary": "Cannot compare today vs history: historical observations (D-12..D-1) are UNAVAILABLE.",
            }

        past_mean_t = sum(d.temperature_avg for d in past_days) / len(past_days)
        delta_t = round(d0.temperature_avg - past_mean_t, 1)
        direction = "warmer" if delta_t > 0 else "cooler"

        past_mean_rain = sum((d.rainfall_amount or 0.0) for d in past_days) / len(past_days)
        d0_rain = d0.rainfall_amount or 0.0
        delta_rain = round(d0_rain - past_mean_rain, 1)

        summary = (
            f"Today ({d0.date}) observed average temperature of {d0.temperature_avg:.1f}°C is "
            f"{abs(delta_t):.1f}°C {direction} than the preceding 12-day historical average of {past_mean_t:.1f}°C. "
            f"Recorded rainfall today is {d0_rain:.1f} mm compared to a recent daily average of {past_mean_rain:.1f} mm."
        )

        return {
            "comparison_possible": True,
            "today_temp": d0.temperature_avg,
            "past_mean_temp": round(past_mean_t, 1),
            "temp_delta_c": delta_t,
            "today_rain_mm": d0_rain,
            "past_mean_rain_mm": round(past_mean_rain, 1),
            "summary": summary,
        }

    @staticmethod
    def compare_t1_vs_t7(context: AuthoritativeWeatherContextInput) -> Dict[str, Any]:
        forecast_days = [d for d in context.timeline_days if d.relative_day > 0]
        t1 = next((d for d in forecast_days if d.relative_day == 1), None)
        t7 = next((d for d in forecast_days if d.relative_day == 7), None)

        if not t1 or not t7 or t1.temperature_avg is None or t7.temperature_avg is None:
            return {
                "comparison_possible": False,
                "summary": "Cannot compare T+1 vs T+7: one or both horizons are unavailable.",
            }

        delta_t = round(t7.temperature_avg - t1.temperature_avg, 1)
        direction = "warmer" if delta_t > 0 else "cooler"
        delta_p = round((t7.rain_probability or 0.0) - (t1.rain_probability or 0.0), 3)

        summary = (
            f"Comparing Day 1 (T+1, {t1.date}) with Day 7 (T+7, {t7.date}): "
            f"Average temperature transitions from {t1.temperature_avg:.1f}°C to {t7.temperature_avg:.1f}°C ({abs(delta_t):.1f}°C {direction}). "
            f"Rain probability shifts from {(t1.rain_probability or 0.0) * 100:.1f}% to {(t7.rain_probability or 0.0) * 100:.1f}% "
            f"({delta_p * 100:+.1f}%). Forecast uncertainty expands significantly as horizon increases."
        )

        return {
            "comparison_possible": True,
            "t1_temp": t1.temperature_avg,
            "t7_temp": t7.temperature_avg,
            "temp_delta_c": delta_t,
            "t1_rain_prob": t1.rain_probability,
            "t7_rain_prob": t7.rain_probability,
            "summary": summary,
        }

    @staticmethod
    def compare_stations(ctx_a: AuthoritativeWeatherContextInput, ctx_b: AuthoritativeWeatherContextInput) -> Dict[str, Any]:
        """Compares two distinct stations across the 12-day forecast window."""
        fc_a = [d for d in ctx_a.timeline_days if d.relative_day > 0 and d.temperature_avg is not None]
        fc_b = [d for d in ctx_b.timeline_days if d.relative_day > 0 and d.temperature_avg is not None]

        if not fc_a or not fc_b:
            return {"summary": "Cannot compare stations: one or both lack forecast data."}

        mean_ta = round(sum(d.temperature_avg for d in fc_a) / len(fc_a), 1)
        mean_tb = round(sum(d.temperature_avg for d in fc_b) / len(fc_b), 1)
        total_ra = round(sum((d.rainfall_amount or 0.0) for d in fc_a), 1)
        total_rb = round(sum((d.rainfall_amount or 0.0) for d in fc_b), 1)

        summary = (
            f"Station Comparison: {ctx_a.station.station_name} ({ctx_a.station.state}) vs "
            f"{ctx_b.station.station_name} ({ctx_b.station.state}). "
            f"12-day mean forecast temperature: {ctx_a.station.station_name} is {mean_ta:.1f}°C vs "
            f"{ctx_b.station.station_name} at {mean_tb:.1f}°C (delta {round(mean_ta - mean_tb, 1):+.1f}°C). "
            f"Cumulative projected rainfall: {total_ra:.1f} mm vs {total_rb:.1f} mm."
        )

        return {
            "station_a": ctx_a.station.station_name,
            "station_b": ctx_b.station.station_name,
            "mean_temp_a": mean_ta,
            "mean_temp_b": mean_tb,
            "total_rain_a": total_ra,
            "total_rain_b": total_rb,
            "summary": summary,
        }

    @staticmethod
    def compare_with_external_benchmark(model_temp: float, external_temp: float, horizon: int) -> str:
        """Compares model prediction with external benchmark. Strictly forbids labeling benchmark as ground truth."""
        delta = round(model_temp - external_temp, 1)
        return (
            f"For horizon T+{horizon}, the primary XGBoost model predicts {model_temp:.1f}°C while the "
            f"external benchmark reports {external_temp:.1f}°C (discrepancy of {delta:+.1f}°C). "
            f"Note: The external benchmark represents an independent numerical weather prediction reference, "
            f"NOT verified ground truth."
        )
