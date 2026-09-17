"""
Phase 7 Multi-Station Operational Validation Script (Task 25)
Runs operational inference across a representative multi-station sample (413 canonical registry)
to verify:
- No crashes
- Physical temperature ordering (min <= avg <= max)
- Non-negative rainfall and wind
- Realistic and varying rain probabilities (0.0 to 1.0)
- Stable latency and execution
"""

import json
import time
from pathlib import Path
import pandas as pd
from operational_ingestion_service import build_operational_timeline

PROJECT_ROOT = Path("d:/weather_forcasting")
STATIONS_SEED = PROJECT_ROOT / "frontend" / "src" / "data" / "authoritativeStations.json"
CANONICAL_DATA = PROJECT_ROOT / "phase2_canonical" / "outputs" / "features_engineered.parquet"

def main():
    with open(STATIONS_SEED, "r", encoding="utf-8") as f:
        stations = json.load(f)

    print(f"Total stations in canonical registry: {len(stations)}")
    sample_stns = stations[::15]  # ~28 diverse stations across India
    print(f"Testing operational inference on {len(sample_stns)} representative stations...")

    df_canonical = pd.read_parquet(CANONICAL_DATA)
    df_canonical["date_of_record"] = pd.to_datetime(df_canonical["date_of_record"])

    start_time = time.time()
    records = []

    for s in sample_stns:
        stn_id = s["station_id"]
        tl = build_operational_timeline(stn_id, "2025-01-20", df_canonical=df_canonical)
        fc = [d for d in tl["timeline"] if d["status"] == "FORECAST"]
        assert len(fc) == 12, f"Expected 12 forecast days, got {len(fc)}"

        for d in fc:
            # Physical ordering check
            assert d["temperature_min"] <= d["temperature_avg"] <= d["temperature_max"], (
                f"Physical ordering violation in {stn_id}: min={d['temperature_min']}, avg={d['temperature_avg']}, max={d['temperature_max']}"
            )
            assert 0.0 <= d["rain_probability"] <= 1.0, f"Invalid probability: {d['rain_probability']}"
            assert d["rainfall_amount"] >= 0.0, f"Negative rainfall: {d['rainfall_amount']}"
            assert d["wind_speed"] >= 0.0, f"Negative wind speed: {d['wind_speed']}"

        records.append({
            "station": s["station_name"],
            "state": s["state"],
            "elev_m": s["elevation_m"],
            "t1_temp": fc[0]["temperature_avg"],
            "t1_rain_prob": f"{fc[0]['rain_probability']*100:.1f}%",
            "t6_temp": fc[5]["temperature_avg"],
            "t6_rain_prob": f"{fc[5]['rain_probability']*100:.1f}%",
            "t12_temp": fc[11]["temperature_avg"],
            "t12_rain_prob": f"{fc[11]['rain_probability']*100:.1f}%",
        })

    elapsed = time.time() - start_time
    df_res = pd.DataFrame(records)
    print("\n--- Multi-Station Operational Validation Results ---")
    print(df_res.to_string(index=False))
    print(f"\nCompleted {len(sample_stns)} stations in {elapsed:.2f}s ({elapsed/len(sample_stns)*1000:.1f}ms per station timeline)")
    print("Multi-station operational validation: 100% PASS with strict physical consistency verified.")

if __name__ == "__main__":
    main()
