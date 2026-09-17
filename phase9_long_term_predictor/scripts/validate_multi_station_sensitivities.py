"""
Phase 9 Multi-Station & Multi-Season Validation Script
Validates:
1. Multi-station geographic sensitivity across 6 distinct Indian biomes.
2. Multi-season temporal sensitivity (Winter, Summer, Monsoon, Post-Monsoon).
3. Elevation lapse rate response (high-altitude Himalayan vs low-altitude plains).
4. Rain probability dynamics (Cherrapunji monsoon vs Jodhpur arid).
5. 100% adherence to physical temperature ordering (T_min <= T_avg <= T_max).
"""

import json
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path("d:/weather_forcasting")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from phase9_long_term_predictor.services.long_term_predictor_engine import predict_long_term

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("validate_sensitivities")

REPRESENTATIVE_STATIONS = {
    "Arid (Rajasthan)": "jodhpur_26.3000_73.0167_217m",
    "Coastal Maritime (Mumbai)": "bombay_colaba_18.9000_72.8167_10m",
    "High Himalayan (Shimla)": "shimla_31.1000_77.1667_2205m",
    "Northeast High Rainfall (Cherrapunji)": "cherrapunji_25.2500_91.7333_1312m",
    "Inland Plateau (Nagpur)": "nagpur_sonegaon_21.1000_79.0500_308m",
    "Island (Port Blair)": "port_blair_11.6667_92.7167_73m",
    "Prompt Use Case (Rajanagaram)": "rajahmundry_rjnagaram_17.1104_81.8182_46m",
}

SEASONS_DATES = {
    "Winter": "2026-01-15",
    "Summer": "2026-05-15",
    "Monsoon": "2026-07-15",
    "Post-Monsoon": "2026-11-15",
}


def main():
    logger.info("Starting Phase 9 Multi-Station & Multi-Season Climate Validation...")
    results_summary = {}

    for biome, stn_id in REPRESENTATIVE_STATIONS.items():
        logger.info(f"\n--- Testing Station: {biome} ({stn_id}) ---")
        results_summary[biome] = {}

        for season, dt in SEASONS_DATES.items():
            res = predict_long_term(stn_id, dt)
            assert res["status"] == "AVAILABLE", f"Failed prediction for {stn_id} on {dt}"
            preds = res["predictions"]

            # 1. Physical ordering check
            assert preds["min_temp"] <= preds["avg_temp"] <= preds["max_temp"], (
                f"Physical ordering violation in {biome} on {dt}: {preds}"
            )

            # 2. Non-negativity check
            assert preds["rainfall"] >= 0.0
            assert preds["wind_speed"] >= 0.0
            assert 0.0 <= preds["rain_probability"] <= 1.0

            results_summary[biome][season] = {
                "date": dt,
                "avg_temp": preds["avg_temp"],
                "min_temp": preds["min_temp"],
                "max_temp": preds["max_temp"],
                "rain_prob_pct": preds["rain_probability_pct"],
                "rainfall_mm": preds["rainfall"],
                "wind_kmh": preds["wind_speed"],
                "pressure_hpa": preds["air_pressure"],
            }
            logger.info(
                f"  [{season} - {dt}]: Avg Temp={preds['avg_temp']}°C ({preds['min_temp']}° to {preds['max_temp']}°), "
                f"Rain Prob={preds['rain_probability_pct']}%, Rain={preds['rainfall']}mm, Wind={preds['wind_speed']}km/h, Pres={preds['air_pressure']}hPa"
            )

    # Cross-station sanity checks:
    # 1. High elevation lapse rate: Shimla summer temperature should be noticeably cooler than Nagpur summer temperature
    shimla_summer_temp = results_summary["High Himalayan (Shimla)"]["Summer"]["avg_temp"]
    nagpur_summer_temp = results_summary["Inland Plateau (Nagpur)"]["Summer"]["avg_temp"]
    assert nagpur_summer_temp - shimla_summer_temp > 10.0, (
        f"Lapse rate anomaly: Nagpur Summer ({nagpur_summer_temp}°C) not sufficiently warmer than Shimla Summer ({shimla_summer_temp}°C)"
    )
    logger.info(f"\n✓ Elevation Lapse Rate Verified: Nagpur Summer ({nagpur_summer_temp}°C) vs Shimla Summer ({shimla_summer_temp}°C), delta={round(nagpur_summer_temp - shimla_summer_temp, 1)}°C")

    # 2. Seasonal temperature cycle: Summer temperature should exceed Winter temperature for all continental stations
    for biome in ["Arid (Rajasthan)", "High Himalayan (Shimla)", "Inland Plateau (Nagpur)", "Prompt Use Case (Rajanagaram)"]:
        t_sum = results_summary[biome]["Summer"]["avg_temp"]
        t_win = results_summary[biome]["Winter"]["avg_temp"]
        assert t_sum > t_win, f"Seasonal inversion in {biome}: Summer ({t_sum}°C) <= Winter ({t_win}°C)"
        logger.info(f"✓ Seasonal Temp Cycle Verified for {biome}: Summer ({t_sum}°C) > Winter ({t_win}°C), delta=+{round(t_sum - t_win, 1)}°C")

    # 3. Monsoon precipitation: Cherrapunji monsoon rain probability should be significantly higher than Jodhpur monsoon rain prob
    cherra_monsoon_p = results_summary["Northeast High Rainfall (Cherrapunji)"]["Monsoon"]["rain_prob_pct"]
    jodh_monsoon_p = results_summary["Arid (Rajasthan)"]["Monsoon"]["rain_prob_pct"]
    assert cherra_monsoon_p > jodh_monsoon_p, f"Rainfall anomaly: Cherrapunji ({cherra_monsoon_p}%) <= Jodhpur ({jodh_monsoon_p}%)"
    logger.info(f"✓ Geographic Precipitation Contrast Verified: Cherrapunji Monsoon ({cherra_monsoon_p}%) vs Jodhpur Monsoon ({jodh_monsoon_p}%)")

    # Save validation report JSON
    out_path = Path("d:/weather_forcasting/phase9_long_term_predictor/reports/multi_station_validation_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2)
    logger.info(f"\nSaved full validation matrix to {out_path}")
    logger.info("All Multi-Station and Multi-Season climate sensitivity checks PASSED!")


if __name__ == "__main__":
    main()
