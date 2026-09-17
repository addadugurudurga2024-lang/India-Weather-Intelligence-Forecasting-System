# Phase 2: Canonical Dataset Construction & Feature Engineering Foundation

This directory houses the operational Phase 2 codebase, artifacts, automated test suite, and reports for the Weather Forecasting & Intelligence System.

## Directory Structure

```
phase2_canonical/
├── scripts/
│   ├── config.py                      # Constants, file paths, station slug & ID generation
│   ├── clean_and_standardize.py        # P2-DEC-02, P2-DEC-03, P2-DEC-05 implementation
│   ├── build_canonical_dataset.py     # Assembly of full and forecasting canonical datasets
│   ├── feature_engineering.py         # Leakage-free, gap-aware lags, rolling stats, targets
│   ├── temporal_split_builder.py      # Walk-forward chronological cross-validation manifests
│   └── run_phase2_pipeline.py         # End-to-end master pipeline runner
├── outputs/
│   ├── canonical_weather_full.parquet        # 968,849 rows (2015-2025)
│   ├── canonical_weather_forecasting.parquet # 604,155 rows (2021-2025)
│   ├── features_engineered.parquet           # 604,155 rows, 40 feature & target columns
│   ├── station_metadata.json                 # 413 physical station catalog
│   ├── data_dictionary.json                  # Schema and feature definitions
│   └── temporal_split_manifest.json          # Folds 1 & 2 + Out-of-time holdout test
├── tests/
│   └── test_canonical_integrity.py     # Automated assertions for uniqueness, lags, immutability
├── reports/
│   └── phase2_engineering_report.md    # Comprehensive Phase 2 sign-off report
└── logs/
    └── phase2_pipeline.log             # Execution logging
```

## Running the Pipeline and Tests

To re-run the entire pipeline from scratch:
```powershell
python phase2_canonical/scripts/run_phase2_pipeline.py
```

To run the automated verification test suite:
```powershell
python phase2_canonical/tests/test_canonical_integrity.py
```

## Core Invariants Enforced
- **Zero Duplicate Rows:** `(station_id, date_of_record)` is guaranteed 100% unique.
- **Zero Data Leakage:** Lag and rolling features are strictly backward-looking.
- **Gap Awareness:** Calendar transitions greater than 1 day produce `NaN` in lag features.
- **Source Immutability:** Raw Excel file SHA256 is programmatically verified on every run.
