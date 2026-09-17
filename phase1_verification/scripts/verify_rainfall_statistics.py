"""
Phase 1.5 Verification Suite - Rainfall Statistics & Extremes
Recalculates missing, zero, positive counts, quantiles, and extreme thresholds (>100mm, >200mm, >300mm).
"""
import json
from pathlib import Path
import pandas as pd
# pyrefly: ignore [missing-import]
from data_loader import load_authoritative_data

def verify_rainfall():
    df = load_authoritative_data()
    rf = df['rainfall']
    
    missing_count = int(rf.isna().sum())
    non_null = rf.dropna()
    total_non_null = int(len(non_null))
    zero_count = int((non_null == 0).sum())
    pos_count = int((non_null > 0).sum())
    neg_count = int((non_null < 0).sum())
    
    pos_rf = non_null[non_null > 0]
    
    # Quantiles
    quantiles_overall = {f"q{int(q*100):02d}": float(non_null.quantile(q)) for q in [0.25, 0.50, 0.75, 0.90, 0.95, 0.98, 0.99, 0.999]}
    quantiles_pos = {f"q{int(q*100):02d}": float(pos_rf.quantile(q)) for q in [0.25, 0.50, 0.75, 0.90, 0.95, 0.98, 0.99, 0.999]}
    
    # Extreme thresholds
    rf_gt_100 = int((non_null > 100).sum())
    rf_gt_200 = int((non_null > 200).sum())
    rf_gt_300 = int((non_null > 300).sum())
    
    results = {
        "total_records": int(len(df)),
        "missing_count": missing_count,
        "missing_rate": float(missing_count / len(df)),
        "non_null_count": total_non_null,
        "zero_count": zero_count,
        "zero_rate_overall": float(zero_count / len(df)),
        "zero_rate_among_observed": float(zero_count / total_non_null),
        "positive_count": pos_count,
        "positive_rate_overall": float(pos_count / len(df)),
        "positive_rate_among_observed": float(pos_count / total_non_null),
        "negative_count": neg_count,
        "min": float(non_null.min()),
        "max": float(non_null.max()),
        "mean_overall": float(non_null.mean()),
        "mean_positive": float(pos_rf.mean()),
        "median_positive": float(pos_rf.median()),
        "std_overall": float(non_null.std()),
        "overall_quantiles": quantiles_overall,
        "positive_quantiles": quantiles_pos,
        "rf_gt_100mm_count": rf_gt_100,
        "rf_gt_200mm_count": rf_gt_200,
        "rf_gt_300mm_count": rf_gt_300
    }
    
    out_json = Path(r"D:\weather_forcasting\phase1_verification\outputs\rainfall_verification.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("Rainfall verification completed and saved to:", out_json)
    return results

if __name__ == "__main__":
    verify_rainfall()
