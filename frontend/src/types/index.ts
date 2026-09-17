/**
 * Domain types for India Weather Forecasting & Intelligence System
 * Strict, future-compatible definitions matching Phase 2 canonical data and Phase 3 model registry.
 */

export interface Station {
  station_id: string;
  station_name: string;
  state: string;
  district: string;
  latitude: number;
  longitude: number;
  elevation_m: number;
  record_count_total: number;
  record_count_modern_2021_2025: number;
  first_observed_date: string;
  last_observed_date: string;
}

export interface WeatherObservation {
  station_id: string;
  station_name?: string;
  state?: string;
  district?: string;
  date_of_record: string;
  avg_temp: number | null;
  min_temp: number | null;
  max_temp: number | null;
  rainfall: number | null; // null represents missing observation, never zero
  wind_speed: number | null;
  air_pressure: number | null;
  is_rainy?: boolean;
}

export interface ForecastResult {
  station_id: string;
  station_name: string;
  state: string;
  district: string;
  forecast_date: string;
  predicted_temp: number;
  predicted_rainfall_amount: number;
  predicted_rain_probability: number;
  predicted_rain_binary: boolean;
  model_temperature: string;
  model_rainfall: string;
  model_classification: string;
  generated_at: string;
  is_preview: boolean; // Explicitly marks development preview vs live
}

export type TimelineDayStatus = 'OBSERVED' | 'MODEL ESTIMATE' | 'CURRENT' | 'FORECAST' | 'DERIVED' | 'UNAVAILABLE';

export interface TimelineDayUncertainty {
  temp_interval_80: [number, number];
  temp_interval_95: [number, number];
  rainfall_interval_80: [number, number];
  methodology: string;
}

export interface TimelineDayEntry {
  date: string;
  relative_day: number; // -12 to +12
  status: TimelineDayStatus;
  is_observed: boolean;
  provenance: string;
  temperature_avg: number | null;
  temperature_min: number | null;
  temperature_max: number | null;
  rainfall_amount: number | null;
  rain_probability: number | null;
  rain_binary: boolean | null;
  wind_speed: number | null;
  air_pressure: number | null;
  uncertainty?: TimelineDayUncertainty | null;
  model_metadata?: {
    model_id: string;
    model_version: string;
    horizon_name: string;
    training_period: string;
  } | null;
}

export interface Operational25DayTimeline {
  station_id: string;
  station_name: string;
  district: string;
  state: string;
  latitude: number;
  longitude: number;
  elevation_m: number;
  forecast_origin: string;
  generated_at: string;
  is_historical_simulation: boolean;
  timeline_summary: {
    total_days: number;
    historical_observed_count: number;
    current_count: number;
    forecast_count: number;
    unavailable_count: number;
  };
  timeline: TimelineDayEntry[];
}

export interface MultiHorizonSummary {
  metadata: {
    phase: string;
    authoritative_date: string;
    supported_horizons: number[];
  };
  benchmarks_by_horizon: Record<string, any>;
  skill_degradation: {
    avg_temp_mae: number[];
    min_temp_mae: number[];
    max_temp_mae: number[];
    wind_speed_mae: number[];
    air_pressure_mae: number[];
    rainfall_mae: number[];
    rain_binary_roc_auc: number[];
  };
  model_selection_matrix: Array<{
    horizon: string;
    days_ahead: number;
    best_temp_model: string;
    temp_mae: number;
    temp_skill_vs_persistence: number;
    best_rainfall_model: string;
    rainfall_mae: number;
    best_rain_cls_model: string;
    rain_roc_auc: number;
    recommendation: string;
  }>;
  uncertainty_and_calibration: {
    continuous_intervals: Record<string, any>;
    rain_calibration_bins: Array<{
      bin_range: string;
      mean_predicted_prob: number;
      empirical_frequency: number;
      sample_count: number;
    }>;
    expected_calibration_error: number;
    brier_score: number;
  };
  seasonal_evaluation: Record<string, any>;
  geographic_evaluation: Record<string, any>;
  known_limitations: string[];
}

export interface RegressionMetrics {
  mae: number;
  rmse: number;
  r2: number;
  mae_rainy_only?: number | null;
  rmse_rainy_only?: number | null;
  count?: number;
  train_rows?: number;
  val_rows?: number;
  train_time_sec?: number;
}

export interface ClassificationMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  roc_auc: number;
  pr_auc: number;
  confusion_matrix?: number[][];
  count?: number;
  pos_count?: number;
  neg_count?: number;
  train_rows?: number;
  val_rows?: number;
  train_time_sec?: number;
}

export interface TargetModelMetrics {
  baseline: {
    fold1_val?: RegressionMetrics | ClassificationMetrics;
    fold2_val?: RegressionMetrics | ClassificationMetrics;
    holdout?: RegressionMetrics | ClassificationMetrics;
  };
  xgboost: {
    fold1?: RegressionMetrics | ClassificationMetrics;
    fold2?: RegressionMetrics | ClassificationMetrics;
    holdout?: RegressionMetrics | ClassificationMetrics;
  };
  lstm: {
    fold1?: RegressionMetrics | ClassificationMetrics;
    fold2?: RegressionMetrics | ClassificationMetrics;
    holdout?: RegressionMetrics | ClassificationMetrics;
  };
}

export interface MetricsSummary {
  metadata: {
    phase: string;
    authoritative_source_hash: string;
    cross_validation_strategy: string;
    holdout_period: string;
    models_compared: string[];
    targets: string[];
  };
  target_a_temperature: TargetModelMetrics;
  target_b_rainfall_amount: TargetModelMetrics;
  target_c_rain_binary: TargetModelMetrics;
}

export interface ModelMetadataItem {
  model_id: string;
  model_family: 'XGBoost' | 'LSTM' | 'Baseline';
  target: 'target_next_day_temp' | 'target_next_day_rainfall_amount' | 'target_next_day_rain_binary';
  task: 'regression' | 'binary_classification';
  artifact_path: string;
  preprocessor_path?: string;
  transformation?: string;
  sequence_length?: number;
  training_period: string;
  validation_period: string;
  status: 'APPROVED_FOR_PRODUCTION_CANDIDATE' | 'BENCHMARKED';
}

export interface ModelRegistry {
  version: string;
  phase: string;
  created_at: string;
  models: ModelMetadataItem[];
}

export interface FilterState {
  state: string; // "ALL" or state code
  district: string; // "ALL" or district name
  stationId: string; // "ALL" or specific station_id
  dateRange: {
    startDate: string;
    endDate: string;
  };
  season: 'ALL' | 'Winter' | 'Pre-Monsoon' | 'Monsoon' | 'Post-Monsoon';
  rainfallFilter: 'ALL' | 'RAINY_ONLY' | 'DRY_ONLY';
}

export interface DashboardKPI {
  id: string;
  title: string;
  value: string | number;
  unit?: string;
  subtext: string;
  status: 'normal' | 'info' | 'warning' | 'success';
  sparklineData?: number[];
}

export interface GeographicEntity {
  state_code: string;
  state_name: string;
  station_count: number;
  avg_elevation: number;
  stations: Station[];
}

export * from './geospatial';

// ==========================================
// Phase 9 — Long-Term Weather Predictor Types
// ==========================================

export interface LongTermPredictionRequest {
  date: string; // YYYY-MM-DD
  station_id: string;
}

export interface LongTermPredictions {
  avg_temp: number;
  min_temp: number;
  max_temp: number;
  rainfall: number;
  rain_probability: number;
  rain_probability_pct: number;
  wind_speed: number;
  air_pressure: number;
}

export interface LongTermUncertainty {
  avg_temp_interval_80: [number, number];
  min_temp_interval_80: [number, number];
  max_temp_interval_80: [number, number];
  rainfall_interval_80: [number, number];
  wind_speed_interval_80: [number, number];
  air_pressure_interval_80: [number, number];
  method: string;
}

export interface LongTermHistoricalReference {
  station_name: string;
  state: string;
  district: string;
  elevation_m: number;
  latitude: number;
  longitude: number;
  calendar_context: {
    selected_date: string;
    month: string;
    season: string;
    day_of_year: number;
  };
  station_monthly_climatology: {
    month: string;
    historical_mean_temp: number | null;
    historical_min_temp: number | null;
    historical_max_temp: number | null;
    historical_rain_frequency_pct: number;
    historical_mean_rainfall_mm: number;
    historical_mean_wind_kmh: number;
    historical_mean_pressure_hpa: number;
  };
  station_overall_climatology: Record<string, any>;
}

export interface LongTermPredictionResult {
  status: 'AVAILABLE' | 'UNAVAILABLE';
  prediction_type: string;
  prediction_date: string;
  station_id: string;
  station_name: string;
  state: string;
  district: string;
  coordinates: {
    latitude: number;
    longitude: number;
    elevation_m: number;
  };
  predictions?: LongTermPredictions;
  uncertainty?: LongTermUncertainty;
  historical_reference?: LongTermHistoricalReference;
  how_prediction_made?: Array<{ step: number; title: string; detail: string }>;
  provenance?: {
    inference_source?: string;
    model_version?: string;
    models_used: Record<string, string>;
    training_window: string;
    validation_window: string;
    source_dataset_sha256: string;
    physical_ordering_applied: boolean;
  };
  limitations?: string[];
  error?: string;
}
