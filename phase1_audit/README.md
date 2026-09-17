# Phase 1: Dataset Audit, Data Quality Assessment & ML Readiness

This directory contains the complete, reproducible Phase 1 engineering audit tooling, diagnostic data artifacts, logs, and formal audit report for the Weather Forecasting & Intelligence System.

## Directory Structure

```
phase1_audit/
├── cache/                  # Fast read-only parquet cache and source integrity reference
├── diagnostics/            # Diagnostic visualization charts (PNG)
│   ├── fig1_temporal_density.png
│   ├── fig2_temp_plausibility.png
│   ├── fig3_rainfall_distribution_log.png
│   └── fig4_station_locations_map.png
├── logs/                   # Structured execution logs
│   └── phase1_audit.log
├── outputs/                # Machine-readable analytical outputs (JSON and CSV)
│   ├── task02_dataset_profile.json
│   ├── task03_field_semantics.json
│   ├── task04_time_coverage.json
│   ├── task05_station_identity.json
│   ├── task06_duplicates.json
│   ├── task07_missingness.json
│   ├── task08_rainfall_analysis.json
│   ├── task09_correlations.json
│   ├── task09_weather_statistics.csv
│   ├── task10_domain_validation.json
│   ├── task11_annual_summary.csv
│   ├── task11_seasonal_summary.csv
│   ├── task12_forecasting_assessment.json
│   ├── task13_leakage_and_validation.json
│   ├── task14_geospatial_feasibility.json
│   ├── task17_decision_register.json
│   └── task18_readiness_assessment.json
├── reports/
│   └── phase1_audit_report.md  # Comprehensive Phase 1 Markdown Audit Report
├── scripts/                # Modular, deterministic audit Python scripts
│   ├── data_loader.py
│   ├── run_audit.py
│   ├── generate_decision_register.py
│   └── generate_readiness_assessment.py
└── README.md
```

## How to Run the Audit

From the workspace root (`d:\weather_forcasting`):
```bash
python phase1_audit/scripts/run_audit.py
python phase1_audit/scripts/generate_decision_register.py
python phase1_audit/scripts/generate_readiness_assessment.py
```

## Source Data Protection
The authoritative source dataset `india_weather_rainfall_data.xlsx` remains strictly read-only and immutable. SHA256 integrity verification is automatically enforced on every run.
