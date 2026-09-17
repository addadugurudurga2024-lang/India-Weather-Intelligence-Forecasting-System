/**
 * Geospatial and Map Domain Contracts for India Weather Forecasting & Intelligence System
 * Strict, future-compatible TypeScript types for Phase 5 Advanced Visualization.
 */

import type { Station } from './index';

export type MapLayerId = 'stations' | 'temperature' | 'rainfall' | 'elevation' | 'state_density' | 'forecast_overlay';

export type TemperatureMetricType = 'avg_temp' | 'min_temp' | 'max_temp';
export type RainfallMetricType = 'amount_mm' | 'is_rainy' | 'intensity_class';
export type ElevationMetricType = 'elevation_m';
export type ForecastMetricType = 'predicted_temp' | 'predicted_rainfall' | 'rain_probability';

export type DataQualityType = 'OBSERVED' | 'MISSING' | 'FORECAST' | 'HISTORICAL' | 'DERIVED_AGGREGATE';

export interface StationLocation {
  station_id: string;
  station_name: string;
  state: string;
  district: string;
  latitude: number;
  longitude: number;
  elevation_m: number;
}

export interface GeographicRegion {
  id: string; // state code or district identifier
  name: string;
  type: 'STATE' | 'DISTRICT' | 'AGRO_CLIMATIC_ZONE' | string;
  station_count: number;
  stations?: string[]; // station_ids
  station_ids?: string[];
  district_count?: number;
  districts?: string[];
  bounds: {
    minLat: number;
    maxLat: number;
    minLon: number;
    maxLon: number;
  };
  centroid: {
    lat: number;
    lon: number;
  };
  avg_elevation_m: number;
  // Deterministic aggregates clearly labeled as derived
  aggregates?: {
    avg_temp_c?: number | null;
    avg_rainfall_mm?: number | null;
    rainy_station_ratio?: number | null;
    total_reporting_stations?: number;
  };
}

export interface MapPoint {
  x: number;
  y: number;
  lat: number;
  lon: number;
  station_id?: string;
  label?: string;
}

export interface HeatmapPoint extends MapPoint {
  weight: number; // Normalized 0-1
  raw_value: number | null;
  metric_name: string;
  unit: string;
}

export interface ForecastMapPoint extends MapPoint {
  station_id: string;
  station_name: string;
  state: string;
  district: string;
  forecast_date: string;
  predicted_temp_c: number;
  predicted_rainfall_mm: number;
  predicted_rain_probability: number;
  predicted_rain_binary: boolean;
  actual_temp_c?: number | null;
  actual_rainfall_mm?: number | null;
  actual_rain_binary?: boolean | null;
  model_name: string;
  is_holdout_benchmark: boolean;
}

export interface GeographicMetric {
  id: string;
  name: string;
  unit: string;
  min: number;
  max: number;
  colorScale: string[]; // Hex or CSS color ramps
  formatValue: (val: number | null) => string;
}

export interface MapLayer {
  id: MapLayerId;
  label: string;
  description: string;
  unit?: string;
  iconName?: string;
  isOverlay?: boolean;
  hasTimeDimension?: boolean;
  availableMetrics?: string[];
  defaultMetric?: string;
}

export interface MapSelection {
  selectedStationId: string | null;
  selectedStation: Station | null;
  selectedState: string | null;
  selectedDistrict: string | null;
  comparisonStationIds: string[];
}

export interface GeographicFilter {
  state: string;
  district: string;
  stationId: string;
  selectedDate: string;
  layerId: MapLayerId;
  activeMetric: string;
}

export interface VisualizationState {
  zoom: number;
  pan: { x: number; y: number };
  activeLayer: MapLayerId;
  activeMetric: string;
  selectedDate: string;
  availableDates: string[];
  isPlayingAnimation: boolean;
  animationSpeedMs: number;
  hoveredStation: Station | null;
  hoveredPointData: {
    title: string;
    subtitle: string;
    metricLabel: string;
    metricValue: string;
    dataQuality: DataQualityType;
    unit?: string;
    extra?: Record<string, string | number>;
  } | null;
  showBoundaries: boolean;
  showRiskZones: boolean;
}

export interface DailyStationObservationRecord {
  station_id?: string;
  date_of_record?: string;
  avg_temp: number | null;
  min_temp: number | null;
  max_temp: number | null;
  rainfall: number | null; // null represents missing observation, never 0
  wind_speed: number | null;
  air_pressure: number | null;
  is_rainy?: boolean;
}
