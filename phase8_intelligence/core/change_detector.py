"""
Phase 8 Forecast Change Detection Engine
Calculates horizon-to-horizon derivatives:
- Daily temperature delta: T(h+1) - T(h)
- Daily rain probability step changes
- Interval width progression
Reports exact magnitude and directional trends without hand-waving.
"""

from typing import List, Dict, Any
from phase8_intelligence.core.contracts import AuthoritativeWeatherContextInput


class ForecastChangeDetector:
    """Computes horizon-to-horizon derivatives and shifts."""

    @staticmethod
    def detect_changes(context: AuthoritativeWeatherContextInput) -> List[str]:
        forecast_days = [d for d in context.timeline_days if d.relative_day > 0 and d.temperature_avg is not None]
        if len(forecast_days) < 2:
            return ["Insufficient horizons to calculate day-over-day changes."]

        changes: List[str] = []

        # 1. Check for abrupt temperature shifts between consecutive days (|delta| >= 2.0 C)
        for i in range(len(forecast_days) - 1):
            curr_d = forecast_days[i]
            next_d = forecast_days[i + 1]
            delta_t = round(next_d.temperature_avg - curr_d.temperature_avg, 1)
            if abs(delta_t) >= 2.0:
                direction = "rise" if delta_t > 0 else "drop"
                changes.append(
                    f"Abrupt temperature {direction} of {abs(delta_t):.1f}°C between T+{curr_d.relative_day} "
                    f"({curr_d.temperature_avg:.1f}°C) and T+{next_d.relative_day} ({next_d.temperature_avg:.1f}°C)."
                )

        # 2. Check for rain probability surge between consecutive days (delta >= +0.25)
        for i in range(len(forecast_days) - 1):
            curr_d = forecast_days[i]
            next_d = forecast_days[i + 1]
            p_curr = curr_d.rain_probability or 0.0
            p_next = next_d.rain_probability or 0.0
            delta_p = round(p_next - p_curr, 3)
            if delta_p >= 0.25:
                changes.append(
                    f"Significant rain probability increase (+{delta_p * 100:.1f}%) from T+{curr_d.relative_day} "
                    f"({p_curr * 100:.1f}%) to T+{next_d.relative_day} ({p_next * 100:.1f}%)."
                )
            elif delta_p <= -0.25:
                changes.append(
                    f"Rapid drying signal: rain probability decreases by {abs(delta_p) * 100:.1f}% from T+{curr_d.relative_day} "
                    f"({p_curr * 100:.1f}%) to T+{next_d.relative_day} ({p_next * 100:.1f}%)."
                )

        # 3. Interval width change summary
        t1 = next((d for d in forecast_days if d.relative_day == 1), None)
        t12 = next((d for d in forecast_days if d.relative_day == 12), None)
        if t1 and t12 and t1.uncertainty and t12.uncertainty:
            w1 = round(t1.uncertainty.temp_interval_80[1] - t1.uncertainty.temp_interval_80[0], 1)
            w12 = round(t12.uncertainty.temp_interval_80[1] - t12.uncertainty.temp_interval_80[0], 1)
            changes.append(
                f"Prediction interval width increases from {w1:.1f}°C at T+1 to {w12:.1f}°C at T+12 "
                f"(+{round(w12 - w1, 1):.1f}°C expansion due to multi-step forecast dispersion)."
            )

        if not changes:
            changes.append("No abrupt day-to-day shifts detected; forecast displays smooth temporal evolution.")

        return changes
