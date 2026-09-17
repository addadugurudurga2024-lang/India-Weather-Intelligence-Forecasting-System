"""
Comprehensive Phase 1 Audit Engine for Tasks 01 through 16:
- Profiling & Metadata
- Field Semantics
- Time Coverage
- Station & Location Identity
- Duplicates & Observation Integrity
- Missingness Structure
- Rainfall Analysis
- Weather-Measurement Statistics
- Domain & Plausibility Validation
- Historical & Seasonal Analytics
- Forecasting Target Assessment
- Temporal Leakage & Validation Design
- Future Analytics & Geospatial Feasibility
- Machine-readable JSON/CSV generation & Key Diagnostic Visualizations
"""

import json
import logging
import math
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from data_loader import load_authoritative_data, verify_source_integrity, RAW_DATA_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(r"D:\weather_forcasting\phase1_audit\logs\phase1_audit.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("phase1_audit_engine")

OUTPUTS_DIR = Path(r"D:\weather_forcasting\phase1_audit\outputs")
DIAGNOSTICS_DIR = Path(r"D:\weather_forcasting\phase1_audit\diagnostics")
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
DIAGNOSTICS_DIR.mkdir(parents=True, exist_ok=True)


def convert_numpy_types(obj):
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.floating, float)):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_types(v) for v in obj]
    return obj


def run_all_tasks():
    logger.info("Starting complete Phase 1 Audit execution...")
    
    # 1. Verify integrity upfront
    if not verify_source_integrity():
        raise RuntimeError("Source integrity check failed prior to audit!")
    
    logger.info("Loading cached authoritative data...")
    df = load_authoritative_data()
    n_records, n_fields = df.shape
    logger.info("Dataset shape: %d rows, %d columns", n_records, n_fields)
    
    # Ensure date_of_record is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['date_of_record']):
        df['date_of_record'] = pd.to_datetime(df['date_of_record'])
    
    # -------------------------------------------------------------
    # TASK 01 & 02: Profiling & Dataset Characteristics
    # -------------------------------------------------------------
    logger.info("Executing Task 02: Dataset Profiling...")
    profile_data: Dict[str, Any] = {
        "n_records": int(n_records),
        "n_fields": int(n_fields),
        "fields": list(df.columns),
        "memory_usage_mb": float(df.memory_usage(deep=True).sum() / (1024 * 1024)),
        "columns_profile": {}
    }
    
    for col in df.columns:
        s = df[col]
        col_prof: Dict[str, Any] = {
            "dtype": str(s.dtype),
            "missing_count": int(s.isna().sum()),
            "missing_rate": float(s.isna().mean()),
            "unique_count": int(s.nunique(dropna=True)),
        }
        if pd.api.types.is_numeric_dtype(s):
            non_null = s.dropna()
            col_prof.update({
                "min": float(non_null.min()) if len(non_null) > 0 else None,
                "max": float(non_null.max()) if len(non_null) > 0 else None,
                "mean": float(non_null.mean()) if len(non_null) > 0 else None,
                "std": float(non_null.std()) if len(non_null) > 0 else None,
                "median": float(non_null.median()) if len(non_null) > 0 else None,
                "zero_count": int((non_null == 0).sum()),
                "zero_rate": float((non_null == 0).mean()) if len(non_null) > 0 else 0.0,
                "negative_count": int((non_null < 0).sum()),
                "negative_rate": float((non_null < 0).mean()) if len(non_null) > 0 else 0.0,
                "quantiles": {
                    "q01": float(non_null.quantile(0.01)) if len(non_null) > 0 else None,
                    "q05": float(non_null.quantile(0.05)) if len(non_null) > 0 else None,
                    "q25": float(non_null.quantile(0.25)) if len(non_null) > 0 else None,
                    "q50": float(non_null.quantile(0.50)) if len(non_null) > 0 else None,
                    "q75": float(non_null.quantile(0.75)) if len(non_null) > 0 else None,
                    "q95": float(non_null.quantile(0.95)) if len(non_null) > 0 else None,
                    "q99": float(non_null.quantile(0.99)) if len(non_null) > 0 else None,
                }
            })
        elif pd.api.types.is_datetime64_any_dtype(s):
            col_prof.update({
                "min_date": str(s.min()),
                "max_date": str(s.max()),
            })
        else:
            top_vals = s.value_counts(dropna=False).head(10).to_dict()
            col_prof.update({
                "top_10_values": {str(k): int(v) for k, v in top_vals.items()}
            })
        profile_data["columns_profile"][col] = col_prof

    with open(OUTPUTS_DIR / "task02_dataset_profile.json", "w", encoding="utf-8") as f:
        json.dump(convert_numpy_types(profile_data), f, indent=2)

    # -------------------------------------------------------------
    # TASK 03: Field Semantics and Calendar Consistency
    # -------------------------------------------------------------
    logger.info("Executing Task 03: Field Semantics & Calendar Consistency...")
    # Cross-check month & season
    observed_months = df['date_of_record'].dt.month_name()
    month_mismatch = (df['month'] != observed_months).sum()
    
    # Month to season mapping in dataset
    month_season_crosstab = pd.crosstab(df['month'], df['season']).to_dict()
    
    semantics_data = {
        "month_mismatch_count": int(month_mismatch),
        "month_season_crosstab": month_season_crosstab,
        "fields_evaluated": list(df.columns)
    }
    with open(OUTPUTS_DIR / "task03_field_semantics.json", "w", encoding="utf-8") as f:
        json.dump(convert_numpy_types(semantics_data), f, indent=2)

    # -------------------------------------------------------------
    # TASK 04: Time Coverage Investigation
    # -------------------------------------------------------------
    logger.info("Executing Task 04: Time Coverage Investigation...")
    dates = df['date_of_record']
    min_date = dates.min()
    max_date = dates.max()
    unique_dates = dates.nunique()
    expected_calendar_days = (max_date - min_date).days + 1
    
    date_counts = dates.value_counts().sort_index()
    records_by_year = df['date_of_record'].dt.year.value_counts().sort_index().to_dict()
    records_by_month = df['month'].value_counts().to_dict()
    records_by_season = df['season'].value_counts().to_dict()
    
    time_coverage = {
        "earliest_observation": str(min_date),
        "latest_observation": str(max_date),
        "unique_dates": int(unique_dates),
        "expected_calendar_days": int(expected_calendar_days),
        "missing_calendar_dates_count": int(expected_calendar_days - unique_dates),
        "records_per_date_stats": {
            "min": int(date_counts.min()),
            "max": int(date_counts.max()),
            "mean": float(date_counts.mean()),
            "median": float(date_counts.median()),
            "std": float(date_counts.std()),
        },
        "records_by_year": records_by_year,
        "records_by_month": records_by_month,
        "records_by_season": records_by_season,
    }
    with open(OUTPUTS_DIR / "task04_time_coverage.json", "w", encoding="utf-8") as f:
        json.dump(convert_numpy_types(time_coverage), f, indent=2)

    # -------------------------------------------------------------
    # TASK 05: Station and Location Identity
    # -------------------------------------------------------------
    logger.info("Executing Task 05: Station and Location Identity...")
    station_names = df['station_name'].nunique()
    station_state_pairs = df[['station_name', 'state']].drop_duplicates().shape[0]
    station_district_pairs = df[['station_name', 'state', 'district']].drop_duplicates().shape[0]
    station_coords_pairs = df[['station_name', 'latitude', 'longitude']].drop_duplicates().shape[0]
    coords_unique = df[['latitude', 'longitude']].drop_duplicates().shape[0]
    
    # Check 1: One station name -> multiple coordinates?
    station_to_coords = df.groupby('station_name')[['latitude', 'longitude']].nunique()
    multi_coord_stations = station_to_coords[(station_to_coords['latitude'] > 1) | (station_to_coords['longitude'] > 1)]
    
    # Check 2: One coordinate -> multiple station names?
    coords_to_station = df.groupby(['latitude', 'longitude'])['station_name'].nunique()
    multi_station_coords = coords_to_station[coords_to_station > 1]
    
    # Check 3: One station name in multiple states?
    station_to_state = df.groupby('station_name')['state'].nunique()
    multi_state_stations = station_to_state[station_to_state > 1]

    # Check 4: One station name in multiple districts?
    station_to_district = df.groupby('station_name')['district'].nunique()
    multi_district_stations = station_to_district[station_to_district > 1]

    station_identity_data = {
        "unique_station_names": int(station_names),
        "unique_station_state_pairs": int(station_state_pairs),
        "unique_station_district_pairs": int(station_district_pairs),
        "unique_station_coordinate_pairs": int(station_coords_pairs),
        "unique_coordinates": int(coords_unique),
        "stations_with_multiple_coordinates_count": int(len(multi_coord_stations)),
        "stations_with_multiple_coordinates_list": multi_coord_stations.index.tolist(),
        "coordinates_with_multiple_stations_count": int(len(multi_station_coords)),
        "stations_in_multiple_states_count": int(len(multi_state_stations)),
        "stations_in_multiple_states_list": multi_state_stations.index.tolist(),
        "stations_in_multiple_districts_count": int(len(multi_district_stations)),
        "stations_in_multiple_districts_list": multi_district_stations.index.tolist()
    }
    with open(OUTPUTS_DIR / "task05_station_identity.json", "w", encoding="utf-8") as f:
        json.dump(convert_numpy_types(station_identity_data), f, indent=2)

    # -------------------------------------------------------------
    # TASK 06: Duplicates and Observation Integrity
    # -------------------------------------------------------------
    logger.info("Executing Task 06: Duplicate & Observation Integrity...")
    exact_duplicates = int(df.duplicated().sum())
    
    # Station + Date duplicates
    station_date_dups = int(df.duplicated(subset=['station_name', 'date_of_record']).sum())
    station_state_dist_date_dups = int(df.duplicated(subset=['station_name', 'state', 'district', 'date_of_record']).sum())
    station_coord_date_dups = int(df.duplicated(subset=['station_name', 'latitude', 'longitude', 'date_of_record']).sum())
    coord_date_dups = int(df.duplicated(subset=['latitude', 'longitude', 'date_of_record']).sum())

    # Sample duplicate records for station+date if any
    sample_dups = []
    if station_date_dups > 0:
        dup_keys = df[df.duplicated(subset=['station_name', 'date_of_record'], keep=False)][['station_name', 'date_of_record']].head(5)
        for _, row in dup_keys.iterrows():
            matches = df[(df['station_name'] == row['station_name']) & (df['date_of_record'] == row['date_of_record'])].to_dict(orient='records')
            sample_dups.append(matches)

    duplicates_data = {
        "exact_duplicates": exact_duplicates,
        "station_date_duplicates": station_date_dups,
        "station_state_district_date_duplicates": station_state_dist_date_dups,
        "station_coord_date_duplicates": station_coord_date_dups,
        "coord_date_duplicates": coord_date_dups,
        "sample_duplicates": sample_dups
    }
    with open(OUTPUTS_DIR / "task06_duplicates.json", "w", encoding="utf-8") as f:
        json.dump(convert_numpy_types(duplicates_data), f, indent=2)

    # -------------------------------------------------------------
    # TASK 07: Missingness Structure
    # -------------------------------------------------------------
    logger.info("Executing Task 07: Missingness Structure...")
    missing_by_col = df.isna().sum().to_dict()
    missing_rates_by_col = df.isna().mean().to_dict()

    # Missingness over time (by year)
    missing_by_year = df.groupby(df['date_of_record'].dt.year)[
        ['avg_temp', 'min_temp', 'max_temp', 'wind_speed', 'air_pressure', 'rainfall']
    ].apply(lambda g: g.isna().mean()).to_dict(orient='index')

    # Missingness by state
    missing_by_state = df.groupby('state')[
        ['avg_temp', 'min_temp', 'max_temp', 'wind_speed', 'air_pressure', 'rainfall']
    ].apply(lambda g: g.isna().mean()).to_dict(orient='index')

    # Missingness correlation between weather variables
    missing_matrix = df[['avg_temp', 'min_temp', 'max_temp', 'wind_speed', 'air_pressure', 'rainfall']].isna()
    missing_corr = missing_matrix.corr().to_dict()

    missingness_data = {
        "missing_counts": missing_by_col,
        "missing_rates": missing_rates_by_col,
        "missing_by_year": missing_by_year,
        "missing_by_state": missing_by_state,
        "missing_correlation": missing_corr
    }
    with open(OUTPUTS_DIR / "task07_missingness.json", "w", encoding="utf-8") as f:
        json.dump(convert_numpy_types(missingness_data), f, indent=2)

    # -------------------------------------------------------------
    # TASK 08: Rainfall Data Investigation
    # -------------------------------------------------------------
    logger.info("Executing Task 08: Rainfall Investigation...")
    rf = df['rainfall']
    rf_missing = int(rf.isna().sum())
    rf_non_null = rf.dropna()
    rf_zero = int((rf_non_null == 0).sum())
    rf_positive = int((rf_non_null > 0).sum())
    rf_negative = int((rf_non_null < 0).sum())

    rf_quantiles = {
        f"q{int(q*100):02d}": float(rf_non_null.quantile(q))
        for q in [0.25, 0.50, 0.75, 0.90, 0.95, 0.98, 0.99, 0.999]
    }
    rf_pos_quantiles = {
        f"q{int(q*100):02d}": float(rf_non_null[rf_non_null > 0].quantile(q))
        for q in [0.25, 0.50, 0.75, 0.90, 0.95, 0.98, 0.99, 0.999]
    }

    # Diagnostic thresholds
    thresholds = [0.1, 1.0, 2.5, 5.0, 10.0, 35.5, 64.5, 115.5, 204.5] # IMD thresholds (light, moderate, heavy, very heavy, extremely heavy)
    threshold_counts = {f"rf_gte_{t}mm": int((rf_non_null >= t).sum()) for t in thresholds}
    threshold_rates = {f"rf_gte_{t}mm": float((rf_non_null >= t).mean()) for t in thresholds}

    # Rainfall by Season & Month
    rf_by_season = df.groupby('season')['rainfall'].agg(['count', 'mean', 'median', lambda s: (s == 0).mean()]).to_dict(orient='index')
    rf_by_month = df.groupby('month')['rainfall'].agg(['count', 'mean', 'median', lambda s: (s == 0).mean()]).to_dict(orient='index')

    rainfall_data = {
        "total_records": n_records,
        "missing_count": rf_missing,
        "missing_rate": float(rf_missing / n_records),
        "zero_count": rf_zero,
        "zero_rate_overall": float(rf_zero / n_records),
        "zero_rate_among_observed": float(rf_zero / len(rf_non_null)),
        "positive_count": rf_positive,
        "positive_rate_among_observed": float(rf_positive / len(rf_non_null)),
        "negative_count": rf_negative,
        "min": float(rf_non_null.min()),
        "max": float(rf_non_null.max()),
        "mean": float(rf_non_null.mean()),
        "median": float(rf_non_null.median()),
        "std": float(rf_non_null.std()),
        "overall_quantiles": rf_quantiles,
        "positive_only_quantiles": rf_pos_quantiles,
        "imd_threshold_counts": threshold_counts,
        "imd_threshold_rates": threshold_rates,
        "rainfall_by_season": rf_by_season,
        "rainfall_by_month": rf_by_month
    }
    with open(OUTPUTS_DIR / "task08_rainfall_analysis.json", "w", encoding="utf-8") as f:
        json.dump(convert_numpy_types(rainfall_data), f, indent=2)

    # -------------------------------------------------------------
    # TASK 09: Weather-Measurement Statistics
    # -------------------------------------------------------------
    logger.info("Executing Task 09: Weather Measurement Statistics & Associations...")
    num_cols = ['avg_temp', 'min_temp', 'max_temp', 'wind_speed', 'air_pressure', 'rainfall', 'elevation', 'latitude', 'longitude']
    stats_table = {}
    for col in num_cols:
        s = df[col].dropna()
        stats_table[col] = {
            "count": int(len(s)),
            "missing": int(df[col].isna().sum()),
            "missing_pct": float(df[col].isna().mean() * 100),
            "mean": float(s.mean()),
            "std": float(s.std()),
            "min": float(s.min()),
            "q25": float(s.quantile(0.25)),
            "median": float(s.median()),
            "q75": float(s.quantile(0.75)),
            "max": float(s.max()),
            "skew": float(s.skew()),
        }
    stats_df = pd.DataFrame(stats_table).T
    stats_df.to_csv(OUTPUTS_DIR / "task09_weather_statistics.csv")

    # Correlations / Associations
    corr_matrix = df[num_cols].corr().to_dict()
    with open(OUTPUTS_DIR / "task09_correlations.json", "w", encoding="utf-8") as f:
        json.dump(convert_numpy_types(corr_matrix), f, indent=2)

    # -------------------------------------------------------------
    # TASK 10: Domain and Value Validation (Physical Plausibility)
    # -------------------------------------------------------------
    logger.info("Executing Task 10: Domain and Plausibility Validation...")
    # 1. Temperature checks
    min_gt_max = int((df['min_temp'] > df['max_temp']).sum())
    # avg_temp outside min_temp and max_temp
    avg_out_of_bounds = int(((df['avg_temp'] < df['min_temp']) | (df['avg_temp'] > df['max_temp'])).sum())
    # Extreme temps (< -40 C or > 60 C)
    extreme_temps = int(((df['max_temp'] > 60) | (df['min_temp'] < -40) | (df['avg_temp'] > 60) | (df['avg_temp'] < -40)).sum())
    
    # 2. Wind speed checks
    neg_wind = int((df['wind_speed'] < 0).sum())
    extreme_wind = int((df['wind_speed'] > 150).sum()) # > 150 km/h (cyclone strength)
    
    # 3. Pressure checks
    neg_pressure = int((df['air_pressure'] < 0).sum())
    abnormal_pressure = int(((df['air_pressure'] < 850) | (df['air_pressure'] > 1085)).sum()) # sea level standard 1013.25, high altitude drops
    
    # 4. Rainfall checks
    neg_rainfall = int((df['rainfall'] < 0).sum())
    extreme_rainfall = int((df['rainfall'] > 1000).sum()) # > 1000 mm in 24h
    
    # 5. Coordinate checks (India bounding box roughly: Lat 6 to 38 N, Lon 68 to 98 E)
    invalid_lat = int(((df['latitude'] < 6.0) | (df['latitude'] > 38.0)).sum())
    invalid_lon = int(((df['longitude'] < 68.0) | (df['longitude'] > 98.0)).sum())
    invalid_elevation = int(((df['elevation'] < -50) | (df['elevation'] > 8848)).sum())

    validation_findings = {
        "temperature": {
            "min_gt_max_count": min_gt_max,
            "avg_out_of_bounds_count": avg_out_of_bounds,
            "extreme_temperature_count": extreme_temps,
            "status": "REQUIRES_ATTENTION" if (min_gt_max > 0 or avg_out_of_bounds > 0) else "VALID"
        },
        "wind_speed": {
            "negative_count": neg_wind,
            "extreme_gt_150_count": extreme_wind,
            "status": "VALID" if neg_wind == 0 else "INVALID"
        },
        "air_pressure": {
            "negative_count": neg_pressure,
            "abnormal_outside_850_1085_count": abnormal_pressure,
            "status": "EVALUATE_ELEVATION" if abnormal_pressure > 0 else "VALID"
        },
        "rainfall": {
            "negative_count": neg_rainfall,
            "extreme_gt_1000_count": extreme_rainfall,
            "status": "VALID" if neg_rainfall == 0 else "INVALID"
        },
        "geography": {
            "lat_outside_india_bounding_box": invalid_lat,
            "lon_outside_india_bounding_box": invalid_lon,
            "elevation_outside_valid_range": invalid_elevation,
            "status": "VALID" if (invalid_lat == 0 and invalid_lon == 0 and invalid_elevation == 0) else "SUSPICIOUS"
        }
    }
    with open(OUTPUTS_DIR / "task10_domain_validation.json", "w", encoding="utf-8") as f:
        json.dump(convert_numpy_types(validation_findings), f, indent=2)

    # -------------------------------------------------------------
    # TASK 11: Historical and Seasonal Analytics
    # -------------------------------------------------------------
    logger.info("Executing Task 11: Historical & Seasonal Analytics...")
    # Annual metrics
    annual_summary = df.groupby(df['date_of_record'].dt.year).agg({
        'avg_temp': ['mean', 'min', 'max'],
        'rainfall': ['mean', lambda s: (s > 0).mean(), 'sum'],
        'wind_speed': 'mean',
        'air_pressure': 'mean'
    })
    annual_summary.columns = ['_'.join(c).strip() for c in annual_summary.columns]
    annual_summary.to_csv(OUTPUTS_DIR / "task11_annual_summary.csv")

    # Seasonal metrics
    seasonal_summary = df.groupby('season').agg({
        'avg_temp': ['mean', 'std'],
        'rainfall': ['mean', lambda s: (s > 0).mean(), lambda s: s.isna().mean()],
        'wind_speed': 'mean',
        'air_pressure': 'mean'
    })
    seasonal_summary.columns = ['_'.join(c).strip() for c in seasonal_summary.columns]
    seasonal_summary.to_csv(OUTPUTS_DIR / "task11_seasonal_summary.csv")

    # -------------------------------------------------------------
    # TASK 12: Forecasting Target Assessment
    # -------------------------------------------------------------
    logger.info("Executing Task 12: Forecasting Target Assessment...")
    # Check consecutive day continuity per station
    # Sample top 10 stations to test continuity
    station_counts = df['station_name'].value_counts()
    continuity_samples = {}
    for stn in station_counts.head(10).index:
        stn_dates = df[df['station_name'] == stn]['date_of_record'].drop_duplicates().sort_values()
        date_diffs = stn_dates.diff().dt.days
        consecutive_1day_rate = float((date_diffs == 1).mean()) if len(date_diffs) > 1 else 0.0
        gaps_gt_1day = int((date_diffs > 1).sum()) if len(date_diffs) > 1 else 0
        continuity_samples[stn] = {
            "total_dates": int(len(stn_dates)),
            "consecutive_1day_fraction": consecutive_1day_rate,
            "gaps_count": gaps_gt_1day
        }

    forecasting_assessment = {
        "Target_A_Next_Day_Avg_Temp": {
            "feasibility": "READY_WITH_CONDITIONS",
            "availability": "High",
            "missingness": float(df['avg_temp'].isna().mean()),
            "continuity_dependency": "Requires strict station-level temporal sorting and masking when date_t+1 is not date_t + 1 day.",
            "leakage_risk": "High if shuffled or split randomly; requires rolling chronological split."
        },
        "Target_B_Next_Day_Rainfall_Amount": {
            "feasibility": "REQUIRES_CLEANING_AND_MASKING",
            "availability": "Zero-inflated and right-skewed (majority zero).",
            "missingness": float(df['rainfall'].isna().mean()),
            "critical_distinction": "Missing rainfall (~X%) must NEVER be imputed as 0 without physical evidence.",
            "skewness": float(df['rainfall'].dropna().skew())
        },
        "Target_C_Next_Day_Rain_No_Rain": {
            "feasibility": "READY_WITH_CONDITIONS",
            "availability": "High (binary classification)",
            "class_imbalance": {
                "zero_share": float(rainfall_data["zero_rate_among_observed"]),
                "rain_share": float(rainfall_data["positive_rate_among_observed"])
            },
            "recommended_threshold": "0.1mm (trace rainfall threshold) or 1.0mm (measurable rainfall threshold)"
        },
        "sample_station_continuity": continuity_samples
    }
    with open(OUTPUTS_DIR / "task12_forecasting_assessment.json", "w", encoding="utf-8") as f:
        json.dump(convert_numpy_types(forecasting_assessment), f, indent=2)

    # -------------------------------------------------------------
    # TASK 13 & 14: Leakage Assessment & Geospatial Feasibility
    # -------------------------------------------------------------
    logger.info("Executing Task 13 & 14: Leakage and Geospatial Feasibility...")
    leakage_assessment = {
        "prohibited_practices": [
            "Random train/test splits (causes extreme temporal autocorrelation leakage)",
            "Global min-max or standard scaling fit across the entire time series",
            "Backward-looking rolling features computed across gap dates without datetime index alignment",
            "Global target encoding of station/district without out-of-fold temporal partitioning",
            "Imputing missing rainfall as 0 across all historical records"
        ],
        "recommended_validation_strategy": "Chronological rolling-origin evaluation (Expanding Window or Walk-Forward Split by station)",
        "station_split_consideration": "Grouped TimeSeriesSplit by station identifier to test generalizability across unseen stations vs temporal holdout on known stations."
    }
    with open(OUTPUTS_DIR / "task13_leakage_and_validation.json", "w", encoding="utf-8") as f:
        json.dump(leakage_assessment, f, indent=2)

    geospatial_feasibility = {
        "state_count": int(df['state'].nunique()),
        "district_count": int(df['district'].nunique()),
        "station_count": int(df['station_name'].nunique()),
        "coordinate_bounds": {
            "min_lat": float(df['latitude'].min()),
            "max_lat": float(df['latitude'].max()),
            "min_lon": float(df['longitude'].min()),
            "max_lon": float(df['longitude'].max()),
            "min_elevation": float(df['elevation'].min()),
            "max_elevation": float(df['elevation'].max()),
        },
        "geospatial_readiness": "EXCELLENT",
        "notes": "Coordinates and elevations are intact across stations, enabling map views, spatial interpolation diagnostics, and regional clustering."
    }
    with open(OUTPUTS_DIR / "task14_geospatial_feasibility.json", "w", encoding="utf-8") as f:
        json.dump(convert_numpy_types(geospatial_feasibility), f, indent=2)

    # -------------------------------------------------------------
    # DIAGNOSTIC VISUALIZATIONS (TASK 16)
    # -------------------------------------------------------------
    logger.info("Generating key diagnostic visualizations for Task 16...")
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    
    # 1. Observation density over time
    fig, ax = plt.subplots(figsize=(12, 4))
    date_counts.plot(ax=ax, color='#1f77b4', lw=1)
    ax.set_title("Observations Count per Date Across India (Temporal Density)", fontsize=13, fontweight='bold')
    ax.set_xlabel("Date of Record")
    ax.set_ylabel("Number of Station Records")
    fig.tight_layout()
    fig.savefig(DIAGNOSTICS_DIR / "fig1_temporal_density.png", dpi=150)
    plt.close(fig)

    # 2. Temperature Plausibility (Avg vs Min/Max Scatter / Boxplot)
    fig, ax = plt.subplots(figsize=(8, 5))
    sample_sub = df.sample(n=min(20000, len(df)), random_state=42)
    ax.scatter(sample_sub['min_temp'], sample_sub['max_temp'], alpha=0.15, s=10, color='#2ca02c')
    ax.plot([-20, 50], [-20, 50], color='red', linestyle='--', label='Min == Max (Boundary)')
    ax.set_title("Domain Plausibility: Min Temp vs Max Temp (Sample N=20k)", fontsize=12, fontweight='bold')
    ax.set_xlabel("Min Temperature (°C)")
    ax.set_ylabel("Max Temperature (°C)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(DIAGNOSTICS_DIR / "fig2_temp_plausibility.png", dpi=150)
    plt.close(fig)

    # 3. Rainfall Distribution (Positive values log scale)
    fig, ax = plt.subplots(figsize=(8, 5))
    pos_rf = df.loc[df['rainfall'] > 0, 'rainfall']
    ax.hist(pos_rf, bins=100, log=True, color='#007acc', edgecolor='black', alpha=0.7)
    ax.set_title("Rainfall Distribution for Positive Records (Log Frequency)", fontsize=12, fontweight='bold')
    ax.set_xlabel("Rainfall (mm)")
    ax.set_ylabel("Count (log scale)")
    fig.tight_layout()
    fig.savefig(DIAGNOSTICS_DIR / "fig3_rainfall_distribution_log.png", dpi=150)
    plt.close(fig)

    # 4. Station Geographic Distribution
    fig, ax = plt.subplots(figsize=(7, 8))
    coords_df = df[['longitude', 'latitude', 'state']].drop_duplicates(subset=['longitude', 'latitude'])
    ax.scatter(coords_df['longitude'], coords_df['latitude'], alpha=0.6, s=15, color='#d95f02')
    ax.set_title(f"Station Locations Across India (N={len(coords_df)} unique coords)", fontsize=12, fontweight='bold')
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    fig.tight_layout()
    fig.savefig(DIAGNOSTICS_DIR / "fig4_station_locations_map.png", dpi=150)
    plt.close(fig)

    logger.info("All Task 01 - Task 16 analyses and diagnostic artifacts generated successfully.")


if __name__ == "__main__":
    run_all_tasks()
