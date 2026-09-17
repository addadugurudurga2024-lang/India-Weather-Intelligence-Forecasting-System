/**
 * Centralized Geographic & Geospatial Data Service
 * Provides deterministic access to:
 * - 413 canonical physical stations
 * - Authoritative observations from 2025 canonical records
 * - Phase 3 XGBoost holdout forecasts
 * - State aggregates and bounding boxes
 * - Accurate India projection mathematics
 * - IMD-standard meteorological classifications
 */

import stationsData from '../data/authoritativeStations.json';
import regionsData from '../data/authoritativeRegions.json';
import observationsSnapshot from '../data/authoritativeObservationsSnapshot.json';
import forecastSnapshots from '../data/authoritativeForecastSnapshots.json';

import type { Station } from '../types';
import type {
  GeographicRegion,
  DailyStationObservationRecord,
  ForecastMapPoint,
  DataQualityType
} from '../types/geospatial';

// Authoritative Indian subcontinent bounding extents
export const INDIA_GEO_BOUNDS = {
  minLat: 6.5,
  maxLat: 37.5,
  minLon: 68.0,
  maxLon: 97.5
};

export const CANONICAL_STATIONS: Station[] = stationsData as Station[];
export const GEOGRAPHIC_REGIONS: GeographicRegion[] = regionsData as unknown as GeographicRegion[];

const observationsMap = (observationsSnapshot as unknown as {
  dates: string[];
  station_count: number;
  observations_by_date: Record<string, Record<string, DailyStationObservationRecord>>;
}).observations_by_date;

const forecastMap = (forecastSnapshots as {
  model_family: string;
  benchmark_period: string;
  forecast_dates: string[];
  forecasts_by_date: Record<string, Record<string, any>>;
}).forecasts_by_date;

export class GeographicService {
  /**
   * Get all 413 canonical stations
   */
  static getAllStations(): Station[] {
    return CANONICAL_STATIONS;
  }

  /**
   * Get station by ID
   */
  static getStationById(stationId: string): Station | undefined {
    return CANONICAL_STATIONS.find((s) => s.station_id === stationId);
  }

  /**
   * Get all state regions
   */
  static getAllRegions(): GeographicRegion[] {
    return GEOGRAPHIC_REGIONS;
  }

  /**
   * Get state region by state name
   */
  static getRegionById(stateName: string): GeographicRegion | undefined {
    return GEOGRAPHIC_REGIONS.find((r) => r.name === stateName);
  }

  /**
   * Get list of dates with observed data (2025)
   */
  static getAvailableObservationDates(): string[] {
    return (observationsSnapshot as any).dates || [];
  }

  /**
   * Get list of available holdout forecast dates
   */
  static getAvailableForecastDates(): string[] {
    return (forecastSnapshots as any).forecast_dates || [];
  }

  /**
   * Get default selected date (latest available date in dataset)
   */
  static getDefaultDate(): string {
    const dates = this.getAvailableObservationDates();
    return dates.length > 0 ? dates[dates.length - 1] : '2025-02-10';
  }

  /**
   * Get observations for all stations on a given date
   */
  static getObservationsForDate(dateStr: string): Record<string, DailyStationObservationRecord> {
    return observationsMap[dateStr] || {};
  }

  /**
   * Get forecasts for all stations on a given date
   */
  static getForecastsForDate(dateStr: string): Record<string, ForecastMapPoint> {
    const rawForDate = forecastMap[dateStr] || {};
    const result: Record<string, ForecastMapPoint> = {};

    for (const [stnId, pred] of Object.entries(rawForDate)) {
      const station = this.getStationById(stnId);
      if (!station) continue;

      const pt = this.projectCoordinates(station.latitude, station.longitude, 800, 720);

      result[stnId] = {
        x: pt.x,
        y: pt.y,
        lat: station.latitude,
        lon: station.longitude,
        station_id: stnId,
        station_name: station.station_name,
        state: station.state,
        district: station.district,
        forecast_date: dateStr,
        predicted_temp_c: pred.predicted_temp,
        predicted_rainfall_mm: pred.predicted_rainfall,
        predicted_rain_probability: pred.rain_probability,
        predicted_rain_binary: pred.predicted_rain_binary,
        actual_temp_c: pred.actual_temp,
        actual_rainfall_mm: pred.actual_rainfall,
        actual_rain_binary: pred.actual_rain_binary,
        model_name: pred.model || 'XGBoost (Phase 3 Candidate)',
        is_holdout_benchmark: true
      };
    }

    return result;
  }

  /**
   * Deterministic State Aggregates
   * Explicitly labeled as derived statistics
   */
  static getStateAggregates(stateName: string, dateStr?: string) {
    const region = this.getRegionById(stateName);
    if (!region) return null;

    const stateStations = CANONICAL_STATIONS.filter((s) => s.state === stateName);
    const dateToUse = dateStr || this.getDefaultDate();
    const obsForDate = this.getObservationsForDate(dateToUse);

    let tempSum = 0;
    let tempCount = 0;
    let rainSum = 0;
    let rainCount = 0;
    let rainyStations = 0;
    let reportingCount = 0;

    for (const stn of stateStations) {
      const obs = obsForDate[stn.station_id];
      if (obs) {
        reportingCount++;
        if (obs.avg_temp !== null && obs.avg_temp !== undefined) {
          tempSum += obs.avg_temp;
          tempCount++;
        }
        if (obs.rainfall !== null && obs.rainfall !== undefined) {
          rainSum += obs.rainfall;
          rainCount++;
          if (obs.rainfall > 0) {
            rainyStations++;
          }
        }
      }
    }

    return {
      stateName,
      stationCount: stateStations.length,
      reportingStations: reportingCount,
      avgElevation: region.avg_elevation_m,
      avgTemp: tempCount > 0 ? Number((tempSum / tempCount).toFixed(1)) : null,
      avgRainfall: rainCount > 0 ? Number((rainSum / rainCount).toFixed(2)) : null,
      rainyRatio: rainCount > 0 ? Number((rainyStations / rainCount).toFixed(2)) : null
    };
  }

  /**
   * Accurate Equirectangular Projection to SVG coordinates
   */
  static projectCoordinates(
    lat: number,
    lon: number,
    mapWidth = 800,
    mapHeight = 720
  ): { x: number; y: number } {
    const { minLat, maxLat, minLon, maxLon } = INDIA_GEO_BOUNDS;
    const x = ((lon - minLon) / (maxLon - minLon)) * mapWidth;
    const y = ((maxLat - lat) / (maxLat - minLat)) * mapHeight;
    return {
      x: Math.round(x * 10) / 10,
      y: Math.round(y * 10) / 10
    };
  }

  /**
   * Scientific Elevation Hypsometric Scale
   */
  static getElevationCategory(elevationM: number): {
    tier: string;
    label: string;
    color: string;
    fillColor: string;
  } {
    if (elevationM >= 1500) {
      return { tier: 'HIMALAYAN', label: 'High Himalayan (≥1500m)', color: '#c084fc', fillColor: '#9333ea' };
    }
    if (elevationM >= 1000) {
      return { tier: 'SUB_HIMALAYAN', label: 'Sub-Himalayan / Ghats (1000–1499m)', color: '#a855f7', fillColor: '#7e22ce' };
    }
    if (elevationM >= 600) {
      return { tier: 'DECCAN_PLATEAU', label: 'Deccan Plateau (600–999m)', color: '#38bdf8', fillColor: '#0284c7' };
    }
    if (elevationM >= 300) {
      return { tier: 'HIGH_PLAINS', label: 'High Plains (300–599m)', color: '#34d399', fillColor: '#059669' };
    }
    return { tier: 'COASTAL_PLAINS', label: 'Coastal / Low Plains (<300m)', color: '#2dd4bf', fillColor: '#0d9488' };
  }

  /**
   * IMD (India Meteorological Department) Standard Scientific Rainfall Intensity Classification
   * Strict handling: null is preserved as missing, NEVER zero.
   */
  static getIMDRainfallIntensity(rainfallMm: number | null): {
    category: string;
    description: string;
    color: string;
    quality: DataQualityType;
  } {
    if (rainfallMm === null || rainfallMm === undefined) {
      return {
        category: 'MISSING',
        description: 'Observation missing / not reported',
        color: '#64748b', // Slate gray indicator for missing data
        quality: 'MISSING'
      };
    }
    if (rainfallMm === 0) {
      return {
        category: 'NO_RAIN',
        description: 'Dry (0.0 mm)',
        color: '#94a3b8',
        quality: 'OBSERVED'
      };
    }
    if (rainfallMm < 2.5) {
      return {
        category: 'VERY_LIGHT',
        description: 'Very Light Rain (< 2.5 mm)',
        color: '#7dd3fc',
        quality: 'OBSERVED'
      };
    }
    if (rainfallMm <= 7.5) {
      return {
        category: 'LIGHT',
        description: 'Light Rain (2.5 – 7.5 mm)',
        color: '#38bdf8',
        quality: 'OBSERVED'
      };
    }
    if (rainfallMm <= 35.5) {
      return {
        category: 'MODERATE',
        description: 'Moderate Rain (7.6 – 35.5 mm)',
        color: '#0284c7',
        quality: 'OBSERVED'
      };
    }
    if (rainfallMm <= 64.4) {
      return {
        category: 'RATHER_HEAVY',
        description: 'Rather Heavy Rain (35.6 – 64.4 mm)',
        color: '#f59e0b',
        quality: 'OBSERVED'
      };
    }
    if (rainfallMm <= 124.4) {
      return {
        category: 'HEAVY',
        description: 'Heavy Rain (64.5 – 124.4 mm)',
        color: '#ef4444',
        quality: 'OBSERVED'
      };
    }
    return {
      category: 'VERY_HEAVY',
      description: 'Very Heavy / Torrential Rain (≥ 124.5 mm)',
      color: '#dc2626',
      quality: 'OBSERVED'
    };
  }

  /**
   * Scientific Temperature Color Ramp (°C)
   */
  static getTemperatureColor(tempC: number | null): string {
    if (tempC === null || tempC === undefined) return '#64748b'; // Missing data color
    if (tempC < 5) return '#818cf8'; // Cold (Indigo)
    if (tempC < 12) return '#38bdf8'; // Cool (Sky blue)
    if (tempC < 18) return '#2dd4bf'; // Mild (Teal)
    if (tempC < 24) return '#34d399'; // Pleasant (Green)
    if (tempC < 29) return '#facc15'; // Warm (Yellow)
    if (tempC < 34) return '#fb923c'; // Hot (Orange)
    return '#f43f5e'; // Extreme heat (Coral / Rose)
  }

  /**
   * Scientific Forecast Risk Level Evaluation
   */
  static getForecastRiskLevel(rainProb: number, rainMm: number): {
    level: 'LOW' | 'ELEVATED' | 'HIGH' | 'SEVERE';
    label: string;
    color: string;
    scientificBasis: string;
  } {
    if (rainProb >= 0.70 && rainMm >= 35.5) {
      return {
        level: 'SEVERE',
        label: 'Severe Heavy Rain Risk',
        color: '#ef4444',
        scientificBasis: 'Probability ≥ 70% with expected rainfall ≥ 35.5 mm (IMD Rather Heavy+)'
      };
    }
    if (rainProb >= 0.50 && rainMm >= 7.5) {
      return {
        level: 'HIGH',
        label: 'High Rain Potential',
        color: '#f59e0b',
        scientificBasis: 'Probability ≥ 50% with expected rainfall in Moderate range (≥ 7.5 mm)'
      };
    }
    if (rainProb >= 0.35 || rainMm >= 2.5) {
      return {
        level: 'ELEVATED',
        label: 'Elevated Rain Potential',
        color: '#38bdf8',
        scientificBasis: 'Precipitation probability ≥ 35% or measurable accumulation predicted'
      };
    }
    return {
      level: 'LOW',
      label: 'Low Rain Risk',
      color: '#10b981',
      scientificBasis: 'Precipitation probability < 35% with dry conditions expected'
    };
  }
}
