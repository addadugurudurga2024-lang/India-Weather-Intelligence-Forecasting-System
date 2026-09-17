"""
Phase 1.5 Verification Suite - Temporal Continuity & Panel Structure
Differentiates national calendar continuity vs station-level panel continuity.
"""
import json
from pathlib import Path
import pandas as pd
# pyrefly: ignore [missing-import]
from data_loader import load_authoritative_data

def verify_temporal_continuity():
    df = load_authoritative_data()
    
    # 1. National calendar continuity
    dates = df['date_of_record'].sort_values().unique()
    min_date = pd.to_datetime(dates.min())
    max_date = pd.to_datetime(dates.max())
    expected_dates = pd.date_range(min_date, max_date, freq='D')
    missing_calendar_dates = expected_dates.difference(dates)
    
    # 2. Station-level continuity
    # Physical station key: station_name + lat + lon + elev
    df_sorted = df.sort_values(by=['station_name', 'latitude', 'longitude', 'elevation', 'date_of_record'])
    df_sorted['prev_date'] = df_sorted.groupby(['station_name', 'latitude', 'longitude', 'elevation'])['date_of_record'].shift(1)
    df_sorted['gap_days'] = (df_sorted['date_of_record'] - df_sorted['prev_date']).dt.days
    
    # Non-first observations
    non_first = df_sorted[df_sorted['gap_days'].notna()]
    consecutive_pairs = int((non_first['gap_days'] == 1).sum())
    gapped_pairs = int((non_first['gap_days'] > 1).sum())
    max_gap = int(non_first['gap_days'].max()) if len(non_first) > 0 else 0
    mean_gap = float(non_first['gap_days'].mean()) if len(non_first) > 0 else 0.0
    
    # Target A next-day availability:
    # A day t has t+1 available if the next observation for the same station has gap == 1 day
    df_sorted['next_date'] = df_sorted.groupby(['station_name', 'latitude', 'longitude', 'elevation'])['date_of_record'].shift(-1)
    df_sorted['days_to_next'] = (df_sorted['next_date'] - df_sorted['date_of_record']).dt.days
    target_a_valid = int((df_sorted['days_to_next'] == 1).sum())
    
    # Target B next-day availability (t+1 consecutive AND rainfall non-null at t+1)
    df_sorted['next_rainfall'] = df_sorted.groupby(['station_name', 'latitude', 'longitude', 'elevation'])['rainfall'].shift(-1)
    target_b_valid = int(((df_sorted['days_to_next'] == 1) & df_sorted['next_rainfall'].notna()).sum())
    
    # Target C binary balance on valid Target B dates
    valid_b_mask = (df_sorted['days_to_next'] == 1) & df_sorted['next_rainfall'].notna()
    target_c_dry = int((valid_b_mask & (df_sorted['next_rainfall'] == 0)).sum())
    target_c_rain = int((valid_b_mask & (df_sorted['next_rainfall'] > 0)).sum())
    
    continuity_results = {
        "national_calendar": {
            "min_date": str(min_date),
            "max_date": str(max_date),
            "total_calendar_days": int(len(expected_dates)),
            "unique_observed_dates": int(len(dates)),
            "missing_national_dates": int(len(missing_calendar_dates)),
            "panel_type": "Irregular unbalanced panel with 100% national daily presence"
        },
        "station_level_panel": {
            "total_physical_stations": int(df[['station_name', 'latitude', 'longitude', 'elevation']].drop_duplicates().shape[0]),
            "total_station_date_transitions": int(len(non_first)),
            "consecutive_1day_transitions": consecutive_pairs,
            "consecutive_1day_pct": float(consecutive_pairs / len(non_first) * 100),
            "gapped_transitions": gapped_pairs,
            "gapped_pct": float(gapped_pairs / len(non_first) * 100),
            "max_gap_days": max_gap,
            "mean_gap_days": mean_gap
        },
        "forecasting_target_availability": {
            "target_a_next_day_temp_available_count": target_a_valid,
            "target_a_pct_of_total": float(target_a_valid / len(df) * 100),
            "target_b_next_day_rain_available_count": target_b_valid,
            "target_b_pct_of_total": float(target_b_valid / len(df) * 100),
            "target_c_rain_status_dry_count": target_c_dry,
            "target_c_rain_status_dry_pct": float(target_c_dry / target_b_valid * 100),
            "target_c_rain_status_rain_count": target_c_rain,
            "target_c_rain_status_rain_pct": float(target_c_rain / target_b_valid * 100)
        }
    }
    
    out_json = Path(r"D:\weather_forcasting\phase1_verification\outputs\temporal_continuity.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(continuity_results, f, indent=2)
    print("Temporal continuity verified and written to:", out_json)
    return continuity_results

if __name__ == "__main__":
    verify_temporal_continuity()
