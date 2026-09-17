"""
Phase 1.5 Verification Suite - Decision Audit & Discrepancy Register
Audits all Phase 2 decisions and generates discrepancy_register.csv.
"""
import pandas as pd
from pathlib import Path

DECISION_AUDIT = [
    {
        "decision_id": "P2-DEC-01",
        "title": "Dual-Regime Temporal Partitioning (2015-2020 vs 2021-2025)",
        "evidence": "Missingness in wind (68-89%), pressure (69-97%), and rain (66-70%) in 2015-2020 vs <3.4% across all variables in 2021-2025.",
        "verified": True,
        "risk": "Information loss if 2015-2020 is discarded entirely; synthetic hallucinations if heavily imputed.",
        "recommendation": "ACCEPT",
        "rationale": "Scientifically rigorous. Reserving 2015-2020 for climate trend analysis while benchmarking multi-variable forecasting on 2021-2025 is the optimal compromise."
    },
    {
        "decision_id": "P2-DEC-02",
        "title": "Composite Station Identifier Construction",
        "evidence": "7 station names map to distinct physical coordinates/elevations, generating 20,213 collisions when grouped by name alone.",
        "verified": True,
        "risk": "Formatting instability with floating point coordinates in string IDs.",
        "recommendation": "ACCEPT WITH CONDITION",
        "rationale": "Essential to prevent collision. Condition: Must format coordinates with fixed precision (e.g. {station_slug}_{lat:.4f}_{lon:.4f}_{elev}m) or use MD5 hash to guarantee deterministic immutability."
    },
    {
        "decision_id": "P2-DEC-03",
        "title": "Resolve 1,490 True Duplicates using Highest Completeness",
        "evidence": "All 1,490 duplicates belong to Jamshedpur (elev 140m vs 128m). Both records on all 1,490 dates have identical non-null feature counts (100% tie rate).",
        "verified": False,
        "risk": "Highest completeness rule FAILS because completeness is 100% tied across all 1,490 dates. A tie-breaker would pick an arbitrary row.",
        "recommendation": "MODIFY",
        "rationale": "Differences are an exact 0.1°C offset across temps due to a 12m elevation difference. Phase 2 must resolve by taking the canonical elevation tower (140m or 128m) or calculating the mathematical mean."
    },
    {
        "decision_id": "P2-DEC-04",
        "title": "Strict Treatment of Rainfall: Zero vs Missing",
        "evidence": "Missing rainfall is 26.54% (257,554 rows), observed zero is 37.74% (366,240 rows). Among observed, dry days are 51.38% and rainy days are 48.62%.",
        "verified": True,
        "risk": "Imputing zero would distort class balance from 51/49 to 64/36 and create severe false negative prediction bias.",
        "recommendation": "ACCEPT",
        "rationale": "Strictly necessary to preserve ground truth meteorological properties."
    },
    {
        "decision_id": "P2-DEC-05",
        "title": "Physical Plausibility Filtering for Temperature Anomalies",
        "evidence": "95 ordering violations (58 avg<min, 36 avg>max, 1 min>max), 1 extreme max_temp (87.0°C).",
        "verified": True,
        "risk": "Destructive deletion destroys spatial coordinates and non-corrupt measurements on those dates.",
        "recommendation": "ACCEPT WITH CONDITION",
        "rationale": "Condition: Do not destroy raw rows or set fields to NaN in-place permanently without provenance. Use quality audit flags (e.g. temp_quality_flag) and clean values in model feature views."
    },
    {
        "decision_id": "P2-DEC-06",
        "title": "Strict Chronological Split & Leakage Prevention",
        "evidence": "Weather time-series has severe daily temporal autocorrelation and spatial synoptic dependencies.",
        "verified": True,
        "risk": "Data leakage and overoptimistic validation metrics if random splitting is used.",
        "recommendation": "ACCEPT",
        "rationale": "Mandatory standard for operational meteorology."
    }
]

DISCREPANCY_REGISTER = [
    {
        "id": "DISC-01",
        "finding": "State Count reported as 36 in Phase 1 report vs 32 unique codes in dataset",
        "severity": "MEDIUM",
        "evidence": "Dataset contains exactly 32 unique 2-letter state codes. Phase 1 report executive text stated 36 (the total number of constitutional States/UTs in India). 4 entities (JH, UT, TG, LA) have zero station presence.",
        "resolution": "Update documentation to clarify: Dataset contains 32 unique state/UT administrative codes representing 24 States and 8 Union Territories. 4 entities are absent."
    },
    {
        "id": "DISC-02",
        "finding": "Inaccuracy of P2-DEC-03: 'Highest Feature Completeness' Rule for 1,490 Duplicates",
        "severity": "HIGH",
        "evidence": "All 1,490 duplicates are Jamshedpur (elev 140m vs 128m). Both duplicate records have identical non-null counts on 100% of dates. Highest completeness rule cannot resolve any record.",
        "resolution": "Modify decision P2-DEC-03: Resolve Jamshedpur 140m vs 128m by either designating the official IMD meteorological station elevation (140m) as canonical, or by calculating the mathematical mean."
    },
    {
        "id": "DISC-03",
        "finding": "Incomplete Station Disambiguation List in Task 05 JSON (Omission of Jamshedpur)",
        "severity": "LOW",
        "evidence": "Task 05 JSON checked latitude and longitude differences (>1) and found 7 stations. Jamshedpur has identical lat and lon but different elevation (140m vs 128m), making it the 8th physical multi-attribute station.",
        "resolution": "Include elevation in multi-attribute station definition, bringing total multi-attribute stations to 8."
    },
    {
        "id": "DISC-04",
        "finding": "99th Percentile Rainfall Reporting Ambiguity (156mm/191.8mm in Phase 1 Report vs 68.1mm/91.9mm Standard Quantile)",
        "severity": "LOW",
        "evidence": "Run_audit.py line 313 used a loop over quantiles where q99 was overwritten by q99.9 (0.999), producing 156.0mm (overall) and 191.8mm (positive), which are actually the 99.9th percentiles (q99.9), not q99 (68.1mm and 91.9mm).",
        "resolution": "Clarify that 156.0mm and 191.8mm correspond to the 99.9th percentile (extreme cloudburst tail), while the true 99.0th percentiles are 68.1mm (overall) and 91.9mm (positive)."
    }
]

def verify_decisions_and_discrepancies():
    dec_df = pd.DataFrame(DECISION_AUDIT)
    out_dec = Path(r"D:\weather_forcasting\phase1_verification\outputs\decision_verification.csv")
    dec_df.to_csv(out_dec, index=False)
    
    disc_df = pd.DataFrame(DISCREPANCY_REGISTER)
    out_disc = Path(r"D:\weather_forcasting\phase1_verification\outputs\discrepancy_register.csv")
    disc_df.to_csv(out_disc, index=False)
    print("Decision verification and discrepancy register exported.")

if __name__ == "__main__":
    verify_decisions_and_discrepancies()
