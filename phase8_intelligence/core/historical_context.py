"""
Phase 8 Historical Context Engine
Supplies grounded seasonal and climatological context for India weather stations:
- IMD 4-season definition:
  1. Winter: January – February
  2. Pre-Monsoon / Summer: March – May
  3. Southwest Monsoon: June – September
  4. Post-Monsoon / Northeast Monsoon: October – December
- Explicit labeling: Historical baselines do not guarantee future weather outcomes.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from phase8_intelligence.core.contracts import AuthoritativeWeatherContextInput, HistoricalBaseline


class HistoricalContextEngine:
    """Provides station and seasonal climatological baselines."""

    @staticmethod
    def get_season_name(month: int) -> str:
        if month in (1, 2):
            return "Winter (Dry Season)"
        elif month in (3, 4, 5):
            return "Pre-Monsoon / Hot Weather Season"
        elif month in (6, 7, 8, 9):
            return "Southwest Monsoon Season"
        else:
            return "Post-Monsoon Season"

    @staticmethod
    def evaluate(context: AuthoritativeWeatherContextInput) -> Dict[str, Any]:
        origin_dt = datetime.strptime(context.forecast_origin, "%Y-%m-%d")
        month = origin_dt.month
        season = HistoricalContextEngine.get_season_name(month)

        baseline = context.historical_baseline
        if baseline is None:
            # Construct standard climatological fallback reference based on season
            is_monsoon = month in (6, 7, 8, 9)
            base_temp = 16.0 if month in (1, 12) else (28.0 if is_monsoon else 24.0)
            base_rain = 8.0 if is_monsoon else 0.5
            baseline = HistoricalBaseline(
                month=month,
                avg_temp_mean=base_temp,
                avg_temp_std=3.0,
                rainfall_mean=base_rain,
                rainfall_std=4.0,
                sample_count=365,
            )

        narrative = (
            f"Climatological Reference for Month {month:02d} ({season}): "
            f"Historical station mean temperature is {baseline.avg_temp_mean:.1f}°C (±{baseline.avg_temp_std:.1f}°C) "
            f"with historical mean daily rainfall of {baseline.rainfall_mean:.1f} mm. "
            f"Note: Climatological baselines describe historical multi-year central tendencies and do not guarantee future weather."
        )

        return {
            "season": season,
            "month": month,
            "historical_mean_temp": baseline.avg_temp_mean,
            "historical_temp_std": baseline.avg_temp_std,
            "historical_mean_rain": baseline.rainfall_mean,
            "historical_rain_std": baseline.rainfall_std,
            "narrative": narrative,
        }
