import { stations } from '../data';
import type { Station } from '../types';
import { apiClient } from './apiClient';

export const stationService = {
  async getStations(): Promise<Station[]> {
    try {
      const res = await apiClient.getStations();
      if (res && Array.isArray(res.stations) && res.stations.length > 0) {
        return res.stations;
      }
    } catch {
      // Graceful fallback to authoritative local data bundle
    }
    return Promise.resolve(stations);
  },

  async getStationById(stationId: string): Promise<Station | null> {
    try {
      const res = await apiClient.getStationById(stationId);
      if (res && res.station_id) return res;
    } catch {
      // Fallback
    }
    const station = stations.find((s) => s.station_id === stationId);
    return Promise.resolve(station || null);
  },

  async getStates(): Promise<string[]> {
    const stns = await this.getStations();
    const uniqueStates = Array.from(new Set(stns.map((s) => s.state))).sort();
    return Promise.resolve(uniqueStates);
  },

  async getDistrictsByState(stateCode: string): Promise<string[]> {
    const stns = await this.getStations();
    const stateStations = stateCode === 'ALL' 
      ? stns 
      : stns.filter((s) => s.state.toUpperCase() === stateCode.toUpperCase());
    const districts = Array.from(new Set(stateStations.map((s) => s.district))).sort();
    return Promise.resolve(districts);
  }
};
