"""
Phase 1.5 Master Verification Runner
Executes all verification modules, creates diagnostic plots, checks source integrity,
and generates summary outputs.
"""
import logging
import sys
from pathlib import Path

# Add script directories to sys.path
sys.path.append(r"d:\weather_forcasting\phase1_audit\scripts")
sys.path.append(r"d:\weather_forcasting\phase1_verification\scripts")
# pyrefly: ignore [missing-import]
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

from verify_baseline import verify_baseline
from verify_state_reconciliation import verify_states
from verify_station_duplicates import verify_stations_and_duplicates
from verify_temperature_anomalies import verify_temperature_anomalies
from verify_rainfall_statistics import verify_rainfall
from verify_temporal_continuity import verify_temporal_continuity
from verify_phase2_decisions import verify_decisions_and_discrepancies
# pyrefly: ignore [missing-import]
from data_loader import verify_source_integrity, RAW_DATA_PATH, compute_file_hash_and_stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(r"D:\weather_forcasting\phase1_verification\logs\phase1_verification.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("phase1_verification.runner")

DIAG_DIR = Path(r"D:\weather_forcasting\phase1_verification\diagnostics")
DIAG_DIR.mkdir(parents=True, exist_ok=True)

def run_all_verifications():
    logger.info("=== STARTING PHASE 1.5 VERIFICATION AND RECONCILIATION GATE ===")
    
    # Check 1: Initial source integrity
    initial_stats = compute_file_hash_and_stats(RAW_DATA_PATH)
    logger.info("Initial Source Integrity: %s", initial_stats)
    if not verify_source_integrity():
        raise RuntimeError("Source integrity check failed at start of verification!")
        
    # Run modular verifications
    logger.info("Running Baseline Verification...")
    verify_baseline()
    
    logger.info("Running State Reconciliation...")
    verify_states()
    
    logger.info("Running Station & Duplicates Verification...")
    verify_stations_and_duplicates()
    
    logger.info("Running Temperature Anomaly Verification...")
    anom_df = verify_temperature_anomalies()
    
    logger.info("Running Rainfall Statistics Verification...")
    verify_rainfall()
    
    logger.info("Running Temporal Continuity & Forecast Readiness Verification...")
    verify_temporal_continuity()
    
    logger.info("Running Decision Audit & Discrepancy Register Generation...")
    verify_decisions_and_discrepancies()
    
    # Generate verification diagnostic plots
    logger.info("Generating Phase 1.5 diagnostic plots...")
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    
    # 1. Jamshedpur Elevation & Temp Offset Diagnostic
    # pyrefly: ignore [missing-import]
    from data_loader import load_authoritative_data
    df = load_authoritative_data()
    j140 = df[(df['station_name'] == 'Jamshedpur') & (df['elevation'] == 140)].sort_values('date_of_record').reset_index(drop=True)
    j128 = df[(df['station_name'] == 'Jamshedpur') & (df['elevation'] == 128)].sort_values('date_of_record').reset_index(drop=True)
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(j140['date_of_record'].head(100), j140['avg_temp'].head(100), label="Jamshedpur Elev 140m", color='#1f77b4', lw=1.5)
    ax.plot(j128['date_of_record'].head(100), j128['avg_temp'].head(100), label="Jamshedpur Elev 128m (+0.1°C offset)", color='#ff7f0e', linestyle='--', lw=1.5)
    ax.set_title("Verification Diagnostic: Jamshedpur Duplicate Pairs (140m vs 128m, Constant 0.1°C Difference)", fontsize=11, fontweight='bold')
    ax.set_xlabel("Date of Record")
    ax.set_ylabel("Average Temperature (°C)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(DIAG_DIR / "jamshedpur_duplicate_offset_diagnostic.png", dpi=150)
    plt.close(fig)
    
    # 2. 87C Outlier Context Plot
    fig, ax = plt.subplots(figsize=(9, 4))
    nearby = df[(df['station_name'] == 'Jaipur / Sanganer') & (df['date_of_record'] >= '2018-04-20') & (df['date_of_record'] <= '2018-05-10')].sort_values('date_of_record')
    ax.plot(nearby['date_of_record'], nearby['avg_temp'], marker='o', label='Avg Temp', color='#2ca02c')
    ax.plot(nearby['date_of_record'], nearby['min_temp'], marker='s', label='Min Temp', color='#1f77b4')
    ax.plot(nearby['date_of_record'], nearby['max_temp'], marker='^', label='Max Temp', color='#d62728')
    ax.annotate("Isolated 87.0°C Transcription Spike\n(Avg: 38.6°C, Min: 30.0°C)", 
                xy=(pd.to_datetime('2018-04-29'), 87.0), xytext=(pd.to_datetime('2018-04-22'), 75),
                arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8),
                fontsize=9, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.6))
    ax.set_title("Verification Diagnostic: Jaipur / Sanganer 87.0°C Max Temp Outlier Investigation", fontsize=11, fontweight='bold')
    ax.set_xlabel("Date of Record")
    ax.set_ylabel("Temperature (°C)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(DIAG_DIR / "jaipur_87c_anomaly_context.png", dpi=150)
    plt.close(fig)

    # Final post-run source integrity check
    final_stats = compute_file_hash_and_stats(RAW_DATA_PATH)
    logger.info("Final Source Integrity Check: %s", final_stats)
    if initial_stats["sha256"] != final_stats["sha256"]:
        raise RuntimeError("CRITICAL ERROR: Source file was altered during verification!")
    logger.info("Source file byte-for-byte immutability confirmed!")
    logger.info("=== PHASE 1.5 VERIFICATION AND RECONCILIATION COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_all_verifications()
