"""
Phase 8 25-Day Timeline Interpreter
Strictly enforces temporal partition semantics:
- D-12 to D-1: Ground-truth historical recorded observations (IMD or validated archive).
- D0: Today's current observed conditions (telemetry feed or null/unavailable fallback).
- D+1 to D+12: Multi-horizon model forecasts (never described as actual or observed).
"""

from typing import Dict, Any, List
from phase8_intelligence.core.contracts import AuthoritativeWeatherContextInput, TimelineDayStatus


class TimelineInterpreter:
    """Interprets and validates temporal boundaries across the 25-day continuum."""

    @staticmethod
    def interpret(context: AuthoritativeWeatherContextInput) -> Dict[str, Any]:
        past_days = [d for d in context.timeline_days if d.relative_day < 0]
        current_days = [d for d in context.timeline_days if d.relative_day == 0]
        forecast_days = [d for d in context.timeline_days if d.relative_day > 0]

        d0 = current_days[0] if current_days else None

        # Validate partition purity
        for d in past_days:
            if not d.is_observed and d.status != TimelineDayStatus.UNAVAILABLE:
                raise ValueError(f"Historical day {d.date} (rel {d.relative_day}) marked as unobserved!")
        for d in forecast_days:
            if d.is_observed:
                raise ValueError(f"Forecast day {d.date} (rel {d.relative_day}) marked as observed!")

        # Past trends
        past_temps = [d.temperature_avg for d in past_days if d.temperature_avg is not None]
        past_rains = [d.rainfall_amount for d in past_days if d.rainfall_amount is not None]

        mean_past_temp = round(sum(past_temps) / len(past_temps), 1) if past_temps else None
        total_past_rain = round(sum(past_rains), 1) if past_rains else None

        # Current status
        if d0 and d0.status == TimelineDayStatus.CURRENT and d0.temperature_avg is not None:
            current_desc = (
                f"Today (D0, {d0.date}) is recorded with observed average temperature {d0.temperature_avg:.1f}°C, "
                f"min {d0.temperature_min}°C, max {d0.temperature_max}°C, and rainfall {d0.rainfall_amount or 0.0:.1f} mm."
            )
        else:
            current_desc = (
                f"Today (D0, {context.forecast_origin}) observation is UNAVAILABLE due to offline telemetry or missing record. "
                f"No synthetic observation is generated."
            )

        narrative = (
            f"The 25-day operational timeline spans from {context.timeline_days[0].date} to {context.timeline_days[-1].date}. "
            f"It comprises {len(past_days)} historical observation days (D-12 to D-1), "
            f"1 current day (D0: {context.forecast_origin}), and {len(forecast_days)} future forecast horizons (T+1 to T+12). "
            f"Ground-truth historical average temperature was {mean_past_temp}°C with {total_past_rain} mm recorded rain."
        )

        return {
            "origin_date": context.forecast_origin,
            "historical_observed_count": len([d for d in past_days if d.temperature_avg is not None]),
            "current_day_available": d0 is not None and d0.temperature_avg is not None,
            "forecast_days_count": len(forecast_days),
            "historical_mean_temp": mean_past_temp,
            "historical_total_rain_mm": total_past_rain,
            "current_condition_summary": current_desc,
            "narrative": narrative,
        }
