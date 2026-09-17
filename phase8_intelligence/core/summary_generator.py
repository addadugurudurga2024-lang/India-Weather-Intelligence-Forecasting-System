"""
Phase 8 Weather Summary Generator
Produces concise, structured meteorological summaries for 7 standard views:
1. Current conditions (or transparently 'Data unavailable')
2. Next 24 hours / T+1
3. Next 3 days (T+1..T+3)
4. Full 12-day outlook
5. Rainfall outlook
6. Temperature outlook
7. Forecast uncertainty
"""

from typing import Dict, Any, Optional
from phase8_intelligence.core.contracts import AuthoritativeWeatherContextInput, TimelineDayStatus
from phase8_intelligence.core.temperature_intel import TemperatureIntelligenceEngine
from phase8_intelligence.core.rainfall_intel import RainfallIntelligenceEngine
from phase8_intelligence.core.risk_engine import PrecipitationRiskEngine
from phase8_intelligence.core.confidence_language import ConfidenceLanguageEngine


class WeatherSummaryGenerator:
    """Generates the 7 canonical structured summaries."""

    @staticmethod
    def generate_all_summaries(context: AuthoritativeWeatherContextInput) -> Dict[str, str]:
        forecast_days = [d for d in context.timeline_days if d.relative_day > 0]
        current_day = next((d for d in context.timeline_days if d.relative_day == 0), None)
        t1_day = next((d for d in forecast_days if d.relative_day == 1), None)

        temp_intel = TemperatureIntelligenceEngine.analyze(context)
        rain_intel = RainfallIntelligenceEngine.analyze(context)
        risk_intel = PrecipitationRiskEngine.evaluate(context)

        # 1. Current conditions
        if current_day and current_day.status == TimelineDayStatus.CURRENT and current_day.temperature_avg is not None:
            s_current = (
                f"Current observed weather at {context.station.station_name} ({context.station.district}, {context.station.state}) "
                f"for origin date {context.forecast_origin}: Average temperature {current_day.temperature_avg:.1f}°C "
                f"(min {current_day.temperature_min}°C, max {current_day.temperature_max}°C), "
                f"wind speed {current_day.wind_speed or 0.0:.1f} km/h, air pressure {current_day.air_pressure or 0.0:.1f} hPa. "
                f"Rainfall recorded: {current_day.rainfall_amount or 0.0:.1f} mm."
            )
        else:
            s_current = (
                f"Current telemetry for origin date {context.forecast_origin} at {context.station.station_name} is UNAVAILABLE. "
                f"No synthetic observations are substituted; historical observations and forecast models remain active."
            )

        # 2. Next 24 hours / T+1
        if t1_day and t1_day.temperature_avg is not None:
            p_val = t1_day.rain_probability or 0.0
            r_val = t1_day.rainfall_amount or 0.0
            s_24h = (
                f"Next 24 hours (T+1, {t1_day.date}): Expected average temperature is {t1_day.temperature_avg:.1f}°C "
                f"(min {t1_day.temperature_min}°C, max {t1_day.temperature_max}°C). "
                f"Rain occurrence probability is {p_val * 100:.1f}%, with predicted rainfall accumulation of {r_val:.1f} mm. "
                f"Wind speed is forecast at {t1_day.wind_speed or 0.0:.1f} km/h."
            )
        else:
            s_24h = "Next 24-hour forecast data is unavailable."

        # 3. Next 3 days (T+1 to T+3)
        t3_days = [d for d in forecast_days if 1 <= d.relative_day <= 3 and d.temperature_avg is not None]
        if t3_days:
            t3_avg = sum(d.temperature_avg for d in t3_days) / len(t3_days)
            t3_max_p = max((d.rain_probability or 0.0) for d in t3_days)
            t3_rain_sum = sum((d.rainfall_amount or 0.0) for d in t3_days)
            s_3d = (
                f"Next 3-day outlook (T+1 to T+3): Daily average temperatures will average {t3_avg:.1f}°C. "
                f"Peak rain occurrence probability over the 3-day window reaches {t3_max_p * 100:.1f}%, "
                f"with cumulative expected rainfall of {t3_rain_sum:.1f} mm."
            )
        else:
            s_3d = "Next 3-day forecast data is unavailable."

        # 4. Full 12-day outlook
        s_12d = (
            f"12-Day Outlook ({context.forecast_origin} to {forecast_days[-1].date if forecast_days else 'N/A'}): "
            f"Average temperatures span {temp_intel.forecast_avg_min:.1f}°C to {temp_intel.forecast_avg_max:.1f}°C "
            f"with an overall {temp_intel.overall_trend.lower()} trajectory. "
            f"Cumulative precipitation is projected at {rain_intel.total_expected_rainfall_mm:.1f} mm "
            f"(peak single-day {rain_intel.max_single_day_rainfall_mm:.1f} mm on {rain_intel.max_rainfall_day}). "
            f"Overall precipitation risk category is {risk_intel.risk_level.value}."
        )

        # 5. Rainfall outlook
        s_rain = (
            f"Rainfall Outlook: {risk_intel.rationale} "
            f"Peak occurrence probability is {rain_intel.highest_probability * 100:.1f}% on {rain_intel.highest_prob_day} "
            f"({rain_intel.highest_prob_horizon}). Cumulative total is {rain_intel.total_expected_rainfall_mm:.1f} mm."
        )

        # 6. Temperature outlook
        s_temp = (
            f"Temperature Outlook: {temp_intel.overall_trend.title()} pattern with {temp_intel.trend_delta_c or 0.0:+.1f}°C "
            f"shift from Day 1 to Day 12. Mean daily diurnal range is {temp_intel.diurnal_range_mean:.1f}°C."
        )

        # 7. Forecast uncertainty
        w1 = 2.4
        w12 = 4.2
        if t1_day and t1_day.uncertainty:
            w1 = t1_day.uncertainty.temp_interval_80[1] - t1_day.uncertainty.temp_interval_80[0]
        t12_day = next((d for d in forecast_days if d.relative_day == 12), None)
        if t12_day and t12_day.uncertainty:
            w12 = t12_day.uncertainty.temp_interval_80[1] - t12_day.uncertainty.temp_interval_80[0]

        conf_obj = ConfidenceLanguageEngine.generate_confidence_statement(w1, w12)
        s_unc = conf_obj.statement

        return {
            "current_conditions": s_current,
            "next_24_hours": s_24h,
            "next_3_days": s_3d,
            "full_12_day_outlook": s_12d,
            "rainfall_outlook": s_rain,
            "temperature_outlook": s_temp,
            "forecast_uncertainty": s_unc,
        }
