"""
Phase 8 Anomaly Intelligence Engine
Identifies statistically significant departures from verified historical baselines.
Uses exact 2-sigma thresholds with explicit reference baselines.
Avoids speculative or sensationalized language (e.g. 'dangerous').
"""

from typing import List
from phase8_intelligence.core.contracts import AuthoritativeWeatherContextInput
from phase8_intelligence.core.schemas import AnomalyReport
from phase8_intelligence.core.historical_context import HistoricalContextEngine


class AnomalyIntelligenceEngine:
    """Detects and reports grounded meteorological anomalies."""

    @staticmethod
    def detect(context: AuthoritativeWeatherContextInput) -> List[AnomalyReport]:
        reports: List[AnomalyReport] = []
        hist = HistoricalContextEngine.evaluate(context)

        hist_temp = hist["historical_mean_temp"]
        hist_t_std = hist["historical_temp_std"]
        hist_rain = hist["historical_mean_rain"]

        forecast_days = [d for d in context.timeline_days if d.relative_day > 0 and d.temperature_avg is not None]
        if not forecast_days:
            return [AnomalyReport(
                is_anomalous=False,
                description="Insufficient forecast data to evaluate anomalies.",
            )]

        # 1. Temperature departure check
        for d in forecast_days:
            t = d.temperature_avg
            if t is None:
                continue
            delta_t = round(t - hist_temp, 1)
            # Threshold: >= 2.0 standard deviations
            if abs(delta_t) >= 2.0 * hist_t_std:
                direction = "above" if delta_t > 0 else "below"
                desc = (
                    f"Horizon T+{d.relative_day} ({d.date}) predicted average temperature of {t:.1f}°C is "
                    f"{abs(delta_t):.1f}°C {direction} the historical monthly baseline of {hist_temp:.1f}°C "
                    f"(exceeds 2σ deviation threshold of ±{2.0 * hist_t_std:.1f}°C)."
                )
                reports.append(AnomalyReport(
                    is_anomalous=True,
                    temperature_anomaly_c=delta_t,
                    baseline_reference=f"Monthly baseline {hist_temp:.1f}°C (std: {hist_t_std:.1f}°C)",
                    description=desc,
                ))

        # 2. Rainfall anomaly check (heavy precipitation compared to climatological daily mean)
        for d in forecast_days:
            r = d.rainfall_amount
            if r is not None and r >= 15.5:  # IMD heavy rain threshold
                pct_above = round(((r - hist_rain) / max(0.1, hist_rain)) * 100, 1) if hist_rain > 0 else 100.0
                desc = (
                    f"Horizon T+{d.relative_day} ({d.date}) forecast rainfall of {r:.1f} mm "
                    f"is significantly elevated compared to the seasonal daily baseline of {hist_rain:.1f} mm "
                    f"(+{pct_above:.0f}% departure, exceeding IMD 15.5 mm rather-heavy threshold)."
                )
                reports.append(AnomalyReport(
                    is_anomalous=True,
                    rainfall_anomaly_percent=pct_above,
                    baseline_reference=f"Seasonal daily mean {hist_rain:.1f} mm",
                    description=desc,
                ))

        if not reports:
            reports.append(AnomalyReport(
                is_anomalous=False,
                baseline_reference=f"Monthly baseline {hist_temp:.1f}°C (std: {hist_t_std:.1f}°C)",
                description="All forecast horizons remain within normal 2-sigma climatological bounds.",
            ))

        return reports
