"""
Phase 8 Data Availability Logic
Implements rigorous state classification (AVAILABLE, PARTIAL, UNAVAILABLE)
across stations, current telemetry (D0), historical observations (D-12..D-1),
and forecast horizons (T+1..T+12).
Zero-fabrication enforcement: missing telemetry is never silently imputed.
"""

from typing import Dict, Any, List, Optional
from phase8_intelligence.core.contracts import DataStatus, TimelineDayData, TimelineDayStatus


class DataAvailabilityAssessment:
    """Evaluates availability across all operational layers."""

    def __init__(self, timeline_days: List[TimelineDayData]):
        self.timeline_days = timeline_days
        self.past_days = [d for d in timeline_days if d.relative_day < 0]
        self.current_days = [d for d in timeline_days if d.relative_day == 0]
        self.forecast_days = [d for d in timeline_days if d.relative_day > 0]

    @property
    def current_telemetry_status(self) -> DataStatus:
        """Evaluates whether today's (D0) observation is available."""
        if not self.current_days:
            return DataStatus.UNAVAILABLE
        d0 = self.current_days[0]
        if d0.status == TimelineDayStatus.UNAVAILABLE:
            return DataStatus.UNAVAILABLE
        if d0.temperature_avg is None:
            return DataStatus.UNAVAILABLE
        # If avg temp is present but some other fields are None, it is PARTIAL
        if any(v is None for v in (d0.temperature_min, d0.temperature_max, d0.wind_speed, d0.air_pressure)):
            return DataStatus.PARTIAL
        return DataStatus.AVAILABLE

    @property
    def historical_observation_status(self) -> DataStatus:
        """Evaluates availability of D-12..D-1 recorded observations."""
        if not self.past_days:
            return DataStatus.UNAVAILABLE
        valid_days = [d for d in self.past_days if d.status == TimelineDayStatus.OBSERVED and d.temperature_avg is not None]
        if len(valid_days) == 0:
            return DataStatus.UNAVAILABLE
        elif len(valid_days) < len(self.past_days):
            return DataStatus.PARTIAL
        return DataStatus.AVAILABLE

    @property
    def forecast_status(self) -> DataStatus:
        """Evaluates availability of T+1..T+12 multi-horizon direct forecasts."""
        if not self.forecast_days:
            return DataStatus.UNAVAILABLE
        valid_forecasts = [d for d in self.forecast_days if d.status == TimelineDayStatus.FORECAST and d.temperature_avg is not None]
        if len(valid_forecasts) == 0:
            return DataStatus.UNAVAILABLE
        elif len(valid_forecasts) < 12:
            return DataStatus.PARTIAL
        return DataStatus.AVAILABLE

    @property
    def overall_system_status(self) -> DataStatus:
        """Consolidates system status."""
        fc_st = self.forecast_status
        curr_st = self.current_telemetry_status
        hist_st = self.historical_observation_status

        if fc_st == DataStatus.UNAVAILABLE:
            return DataStatus.UNAVAILABLE
        if curr_st == DataStatus.AVAILABLE and hist_st == DataStatus.AVAILABLE and fc_st == DataStatus.AVAILABLE:
            return DataStatus.AVAILABLE
        return DataStatus.PARTIAL

    def get_summary_report(self) -> Dict[str, Any]:
        """Provides a structured dictionary report of data availability."""
        return {
            "overall_status": self.overall_system_status.value,
            "current_telemetry": self.current_telemetry_status.value,
            "historical_observations": self.historical_observation_status.value,
            "forecast_horizons": self.forecast_status.value,
            "available_past_days_count": len([d for d in self.past_days if d.temperature_avg is not None]),
            "available_forecast_days_count": len([d for d in self.forecast_days if d.temperature_avg is not None]),
            "current_day_observed": self.current_telemetry_status != DataStatus.UNAVAILABLE,
        }
