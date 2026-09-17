"""Configuration settings for India Weather Forecasting & Intelligence System backend."""

import os
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field

# Absolute project root directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseModel):
    PROJECT_NAME: str = "India Weather Forecasting & Intelligence System"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # CORS origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]

    # Authoritative File Paths
    ROOT_PATH: Path = BASE_DIR
    CANONICAL_PARQUET_PATH: Path = BASE_DIR / "phase2_canonical" / "outputs" / "canonical_weather_full.parquet"
    CANONICAL_STATIONS_PATH: Path = BASE_DIR / "phase2_canonical" / "outputs" / "station_metadata.json"
    FRONTEND_STATIONS_PATH: Path = BASE_DIR / "frontend" / "src" / "data" / "authoritativeStations.json"
    DISTRICT_MAPPING_PATH: Path = BASE_DIR / "phase2_canonical" / "outputs" / "station_metadata.json"
    
    # Model Directories
    PHASE3_METRICS_PATH: Path = BASE_DIR / "phase3_models" / "metrics" / "phase3_authoritative_metrics.json"
    PHASE7_MODELS_DIR: Path = BASE_DIR / "phase7_forecasting" / "models"
    PHASE9_MODELS_DIR: Path = BASE_DIR / "phase9_long_term_predictor" / "models"
    PHASE9_CLIMATOLOGY_PATH: Path = BASE_DIR / "phase9_long_term_predictor" / "data" / "station_climatology_413.json"
    
    # Optional Database URL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mongodb://localhost:27017/india_weather_intelligence")

    model_config = {
        "case_sensitive": True,
        "extra": "allow",
    }


settings = Settings()
