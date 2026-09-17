"""
Deterministic MongoDB Development Database Seeder
Seeds the india_weather_intelligence database using canonical Phase 2 & Phase 3 artifacts.
Safe execution: Checks if MongoDB connection is available; exports JSON dump if offline.
"""

import json
import os
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
STATIONS_FILE = Path(r"d:\weather_forcasting\phase2_canonical\outputs\station_metadata.json")
MODELS_FILE = Path(r"d:\weather_forcasting\phase3_models\model_registry.json")
METRICS_FILE = Path(r"d:\weather_forcasting\phase3_models\metrics\metrics_summary.json")

def prepare_seed_data():
    print("Preparing deterministic MongoDB seed documents...")
    
    # 1. Stations
    stations_raw = json.load(open(STATIONS_FILE, "r", encoding="utf-8"))
    stations_docs = []
    for sid, s in stations_raw.items():
        doc = {
            "station_id": s["station_id"],
            "station_name": s["station_name"],
            "state": s["state"],
            "district": s["district"],
            "latitude": float(s["latitude"]),
            "longitude": float(s["longitude"]),
            "elevation_m": float(s["elevation_m"]),
            "record_count_total": int(s["record_count_total"]),
            "record_count_modern_2021_2025": int(s["record_count_modern_2021_2025"]),
            "first_observed_date": s["first_observed_date"],
            "last_observed_date": s["last_observed_date"],
            "location": {
                "type": "Point",
                "coordinates": [float(s["longitude"]), float(s["latitude"])]
            },
            "created_at": datetime.utcnow().isoformat()
        }
        stations_docs.append(doc)
        
    # 2. Model Metadata
    models_raw = json.load(open(MODELS_FILE, "r", encoding="utf-8"))
    models_docs = models_raw.get("models", [])
    for m in models_docs:
        m["registered_at"] = datetime.utcnow().isoformat()
        
    # Save seed export files locally
    seeds_dir = BASE_DIR / "seeds"
    seeds_dir.mkdir(parents=True, exist_ok=True)
    
    with open(seeds_dir / "stations.seed.json", "w", encoding="utf-8") as f:
        json.dump(stations_docs, f, indent=2)
        
    with open(seeds_dir / "model_metadata.seed.json", "w", encoding="utf-8") as f:
        json.dump(models_docs, f, indent=2)
        
    print(f"Generated {len(stations_docs)} stations and {len(models_docs)} model metadata seed documents in {seeds_dir}")

    # Attempt pymongo seed if local mongo is running
    try:
        from pymongo import MongoClient
        mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        client.server_info() # trigger exception if offline
        db = client["india_weather_intelligence"]
        
        # Insert stations
        db.stations.drop()
        db.stations.insert_many(stations_docs)
        
        # Insert model_metadata
        db.model_metadata.drop()
        db.model_metadata.insert_many(models_docs)
        
        print(f"Successfully seeded MongoDB database 'india_weather_intelligence' directly at {mongo_uri}!")
    except Exception as e:
        print(f"Local MongoDB service not currently connected ({e}). Offline JSON seed files were successfully generated.")

if __name__ == "__main__":
    prepare_seed_data()
