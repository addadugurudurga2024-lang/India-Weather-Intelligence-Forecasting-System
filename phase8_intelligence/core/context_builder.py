"""
Phase 8 Weather Context Builder
Deterministic assembler of verified operational weather timelines, station metadata,
forecast horizons, prediction intervals, and historical baselines into a validated
AuthoritativeWeatherContextInput.
Strictly enforces the boundary between observed and forecast data.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from phase8_intelligence.core.contracts import (
    AuthoritativeWeatherContextInput,
    StationMetadata,
    TimelineDayData,
    TimelineDayStatus,
    PredictionIntervals,
    ModelMetadata,
    HistoricalBaseline,
)


class WeatherContextBuilder:
    """Constructs and validates authoritative weather context inputs."""

    @staticmethod
    def from_operational_timeline_dict(
        timeline_dict: Dict[str, Any],
        historical_baseline: Optional[HistoricalBaseline] = None,
        evaluation_summary: Optional[Dict[str, Any]] = None,
    ) -> AuthoritativeWeatherContextInput:
        """Parses a Phase 7 Operational25DayTimeline JSON payload into AuthoritativeWeatherContextInput."""
        # 1. Parse station metadata
        station_meta = StationMetadata(
            station_id=timeline_dict.get("station_id", "UNKNOWN"),
            station_name=timeline_dict.get("station_name", "Unknown Station"),
            state=timeline_dict.get("state", "IN"),
            district=timeline_dict.get("district", "Unknown District"),
            latitude=float(timeline_dict.get("latitude", 20.0)),
            longitude=float(timeline_dict.get("longitude", 78.0)),
            elevation_m=float(timeline_dict.get("elevation_m", 100.0)),
        )

        # 2. Parse timeline days
        parsed_days: List[TimelineDayData] = []
        raw_timeline = timeline_dict.get("timeline", [])

        for item in raw_timeline:
            rel_day = int(item["relative_day"])
            status_str = item.get("status", "UNAVAILABLE")
            try:
                status = TimelineDayStatus(status_str)
            except ValueError:
                status = TimelineDayStatus.UNAVAILABLE

            # Prediction intervals if available
            unc_obj = None
            if "uncertainty" in item and item["uncertainty"] is not None:
                u = item["uncertainty"]
                unc_obj = PredictionIntervals(
                    temp_interval_80=(float(u["temp_interval_80"][0]), float(u["temp_interval_80"][1])),
                    temp_interval_95=(float(u["temp_interval_95"][0]), float(u["temp_interval_95"][1])),
                    rainfall_interval_80=(float(u["rainfall_interval_80"][0]), float(u["rainfall_interval_80"][1])),
                    methodology=u.get("methodology", "Empirical Validation Residual Quantiles (Fold 2)"),
                )

            # Model metadata if available
            model_obj = None
            if "model_metadata" in item and item["model_metadata"] is not None:
                m = item["model_metadata"]
                model_obj = ModelMetadata(
                    model_id=m.get("model_id", "xgb_multi_horizon"),
                    model_version=m.get("model_version", "1.0.0"),
                    horizon_name=m.get("horizon_name", f"T+{rel_day}"),
                    training_period=m.get("training_period", "2021-01-01 to 2023-12-31"),
                )

            day_data = TimelineDayData(
                date=item["date"],
                relative_day=rel_day,
                status=status,
                is_observed=bool(item.get("is_observed", False)),
                provenance=item.get("provenance", "Operational Pipeline"),
                temperature_avg=float(item["temperature_avg"]) if item.get("temperature_avg") is not None else None,
                temperature_min=float(item["temperature_min"]) if item.get("temperature_min") is not None else None,
                temperature_max=float(item["temperature_max"]) if item.get("temperature_max") is not None else None,
                rainfall_amount=float(item["rainfall_amount"]) if item.get("rainfall_amount") is not None else None,
                rain_probability=float(item["rain_probability"]) if item.get("rain_probability") is not None else None,
                rain_binary=bool(item["rain_binary"]) if item.get("rain_binary") is not None else None,
                wind_speed=float(item["wind_speed"]) if item.get("wind_speed") is not None else None,
                air_pressure=float(item["air_pressure"]) if item.get("air_pressure") is not None else None,
                uncertainty=unc_obj,
                model_metadata=model_obj,
            )
            parsed_days.append(day_data)

        # Sort days by relative_day ascending
        parsed_days.sort(key=lambda d: d.relative_day)

        origin_date = timeline_dict.get("forecast_origin", datetime.now().strftime("%Y-%m-%d"))
        gen_at = timeline_dict.get("generated_at", datetime.now().isoformat())

        return AuthoritativeWeatherContextInput(
            station=station_meta,
            forecast_origin=origin_date,
            timeline_days=parsed_days,
            historical_baseline=historical_baseline,
            evaluation_summary=evaluation_summary,
            generated_at=gen_at,
            provenance="Phase 7 Operational Ingestion and Timeline System",
        )
