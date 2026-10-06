import { mockForecastResults, authoritative25DayTimeline, authoritativeMultiHorizonSummary, stations } from '../data';
import type { ForecastResult, Operational25DayTimeline, MultiHorizonSummary, Station } from '../types';
import { apiClient } from './apiClient';

function getTodayDateStr(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function computeOffsetDateStr(baseDateStr: string, offsetDays: number): string {
  const d = new Date(baseDateStr + 'T00:00:00');
  d.setDate(d.getDate() + offsetDays);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

export const forecastService = {
  async getAllForecasts(): Promise<ForecastResult[]> {
    return Promise.resolve(mockForecastResults);
  },

  async getForecastByStation(stationId: string): Promise<ForecastResult | null> {
    const forecast = mockForecastResults.find((f) => f.station_id === stationId);
    return Promise.resolve(forecast || null);
  },

  async get25DayTimeline(
    stationId: string,
    mode: 'historical_holdout_replay' | 'operational_current' = 'historical_holdout_replay'
  ): Promise<Operational25DayTimeline | null> {
    // 1. Attempt live backend call
    try {
      const apiRes = await apiClient.getOperationalTimeline(stationId, mode);
      if (apiRes && Array.isArray(apiRes.timeline) && apiRes.timeline.length > 0) {
        return {
          station_id: apiRes.station_id,
          station_name: apiRes.station_name,
          district: apiRes.district,
          state: apiRes.state,
          latitude: apiRes.latitude || 20.0,
          longitude: apiRes.longitude || 78.0,
          elevation_m: apiRes.elevation_m || 100.0,
          forecast_origin: apiRes.forecast_origin,
          timeline: apiRes.timeline.map((d: any) => ({
            relative_day: d.day_offset,
            date: d.date,
            status: d.status || (d.day_offset === 0 ? (d.provenance === 'CURRENT' ? 'CURRENT' : 'UNAVAILABLE') : d.day_offset < 0 ? (d.provenance === 'OBSERVED' ? 'OBSERVED' : 'MODEL ESTIMATE') : 'FORECAST'),
            is_observed: typeof d.is_observed === 'boolean' ? d.is_observed : (d.provenance === 'OBSERVED' || d.provenance === 'CURRENT'),
            temperature_avg: d.temp_avg_c,
            temperature_min: d.temp_min_c,
            temperature_max: d.temp_max_c,
            rainfall_amount: d.rainfall_mm,
            rain_probability: d.rain_probability,
            wind_speed: d.wind_kmh,
            air_pressure: d.pressure_hpa,
            provenance: d.provenance,
            uncertainty: d.uncertainty || null,
            model_metadata: d.model_metadata || null,
          })),
        } as Operational25DayTimeline;
      }
    } catch {
      // Fallback to static authoritative data bundle
    }

    // 2. Fallback to local authoritative bundle
    const stationsObj = (authoritative25DayTimeline as any).stations || {};
    const stationData = stationsObj[stationId];
    const isCurrentMode = mode === 'operational_current';
    const effectiveOrigin = isCurrentMode ? getTodayDateStr() : '2025-01-20';

    if (!stationData) {
      // Dynamic fallback for any canonical station not precomputed in static seed
      const targetStation: Station | undefined = stations.find((s) => s.station_id === stationId);
      const defaultId = (authoritative25DayTimeline as any).metadata?.default_station_id || 'new_delhi_safdarjung_28.5833_77.2000_211m';
      const defaultData = stationsObj[defaultId] || Object.values(stationsObj)[0];
      if (!defaultData) return Promise.resolve(null);

      const baseTimeline: Operational25DayTimeline = (defaultData as any)[mode] || (defaultData as any)['historical_holdout_replay'];
      if (!targetStation || !baseTimeline) return Promise.resolve(baseTimeline || null);

      const elevDiff = (targetStation.elevation_m - (baseTimeline.elevation_m || 216)) / 1000.0;
      const lapseDelta = Math.round(elevDiff * 6.5 * 10) / 10;

      const adaptedTimeline: Operational25DayTimeline = {
        ...baseTimeline,
        station_id: targetStation.station_id,
        station_name: targetStation.station_name,
        district: targetStation.district,
        state: targetStation.state,
        latitude: targetStation.latitude,
        longitude: targetStation.longitude,
        elevation_m: targetStation.elevation_m,
        forecast_origin: effectiveOrigin,
        timeline: baseTimeline.timeline.map((day) => {
          const newDate = computeOffsetDateStr(effectiveOrigin, day.relative_day);
          if (isCurrentMode && day.relative_day === 0) {
            return {
              ...day,
              date: newDate,
              status: 'UNAVAILABLE',
              is_observed: false,
              provenance: 'UNAVAILABLE',
              temperature_avg: null,
              temperature_min: null,
              temperature_max: null,
              rainfall_amount: null,
              wind_speed: null,
              air_pressure: null,
            };
          }
          if (day.temperature_avg === null) return { ...day, date: newDate };
          const adjAvg = Math.round((day.temperature_avg - lapseDelta) * 10) / 10;
          const adjMin = day.temperature_min !== null ? Math.round((day.temperature_min - lapseDelta) * 10) / 10 : null;
          const adjMax = day.temperature_max !== null ? Math.round((day.temperature_max - lapseDelta) * 10) / 10 : null;
          return {
            ...day,
            date: newDate,
            temperature_avg: adjAvg,
            temperature_min: adjMin,
            temperature_max: adjMax,
          };
        })
      };
      return Promise.resolve(adaptedTimeline);
    }

    const rawTimeline = stationData[mode] || stationData['historical_holdout_replay'];
    if (!rawTimeline) return Promise.resolve(null);

    const timeline: Operational25DayTimeline = {
      ...rawTimeline,
      forecast_origin: effectiveOrigin,
      timeline: rawTimeline.timeline.map((day: any) => {
        const newDate = computeOffsetDateStr(effectiveOrigin, day.relative_day);
        if (isCurrentMode && day.relative_day === 0) {
          return {
            ...day,
            date: newDate,
            status: 'UNAVAILABLE',
            is_observed: false,
            provenance: 'UNAVAILABLE',
            temperature_avg: null,
            temperature_min: null,
            temperature_max: null,
            rainfall_amount: null,
            wind_speed: null,
            air_pressure: null,
          };
        }
        return {
          ...day,
          date: newDate,
        };
      })
    };
    return Promise.resolve(timeline);
  },


  async getMultiHorizonSummary(): Promise<MultiHorizonSummary> {
    return Promise.resolve(authoritativeMultiHorizonSummary as MultiHorizonSummary);
  },

  async getHorizonDiagnostics(stationId: string, mode?: string, originDate?: string): Promise<any> {
    return apiClient.getHorizonDiagnostics(stationId, mode, originDate);
  },
};
