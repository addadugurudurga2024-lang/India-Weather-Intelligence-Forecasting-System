"""
Phase 7 Post-Audit Script: Test External Provider & Feature Construction
"""
import urllib.request
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np

def fetch_external_forecast(lat=28.5833, lon=77.2000):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,wind_speed_10m_max&timezone=auto"
    req = urllib.request.Request(url, headers={"User-Agent": "WeatherAudit/1.0"})
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read().decode())

if __name__ == "__main__":
    res = fetch_external_forecast()
    daily = res.get("daily", {})
    times = daily.get("time", [])
    print(f"Retrieved {len(times)} daily horizons from Open-Meteo:")
    for i in range(min(12, len(times))):
        t = times[i]
        t_min = daily.get("temperature_2m_min", [])[i]
        t_max = daily.get("temperature_2m_max", [])[i]
        prob = daily.get("precipitation_probability_max", [])[i]
        precip = daily.get("precipitation_sum", [])[i]
        print(f"Day {i+1} ({t}): Min={t_min}°C, Max={t_max}°C, RainProb={prob}%, Rain={precip}mm")
