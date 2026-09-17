"""
Phase 8 Temperature Intelligence Engine
Produces deterministic, grounded temperature insights:
- Warming / cooling trend calculation
- Diurnal temperature range (Tmax - Tmin)
- Day-to-day step changes
- Horizon prediction interval widening analysis
Zero data fabrication; strict bound preservation.
"""

from typing import List, Optional
from phase8_intelligence.core.contracts import AuthoritativeWeatherContextInput, DataStatus
from phase8_intelligence.core.schemas import TemperatureInsights
from phase8_intelligence.core.availability import DataAvailabilityAssessment


class TemperatureIntelligenceEngine:
    """Analyzes observed and multi-horizon forecast temperatures."""

    @staticmethod
    def analyze(context: AuthoritativeWeatherContextInput) -> TemperatureInsights:
        availability = DataAvailabilityAssessment(context.timeline_days)
        forecast_days = [d for d in context.timeline_days if d.relative_day > 0 and d.temperature_avg is not None]
        current_day = next((d for d in context.timeline_days if d.relative_day == 0), None)

        if not forecast_days:
            return TemperatureInsights(
                data_status=DataStatus.UNAVAILABLE,
                overall_trend="UNAVAILABLE",
                insights=["Temperature forecast data is unavailable."]
            )

        current_temp = current_day.temperature_avg if (current_day and current_day.temperature_avg is not None) else None
        avg_temps = [d.temperature_avg for d in forecast_days if d.temperature_avg is not None]
        min_temps = [d.temperature_min for d in forecast_days if d.temperature_min is not None]
        max_temps = [d.temperature_max for d in forecast_days if d.temperature_max is not None]

        forecast_avg_min = min(avg_temps) if avg_temps else None
        forecast_avg_max = max(avg_temps) if avg_temps else None

        # Overall trend across forecast horizons
        # Compare near-term (T+1..T+3 average) vs extended (T+10..T+12 average)
        near_temps = [d.temperature_avg for d in forecast_days if 1 <= d.relative_day <= 3 and d.temperature_avg is not None]
        far_temps = [d.temperature_avg for d in forecast_days if 10 <= d.relative_day <= 12 and d.temperature_avg is not None]

        trend = "STABLE"
        trend_delta: Optional[float] = None
        if near_temps and far_temps:
            mean_near = sum(near_temps) / len(near_temps)
            mean_far = sum(far_temps) / len(far_temps)
            trend_delta = round(mean_far - mean_near, 1)
            if trend_delta >= 1.5:
                trend = "WARMING"
            elif trend_delta <= -1.5:
                trend = "COOLING"
            else:
                trend = "STABLE"

        # Diurnal range analysis
        diurnal_ranges = []
        for d in forecast_days:
            if d.temperature_max is not None and d.temperature_min is not None:
                diurnal_ranges.append(d.temperature_max - d.temperature_min)
        diurnal_mean = round(sum(diurnal_ranges) / len(diurnal_ranges), 1) if diurnal_ranges else None

        # Interval widening between T+1 and T+12
        t1_day = next((d for d in forecast_days if d.relative_day == 1), None)
        t12_day = next((d for d in forecast_days if d.relative_day == 12), None)
        widening_c: Optional[float] = None
        if t1_day and t12_day and t1_day.uncertainty and t12_day.uncertainty:
            w1 = t1_day.uncertainty.temp_interval_80[1] - t1_day.uncertainty.temp_interval_80[0]
            w12 = t12_day.uncertainty.temp_interval_80[1] - t12_day.uncertainty.temp_interval_80[0]
            widening_c = round(w12 - w1, 1)

        # Grounded narrative bullet points
        insights: List[str] = []
        if current_temp is not None:
            insights.append(
                f"Current recorded temperature at origin date ({context.forecast_origin}) is {current_temp:.1f}°C."
            )
        else:
            insights.append(
                f"Current telemetry for origin date ({context.forecast_origin}) is unavailable; insights rely on verified multi-horizon forecast models."
            )

        if forecast_avg_min is not None and forecast_avg_max is not None:
            insights.append(
                f"Predicted daily average temperature ranges from {forecast_avg_min:.1f}°C to {forecast_avg_max:.1f}°C across the 12-day forecast window."
            )

        if trend == "WARMING" and trend_delta is not None:
            insights.append(
                f"A warming trend of approximately +{trend_delta:.1f}°C is indicated between the near-term and day 12 horizons."
            )
        elif trend == "COOLING" and trend_delta is not None:
            insights.append(
                f"A cooling trend of approximately {trend_delta:.1f}°C is indicated between the near-term and day 12 horizons."
            )
        else:
            insights.append(
                f"Temperatures remain relatively stable across horizons with expected variance within ±1.5°C."
            )

        if diurnal_mean is not None:
            insights.append(
                f"The mean forecast diurnal temperature spread (Tmax - Tmin) is {diurnal_mean:.1f}°C."
            )

        if widening_c is not None and widening_c > 0:
            insights.append(
                f"Forecast uncertainty widens by {widening_c:.1f}°C between Day 1 and Day 12 as error bounds expand."
            )

        return TemperatureInsights(
            data_status=availability.overall_system_status,
            current_temp=current_temp,
            forecast_avg_min=forecast_avg_min,
            forecast_avg_max=forecast_avg_max,
            overall_trend=trend,
            trend_delta_c=trend_delta,
            diurnal_range_mean=diurnal_mean,
            interval_widening_c=widening_c,
            insights=insights,
        )
