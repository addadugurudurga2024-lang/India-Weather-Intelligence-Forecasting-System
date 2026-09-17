"""Data access service for canonical weather data and station registry."""

import json
from typing import Dict, List, Optional, Any
import pandas as pd
from backend.app.config import settings

_STATIONS_CACHE: Optional[List[Dict[str, Any]]] = None
_STATION_MAP: Optional[Dict[str, Dict[str, Any]]] = None
_PARQUET_DF: Optional[pd.DataFrame] = None


def load_stations() -> List[Dict[str, Any]]:
    """Loads all 413 canonical stations."""
    global _STATIONS_CACHE, _STATION_MAP
    if _STATIONS_CACHE is not None:
        return _STATIONS_CACHE

    target_path = settings.FRONTEND_STATIONS_PATH
    if not target_path.exists():
        target_path = settings.CANONICAL_STATIONS_PATH

    with open(target_path, "r", encoding="utf-8") as f:
        stations = json.load(f)

    if isinstance(stations, dict):
        stations = list(stations.values())

    # Standardize schema across all stations
    normalized = []
    station_map = {}
    for stn in stations:
        item = {
            "station_id": stn["station_id"],
            "station_name": stn["station_name"],
            "state": stn["state"],
            "district": stn["district"],
            "latitude": float(stn["latitude"]),
            "longitude": float(stn["longitude"]),
            "elevation_m": float(stn.get("elevation_m", stn.get("elevation", 0.0))),
        }
        normalized.append(item)
        station_map[stn["station_id"]] = item

    _STATIONS_CACHE = normalized
    _STATION_MAP = station_map
    return _STATIONS_CACHE


def _clean_filter_param(val: Optional[str]) -> Optional[str]:
    """Cleans a filter parameter, converting empty/ALL/undefined/null strings to None."""
    if not val:
        return None
    cleaned = str(val).strip()
    if cleaned.upper() in ("ALL", "UNDEFINED", "NULL", ""):
        return None
    return cleaned


def get_station_by_id(station_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single station by canonical ID."""
    global _STATION_MAP
    if _STATION_MAP is None:
        load_stations()
    return _STATION_MAP.get(station_id)


def get_geographic_hierarchy() -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
    """Returns State -> District -> [Stations] hierarchy."""
    stations = load_stations()
    hierarchy: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
    for stn in stations:
        st = stn["state"]
        dist = stn["district"]
        if st not in hierarchy:
            hierarchy[st] = {}
        if dist not in hierarchy[st]:
            hierarchy[st][dist] = []
        hierarchy[st][dist].append(stn)
    return hierarchy


def get_parquet_dataframe() -> Optional[pd.DataFrame]:
    """Loads or retrieves the in-memory cached canonical parquet DataFrame."""
    global _PARQUET_DF
    if _PARQUET_DF is not None:
        return _PARQUET_DF
    if settings.CANONICAL_PARQUET_PATH.exists():
        _PARQUET_DF = pd.read_parquet(
            settings.CANONICAL_PARQUET_PATH,
            columns=[
                "station_id", "station_name", "state", "district",
                "date_of_record", "avg_temp", "min_temp", "max_temp",
                "rainfall", "wind_speed", "air_pressure"
            ]
        )
        return _PARQUET_DF
    return None


def get_station_analytics(station_id: str) -> Optional[Dict[str, Any]]:
    """Computes / retrieves historical summary statistics for a station."""
    stn = get_station_by_id(station_id)
    if not stn:
        return None

    df_full = get_parquet_dataframe()
    if df_full is not None:
        df = df_full[df_full["station_id"] == station_id]
        if len(df) > 0:
            df_dates = pd.to_datetime(df["date_of_record"])
            return {
                "station_id": station_id,
                "station_name": stn["station_name"],
                "record_count": int(len(df)),
                "date_range": {
                    "start": str(df_dates.min().strftime("%Y-%m-%d")),
                    "end": str(df_dates.max().strftime("%Y-%m-%d")),
                },
                "temp_avg_mean": round(float(df["avg_temp"].mean()), 1) if pd.notna(df["avg_temp"].mean()) else None,
                "temp_min_record": round(float(df["min_temp"].min()), 1) if pd.notna(df["min_temp"].min()) else None,
                "temp_max_record": round(float(df["max_temp"].max()), 1) if pd.notna(df["max_temp"].max()) else None,
                "annual_rainfall_mean_mm": round(float(df["rainfall"].sum() / (len(df) / 365.25)), 1) if len(df) >= 365 and pd.notna(df["rainfall"].sum()) else None,
                "max_single_day_rain_mm": round(float(df["rainfall"].max()), 1) if pd.notna(df["rainfall"].max()) else None,
                "wind_speed_mean_kmh": round(float(df["wind_speed"].mean()), 1) if pd.notna(df["wind_speed"].mean()) else None,
                "air_pressure_mean_hpa": round(float(df["air_pressure"].mean()), 1) if pd.notna(df["air_pressure"].mean()) else None,
            }

    return {
        "station_id": station_id,
        "station_name": stn["station_name"],
        "record_count": 0,
        "date_range": {"start": "2015-01-01", "end": "2025-02-10"},
        "temp_avg_mean": None,
    }


def get_station_timeseries(station_id: str, limit: int = 365) -> List[Dict[str, Any]]:
    """Retrieves chronological observations for a station up to limit."""
    stn = get_station_by_id(station_id)
    if not stn:
        return []

    df_full = get_parquet_dataframe()
    if df_full is None:
        return []

    df = df_full[df_full["station_id"] == station_id]
    if len(df) == 0:
        return []

    df = df.sort_values("date_of_record", ascending=False).head(limit).iloc[::-1]
    results = []
    for _, row in df.iterrows():
        results.append({
            "date": row["date_of_record"].strftime("%Y-%m-%d") if hasattr(row["date_of_record"], "strftime") else str(row["date_of_record"])[:10],
            "temp_avg": round(float(row["avg_temp"]), 1) if pd.notna(row["avg_temp"]) else None,
            "temp_min": round(float(row["min_temp"]), 1) if pd.notna(row["min_temp"]) else None,
            "temp_max": round(float(row["max_temp"]), 1) if pd.notna(row["max_temp"]) else None,
            "rainfall": round(float(row["rainfall"]), 1) if pd.notna(row["rainfall"]) else None,
            "wind_speed": round(float(row["wind_speed"]), 1) if pd.notna(row["wind_speed"]) else None,
            "air_pressure": round(float(row["air_pressure"]), 1) if pd.notna(row["air_pressure"]) else None,
        })
    return results


def get_scoped_observations(
    state: Optional[str] = None,
    district: Optional[str] = None,
    station_id: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Retrieves recent canonical observations scoped to state, district, or station."""
    df_full = get_parquet_dataframe()
    if df_full is None:
        return []

    clean_state = _clean_filter_param(state)
    clean_district = _clean_filter_param(district)
    clean_station_id = _clean_filter_param(station_id)

    sub = df_full
    if clean_state:
        sub = sub[sub["state"].astype(str).str.upper() == clean_state.upper()]
    if clean_district:
        sub = sub[sub["district"].astype(str).str.lower() == clean_district.lower()]
    if clean_station_id:
        sub = sub[sub["station_id"].astype(str) == clean_station_id]

    if len(sub) == 0:
        return []

    sub = sub.sort_values("date_of_record", ascending=False).head(limit)
    res = []
    for _, row in sub.iterrows():
        d_str = row["date_of_record"].strftime("%Y-%m-%d") if hasattr(row["date_of_record"], "strftime") else str(row["date_of_record"])[:10]
        rain_val = round(float(row["rainfall"]), 1) if pd.notna(row["rainfall"]) else None
        res.append({
            "station_id": row["station_id"],
            "station_name": row["station_name"],
            "state": row["state"],
            "district": row["district"],
            "date_of_record": d_str,
            "avg_temp": round(float(row["avg_temp"]), 1) if pd.notna(row["avg_temp"]) else None,
            "min_temp": round(float(row["min_temp"]), 1) if pd.notna(row["min_temp"]) else None,
            "max_temp": round(float(row["max_temp"]), 1) if pd.notna(row["max_temp"]) else None,
            "rainfall": rain_val,
            "wind_speed": round(float(row["wind_speed"]), 1) if pd.notna(row["wind_speed"]) else None,
            "air_pressure": round(float(row["air_pressure"]), 1) if pd.notna(row["air_pressure"]) else None,
            "is_rainy": bool(rain_val is not None and rain_val > 0),
        })
    return res


def get_scoped_timeseries(
    state: Optional[str] = None,
    district: Optional[str] = None,
    station_id: Optional[str] = None,
    limit: int = 365
) -> List[Dict[str, Any]]:
    """Retrieves chronological observations or aggregated daily timeseries for state/district/station."""
    df_full = get_parquet_dataframe()
    if df_full is None:
        return []

    clean_state = _clean_filter_param(state)
    clean_district = _clean_filter_param(district)
    clean_station_id = _clean_filter_param(station_id)

    sub = df_full
    if clean_state:
        sub = sub[sub["state"].astype(str).str.upper() == clean_state.upper()]
    if clean_district:
        sub = sub[sub["district"].astype(str).str.lower() == clean_district.lower()]
    if clean_station_id:
        sub = sub[sub["station_id"].astype(str) == clean_station_id]

    if len(sub) == 0:
        return []

    # Single station scope: return station's actual chronological records
    if clean_station_id:
        sub = sub.sort_values("date_of_record", ascending=False).head(limit).iloc[::-1]
        res = []
        for _, row in sub.iterrows():
            d_str = row["date_of_record"].strftime("%Y-%m-%d") if hasattr(row["date_of_record"], "strftime") else str(row["date_of_record"])[:10]
            rain_val = round(float(row["rainfall"]), 1) if pd.notna(row["rainfall"]) else None
            res.append({
                "station_id": row["station_id"],
                "station_name": row["station_name"],
                "state": row["state"],
                "district": row["district"],
                "date_of_record": d_str,
                "avg_temp": round(float(row["avg_temp"]), 1) if pd.notna(row["avg_temp"]) else None,
                "min_temp": round(float(row["min_temp"]), 1) if pd.notna(row["min_temp"]) else None,
                "max_temp": round(float(row["max_temp"]), 1) if pd.notna(row["max_temp"]) else None,
                "rainfall": rain_val,
                "wind_speed": round(float(row["wind_speed"]), 1) if pd.notna(row["wind_speed"]) else None,
                "air_pressure": round(float(row["air_pressure"]), 1) if pd.notna(row["air_pressure"]) else None,
                "is_rainy": bool(rain_val is not None and rain_val > 0),
            })
        return res
    else:
        # State or District level: aggregate across reporting stations by date
        unique_dates = sorted(sub["date_of_record"].unique(), reverse=True)[:limit]
        sub_dates = sub[sub["date_of_record"].isin(unique_dates)]
        grouped = sub_dates.groupby("date_of_record").agg({
            "avg_temp": "mean",
            "min_temp": "min",
            "max_temp": "max",
            "rainfall": "mean",
            "wind_speed": "mean",
            "air_pressure": "mean",
        }).sort_index()

        res = []
        for dt_val, row in grouped.iterrows():
            d_str = dt_val.strftime("%Y-%m-%d") if hasattr(dt_val, "strftime") else str(dt_val)[:10]
            rain_val = round(float(row["rainfall"]), 1) if pd.notna(row["rainfall"]) else None
            res.append({
                "station_id": f"SCOPED_{clean_state or 'ALL'}_{clean_district or 'ALL'}",
                "station_name": f"{clean_district or clean_state or 'National'} Aggregate",
                "state": clean_state or "ALL",
                "district": clean_district or "ALL",
                "date_of_record": d_str,
                "avg_temp": round(float(row["avg_temp"]), 1) if pd.notna(row["avg_temp"]) else None,
                "min_temp": round(float(row["min_temp"]), 1) if pd.notna(row["min_temp"]) else None,
                "max_temp": round(float(row["max_temp"]), 1) if pd.notna(row["max_temp"]) else None,
                "rainfall": rain_val,
                "wind_speed": round(float(row["wind_speed"]), 1) if pd.notna(row["wind_speed"]) else None,
                "air_pressure": round(float(row["air_pressure"]), 1) if pd.notna(row["air_pressure"]) else None,
                "is_rainy": bool(rain_val is not None and rain_val > 0),
            })
        return res
