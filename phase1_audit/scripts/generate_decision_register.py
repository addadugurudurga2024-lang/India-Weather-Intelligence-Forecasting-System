"""
Registers all evidence-based engineering decisions for Phase 2 based on Tasks 01-16 findings.
"""

import json
from pathlib import Path

DECISION_REGISTER = {
    "P2-DEC-01": {
        "title": "Dual-Regime Temporal Filtering (2015-2020 vs 2021-2025)",
        "evidence": (
            "During 2015-2020, stations recorded only ~44k-67k rows/year with extreme missingness "
            "(Wind speed 68-89%, Air pressure 69-97%, Rainfall 66-70%). From 2021 onwards, observation density "
            "more than doubled to ~142k-150k rows/year and missingness dropped to near-zero (<0.5% for temps, <3.4% for rainfall)."
        ),
        "affected_records": "364,694 historical records (2015-2020) vs 605,645 modern records (2021-2025)",
        "impact": "Training multi-variable models on 2015-2020 data would require massive imputation or discarding 70%+ of features.",
        "options": [
            "Option A: Discard 2015-2020 records for multi-variable forecasting.",
            "Option B: Impute missing variables across 2015-2020.",
            "Option C: Two-tiered modeling: use 2021-2025 as the primary benchmark for full multivariate forecasting, and 2015-2020 exclusively for long-term historical climate trend analysis with temperature."
        ],
        "recommended_approach": "Option C (Two-tiered modeling & benchmarking)",
        "justification": "Preserves sample size and statistical integrity without hallucinating 70% of wind/pressure/rainfall data.",
        "validation_required": "Verify benchmark evaluation metrics strictly on 2021-2025 validation splits."
    },
    "P2-DEC-02": {
        "title": "Composite Station Identifier Construction",
        "evidence": (
            "7 station names correspond to multiple distinct coordinates (e.g. Srinagar at lat 34.0833 vs 33.9833; "
            "Akola, Madurai, Agra, Siliguri, Car Nicobar, Thiruvananthapuram). 21,703 station_name + date duplicate pairs exist."
        ),
        "affected_records": "21,703 observation pairs across 7 multi-coordinate stations and local duplicate pairs.",
        "impact": "Groupby operations on 'station_name' create artificial temporal collisions and corrupt lag features.",
        "options": [
            "Option A: Use station_name alone and average duplicate records.",
            "Option B: Create synthetic station_id = f'{station_name}_{latitude}_{longitude}_{elevation}'."
        ],
        "recommended_approach": "Option B (Synthetic composite station ID)",
        "justification": "Uniquely identifies physical observation towers with identical names and eliminates 93% of station-date duplicate collisions.",
        "validation_required": "Verify that unique(station_id, date_of_record) has zero collisions or handles remaining 1,490 true duplicates deterministically."
    },
    "P2-DEC-03": {
        "title": "Duplicate Observation Resolution (Same Station, Same Date)",
        "evidence": (
            "1,490 records share the identical station_name, coordinates, elevation, and date_of_record, with minor measurement variance."
        ),
        "affected_records": "1,490 duplicate records.",
        "impact": "Violates time-series uniqueness invariant; leads to ambiguous target matching in t+1 forecasting.",
        "options": [
            "Option A: Arbitrarily drop first or last.",
            "Option B: Compute deterministic aggregation (mean for numerical variables) or take record with highest completeness."
        ],
        "recommended_approach": "Option B (Prioritize completeness, then deterministic mean)",
        "justification": "Ensures no arbitrary loss of information and mathematical determinism.",
        "validation_required": "Assert len(df) == len(df.drop_duplicates(subset=['station_id', 'date_of_record']))."
    },
    "P2-DEC-04": {
        "title": "Strict Treatment of Rainfall: Zero vs Missing",
        "evidence": (
            "Rainfall has 257,554 missing values (26.5%) and 366,240 observed zero values (37.7%). "
            "Among non-missing records, zero rainfall accounts for 51.38% and positive rainfall accounts for 48.62%."
        ),
        "affected_records": "257,554 missing rainfall rows.",
        "impact": "Imputing missing rainfall as 0 would artificially inflate zero frequency from 51% to 64% and distort monsoon climatology.",
        "options": [
            "Option A: Impute missing rainfall as 0.0.",
            "Option B: Retain missing as NaN; for rainfall forecasting targets, filter out records where target date has missing rainfall."
        ],
        "recommended_approach": "Option B (Strict masking of missing target dates)",
        "justification": "Preserves genuine meteorological distribution and prevents artificial model bias toward dry days.",
        "validation_required": "Assert zero-rain frequency in training matches observed zero-rain frequency in ground truth."
    },
    "P2-DEC-05": {
        "title": "Physical Plausibility Filtering for Temperature Anomalies",
        "evidence": (
            "1 record has min_temp > max_temp (Jorhat / Lengrabhita, 2024-07-01: min=22.6, max=22.3). "
            "1 record has max_temp = 87.0°C (Jaipur / Sanganer, 2018-04-29). "
            "95 records have avg_temp outside [min_temp, max_temp]."
        ),
        "affected_records": "97 records total (<0.01% of dataset).",
        "impact": "Unbounded loss gradients during regression training on extreme errors.",
        "options": [
            "Option A: Delete all 97 rows.",
            "Option B: Mask invalid values as NaN or recalculate avg_temp where sensor inverted."
        ],
        "recommended_approach": "Option B (Mask erroneous values as NaN; record audit flag)",
        "justification": "Preserves other valid fields (e.g. rainfall, coordinates) while nullifying corrupt temperature fields.",
        "validation_required": "Ensure min_temp <= max_temp across all non-null records."
    },
    "P2-DEC-06": {
        "title": "Strict Chronological Split & Leakage Prevention",
        "evidence": (
            "High temporal autocorrelation in daily weather data across 406 stations."
        ),
        "affected_records": "All modeling and validation pipelines.",
        "impact": "Random k-fold splitting would yield artificially inflated test scores and complete failure in live deployment.",
        "options": [
            "Option A: Random train/test split.",
            "Option B: Expanding-window / Walk-forward rolling temporal split."
        ],
        "recommended_approach": "Option B (Walk-forward chronological validation)",
        "justification": "Standard practice for operational meteorological forecasting.",
        "validation_required": "Assert max(train_date) < min(val_date) for all evaluation folds."
    }
}

def generate_decision_register():
    out_file = Path(r"D:\weather_forcasting\phase1_audit\outputs\task17_decision_register.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(DECISION_REGISTER, f, indent=2)
    print("Decision register saved to", out_file)

if __name__ == "__main__":
    generate_decision_register()
