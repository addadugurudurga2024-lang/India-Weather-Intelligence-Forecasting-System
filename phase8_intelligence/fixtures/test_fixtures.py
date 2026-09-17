"""
Phase 8 AI Quality Test Data Fixtures
Provides 10 deterministic synthetic fixtures representing key meteorological and edge-case profiles:
1. Dry station (Rajasthan desert regime: zero rain, high heat)
2. High-rain station (Monsoon/Northeast regime: high rain accumulation and probability)
3. Coastal station (Peninsular maritime regime: narrow diurnal range)
4. High-elevation station (Himalayan alpine regime: low temperatures, elevation > 2000m)
5. Missing telemetry (D0 telemetry unavailable; fallback behavior)
6. Partial telemetry (D0 has temperatures, but wind/pressure are missing)
7. High forecast uncertainty (significantly wider residual quantiles)
8. Increasing rain probability (drying to wetting transition across horizons)
9. Decreasing temperature (strong cold-front passage across horizons)
10. Historical anomaly (temperature exceeds 2-sigma baseline departure)
"""

from typing import Dict, Any, List
from phase8_intelligence.core.contracts import (
    AuthoritativeWeatherContextInput,
    StationMetadata,
    TimelineDayData,
    TimelineDayStatus,
    PredictionIntervals,
    ModelMetadata,
    HistoricalBaseline,
)


def _create_base_timeline(
    origin_date: str = "2025-01-20",
    d0_temp: float = 22.0,
    d0_min: float = 16.0,
    d0_max: float = 27.0,
    d0_rain: float = 0.0,
    d0_status: TimelineDayStatus = TimelineDayStatus.CURRENT,
    forecast_temp_curve: List[float] = None,
    forecast_rain_prob_curve: List[float] = None,
    forecast_rain_amt_curve: List[float] = None,
    uncertainty_width: float = 2.0,
    is_d0_missing: bool = False,
    is_d0_partial: bool = False,
) -> List[TimelineDayData]:
    """Helper to synthesize a 25-day timeline."""
    days: List[TimelineDayData] = []
    # Dates relative to 2025-01-20:
    # relative_day from -12 to +12

    # D-12 to D-1 (Historical observations)
    for r in range(-12, 0):
        day_num = 20 + r
        d_str = f"2025-01-{day_num:02d}"
        days.append(TimelineDayData(
            date=d_str,
            relative_day=r,
            status=TimelineDayStatus.OBSERVED,
            is_observed=True,
            provenance="IMD Historical Canonical Ground Truth",
            temperature_avg=21.5,
            temperature_min=15.0,
            temperature_max=26.5,
            rainfall_amount=0.0,
            rain_probability=0.05,
            rain_binary=False,
            wind_speed=8.5,
            air_pressure=1013.2,
        ))

    # D0 (Current Day)
    if is_d0_missing:
        days.append(TimelineDayData(
            date=origin_date,
            relative_day=0,
            status=TimelineDayStatus.UNAVAILABLE,
            is_observed=False,
            provenance="Open-Meteo Current Telemetry (Offline/Missing)",
            temperature_avg=None,
            temperature_min=None,
            temperature_max=None,
            rainfall_amount=None,
            rain_probability=None,
            rain_binary=None,
            wind_speed=None,
            air_pressure=None,
        ))
    elif is_d0_partial:
        days.append(TimelineDayData(
            date=origin_date,
            relative_day=0,
            status=TimelineDayStatus.CURRENT,
            is_observed=True,
            provenance="Partial Telemetry Feed",
            temperature_avg=d0_temp,
            temperature_min=d0_min,
            temperature_max=d0_max,
            rainfall_amount=0.0,
            rain_probability=None,
            rain_binary=None,
            wind_speed=None,  # Missing
            air_pressure=None,  # Missing
        ))
    else:
        days.append(TimelineDayData(
            date=origin_date,
            relative_day=0,
            status=d0_status,
            is_observed=True,
            provenance="Open-Meteo Current Telemetry (Verified WMO Station)",
            temperature_avg=d0_temp,
            temperature_min=d0_min,
            temperature_max=d0_max,
            rainfall_amount=d0_rain,
            rain_probability=0.10,
            rain_binary=False,
            wind_speed=9.0,
            air_pressure=1012.8,
        ))

    # D+1 to D+12 (Forecasts)
    f_temps = forecast_temp_curve or [22.0 + (i * 0.1) for i in range(12)]
    f_probs = forecast_rain_prob_curve or [0.10 for _ in range(12)]
    f_rains = forecast_rain_amt_curve or [0.0 for _ in range(12)]

    for h in range(1, 13):
        day_num = 20 + h
        d_str = f"2025-01-{day_num:02d}" if day_num <= 31 else f"2025-02-{day_num - 31:02d}"
        t_avg = round(f_temps[h - 1], 1)
        t_min = round(t_avg - 5.0, 1)
        t_max = round(t_avg + 5.0, 1)
        p_rain = round(f_probs[h - 1], 3)
        amt_rain = round(f_rains[h - 1], 1)

        w = uncertainty_width + (h * 0.2)
        unc = PredictionIntervals(
            temp_interval_80=(round(t_avg - w/2, 1), round(t_avg + w/2, 1)),
            temp_interval_95=(round(t_avg - w, 1), round(t_avg + w, 1)),
            rainfall_interval_80=(0.0, round(amt_rain * 2.0 + 0.5, 1)),
            methodology="Empirical Validation Residual Quantiles (Fold 2)",
        )

        model_meta = ModelMetadata(
            model_id=f"xgb_multi_horizon_h{h}_v1",
            model_version="1.0.0",
            horizon_name=f"T+{h}",
            training_period="2021-01-01 to 2023-12-31",
        )

        days.append(TimelineDayData(
            date=d_str,
            relative_day=h,
            status=TimelineDayStatus.FORECAST,
            is_observed=False,
            provenance=f"XGBoost Multi-Horizon Direct Engine (xgb_multi_horizon_h{h}_v1)",
            temperature_avg=t_avg,
            temperature_min=t_min,
            temperature_max=t_max,
            rainfall_amount=amt_rain,
            rain_probability=p_rain,
            rain_binary=p_rain >= 0.30,
            wind_speed=8.0,
            air_pressure=1012.0,
            uncertainty=unc,
            model_metadata=model_meta,
        ))

    return days


def get_dry_station_fixture() -> AuthoritativeWeatherContextInput:
    """Fixture 1: Dry station (e.g. Bikaner, Rajasthan)."""
    station = StationMetadata(
        station_id="BIK001",
        station_name="Bikaner Meteorological Observatory",
        state="Rajasthan",
        district="Bikaner",
        latitude=28.02,
        longitude=73.31,
        elevation_m=224.0,
    )
    days = _create_base_timeline(
        d0_temp=26.0,
        d0_min=18.0,
        d0_max=32.0,
        forecast_temp_curve=[26.0, 26.5, 27.0, 27.2, 27.5, 28.0, 28.2, 28.5, 29.0, 29.2, 29.5, 30.0],
        forecast_rain_prob_curve=[0.02] * 12,
        forecast_rain_amt_curve=[0.0] * 12,
    )
    return AuthoritativeWeatherContextInput(
        station=station,
        forecast_origin="2025-01-20",
        timeline_days=days,
        generated_at="2025-01-20T06:00:00Z",
    )


def get_high_rain_station_fixture() -> AuthoritativeWeatherContextInput:
    """Fixture 2: High-rain station (e.g. Cherrapunji / Agartala)."""
    station = StationMetadata(
        station_id="CHE002",
        station_name="Cherrapunji Station",
        state="Meghalaya",
        district="East Khasi Hills",
        latitude=25.27,
        longitude=91.73,
        elevation_m=1313.0,
    )
    days = _create_base_timeline(
        d0_temp=18.0,
        d0_min=14.0,
        d0_max=22.0,
        d0_rain=32.0,
        forecast_temp_curve=[18.0] * 12,
        forecast_rain_prob_curve=[0.75, 0.82, 0.88, 0.79, 0.70, 0.65, 0.80, 0.85, 0.90, 0.84, 0.78, 0.72],
        forecast_rain_amt_curve=[24.0, 38.5, 45.0, 28.0, 16.5, 12.0, 25.0, 34.0, 42.0, 26.0, 18.0, 14.0],
    )
    return AuthoritativeWeatherContextInput(
        station=station,
        forecast_origin="2025-01-20",
        timeline_days=days,
        generated_at="2025-01-20T06:00:00Z",
    )


def get_coastal_station_fixture() -> AuthoritativeWeatherContextInput:
    """Fixture 3: Coastal station (e.g. Mumbai, Maharashtra)."""
    station = StationMetadata(
        station_id="MUM003",
        station_name="Mumbai Colaba Observatory",
        state="Maharashtra",
        district="Mumbai",
        latitude=18.90,
        longitude=72.81,
        elevation_m=11.0,
    )
    # Narrow diurnal range (~4 C)
    days = _create_base_timeline(
        d0_temp=27.5,
        d0_min=25.0,
        d0_max=29.5,
        forecast_temp_curve=[27.0 + (i * 0.1) for i in range(12)],
        forecast_rain_prob_curve=[0.15] * 12,
        forecast_rain_amt_curve=[0.0] * 12,
    )
    return AuthoritativeWeatherContextInput(
        station=station,
        forecast_origin="2025-01-20",
        timeline_days=days,
        generated_at="2025-01-20T06:00:00Z",
    )


def get_high_elevation_station_fixture() -> AuthoritativeWeatherContextInput:
    """Fixture 4: High-elevation station (e.g. Shimla / Leh, >2000m)."""
    station = StationMetadata(
        station_id="LEH004",
        station_name="Leh Meteorological Center",
        state="Ladakh",
        district="Leh",
        latitude=34.15,
        longitude=77.58,
        elevation_m=3514.0,
    )
    days = _create_base_timeline(
        d0_temp=-4.0,
        d0_min=-10.0,
        d0_max=2.0,
        forecast_temp_curve=[-4.0, -4.5, -5.0, -3.5, -3.0, -2.5, -3.0, -4.0, -5.0, -4.5, -4.0, -3.5],
        forecast_rain_prob_curve=[0.10] * 12,
        forecast_rain_amt_curve=[0.2] * 12,
    )
    return AuthoritativeWeatherContextInput(
        station=station,
        forecast_origin="2025-01-20",
        timeline_days=days,
        generated_at="2025-01-20T06:00:00Z",
    )


def get_missing_telemetry_fixture() -> AuthoritativeWeatherContextInput:
    """Fixture 5: Missing telemetry (D0 UNAVAILABLE)."""
    station = StationMetadata(
        station_id="DEL005",
        station_name="Delhi Safdarjung Station",
        state="Delhi",
        district="New Delhi",
        latitude=28.58,
        longitude=77.20,
        elevation_m=216.0,
    )
    days = _create_base_timeline(is_d0_missing=True)
    return AuthoritativeWeatherContextInput(
        station=station,
        forecast_origin="2025-01-20",
        timeline_days=days,
        generated_at="2025-01-20T06:00:00Z",
    )


def get_partial_telemetry_fixture() -> AuthoritativeWeatherContextInput:
    """Fixture 6: Partial telemetry (D0 has temperature, but wind & pressure missing)."""
    station = StationMetadata(
        station_id="BLR006",
        station_name="Bengaluru Central Station",
        state="Karnataka",
        district="Bengaluru Urban",
        latitude=12.97,
        longitude=77.59,
        elevation_m=920.0,
    )
    days = _create_base_timeline(is_d0_partial=True)
    return AuthoritativeWeatherContextInput(
        station=station,
        forecast_origin="2025-01-20",
        timeline_days=days,
        generated_at="2025-01-20T06:00:00Z",
    )


def get_high_uncertainty_fixture() -> AuthoritativeWeatherContextInput:
    """Fixture 7: High forecast uncertainty (wide intervals)."""
    station = StationMetadata(
        station_id="KOL007",
        station_name="Kolkata Alipore Station",
        state="West Bengal",
        district="Kolkata",
        latitude=22.53,
        longitude=88.33,
        elevation_m=9.0,
    )
    days = _create_base_timeline(uncertainty_width=6.0)
    return AuthoritativeWeatherContextInput(
        station=station,
        forecast_origin="2025-01-20",
        timeline_days=days,
        generated_at="2025-01-20T06:00:00Z",
    )


def get_increasing_rain_prob_fixture() -> AuthoritativeWeatherContextInput:
    """Fixture 8: Increasing rain probability (drying to wetting transition)."""
    station = StationMetadata(
        station_id="HYD008",
        station_name="Hyderabad Begumpet Station",
        state="Telangana",
        district="Hyderabad",
        latitude=17.45,
        longitude=78.47,
        elevation_m=531.0,
    )
    probs = [0.05, 0.08, 0.12, 0.20, 0.35, 0.48, 0.62, 0.74, 0.81, 0.85, 0.88, 0.90]
    rains = [0.0, 0.0, 0.0, 0.5, 2.8, 6.4, 12.0, 18.5, 22.0, 24.5, 28.0, 31.0]
    days = _create_base_timeline(forecast_rain_prob_curve=probs, forecast_rain_amt_curve=rains)
    return AuthoritativeWeatherContextInput(
        station=station,
        forecast_origin="2025-01-20",
        timeline_days=days,
        generated_at="2025-01-20T06:00:00Z",
    )


def get_decreasing_temp_fixture() -> AuthoritativeWeatherContextInput:
    """Fixture 9: Decreasing temperature (Cold-front passage)."""
    station = StationMetadata(
        station_id="LKO009",
        station_name="Lucknow Amausi Station",
        state="Uttar Pradesh",
        district="Lucknow",
        latitude=26.76,
        longitude=80.88,
        elevation_m=128.0,
    )
    temps = [28.0, 27.0, 25.5, 23.0, 21.0, 19.5, 18.0, 17.0, 16.5, 16.0, 15.5, 15.0]
    days = _create_base_timeline(forecast_temp_curve=temps)
    return AuthoritativeWeatherContextInput(
        station=station,
        forecast_origin="2025-01-20",
        timeline_days=days,
        generated_at="2025-01-20T06:00:00Z",
    )


def get_historical_anomaly_fixture() -> AuthoritativeWeatherContextInput:
    """Fixture 10: Historical anomaly (34°C in January where baseline is 16°C ± 3°C)."""
    station = StationMetadata(
        station_id="JAI010",
        station_name="Jaipur Sanganer Station",
        state="Rajasthan",
        district="Jaipur",
        latitude=26.82,
        longitude=75.80,
        elevation_m=390.0,
    )
    # January baseline: mean 16.0 C, std 3.0 C. 34.0 C is +18.0 C (6 sigma!)
    days = _create_base_timeline(
        d0_temp=33.5,
        d0_min=28.0,
        d0_max=38.0,
        forecast_temp_curve=[33.0, 33.5, 34.0, 34.5, 35.0, 35.0, 34.5, 34.0, 33.5, 33.0, 33.0, 32.5]
    )
    baseline = HistoricalBaseline(
        month=1,
        avg_temp_mean=16.0,
        avg_temp_std=3.0,
        rainfall_mean=0.3,
        rainfall_std=1.2,
        sample_count=500,
    )
    return AuthoritativeWeatherContextInput(
        station=station,
        forecast_origin="2025-01-20",
        timeline_days=days,
        historical_baseline=baseline,
        generated_at="2025-01-20T06:00:00Z",
    )
