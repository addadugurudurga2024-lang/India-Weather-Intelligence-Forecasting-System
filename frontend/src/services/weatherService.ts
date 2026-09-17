import type { WeatherObservation, FilterState } from '../types';
import { apiClient } from './apiClient';

export const weatherService = {
  async getObservations(filters?: Partial<FilterState>, limit: number = 100): Promise<WeatherObservation[]> {
    try {
      const res = await apiClient.getObservations({
        state: filters?.state,
        district: filters?.district,
        stationId: filters?.stationId
      }, limit);
      if (res && Array.isArray(res.data) && res.data.length > 0) {
        let records = res.data as WeatherObservation[];
        if (filters?.rainfallFilter === 'RAINY_ONLY') {
          records = records.filter((o) => o.rainfall !== null && o.rainfall > 0);
        } else if (filters?.rainfallFilter === 'DRY_ONLY') {
          records = records.filter((o) => o.rainfall === 0);
        }
        return records;
      }
    } catch {
      // If API call fails or backend is unreachable, do not fabricate 10-station mock data
      // Return empty array so UI shows explicit DATA UNAVAILABLE rather than misleading mock records
      return Promise.resolve([]);
    }

    return Promise.resolve([]);
  },

  async getScopedTimeseries(filters?: Partial<FilterState>, limit: number = 365): Promise<WeatherObservation[]> {
    try {
      const res = await apiClient.getScopedTimeseries({
        state: filters?.state,
        district: filters?.district,
        stationId: filters?.stationId
      }, limit);
      if (res && Array.isArray(res.data) && res.data.length > 0) {
        return res.data as WeatherObservation[];
      }
    } catch {
      // Fallback
    }
    return this.getObservations(filters, limit);
  },

  async getLatestObservation(stationId?: string): Promise<WeatherObservation | null> {
    if (stationId) {
      try {
        const hist = await this.getStationHistory(stationId, 1);
        if (hist.length > 0) return hist[0];
      } catch {
        // Fallback below
      }
    }
    return Promise.resolve(null);
  },

  async getStationHistory(stationId: string, limitDays = 30): Promise<WeatherObservation[]> {
    try {
      const res = await apiClient.getStationHistory(stationId, limitDays);
      if (res && Array.isArray(res.data) && res.data.length > 0) {
        return res.data as WeatherObservation[];
      }
    } catch {
      // Fallback: return empty array rather than obsolete 10-station mock data
      return Promise.resolve([]);
    }

    return Promise.resolve([]);
  }
};
