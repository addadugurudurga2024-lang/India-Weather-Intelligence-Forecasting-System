/**
 * Unified Full-Stack API Client for India Weather Forecasting & Intelligence System.
 * Connects frontend services to the FastAPI backend with graceful fallback.
 */

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers || {}),
    },
  });

  if (!res.ok) {
    let errorDetail = res.statusText;
    try {
      const errJson = await res.json();
      errorDetail = errJson.detail || errJson.message || JSON.stringify(errJson);
    } catch {
      // Ignored
    }
    throw new Error(`API Error ${res.status}: ${errorDetail}`);
  }

  return res.json() as Promise<T>;
}

export const apiClient = {
  baseUrl: API_BASE,

  // Health
  async checkHealth() {
    return fetchJson<{ status: string; canonical_stations_count: number }>('/health');
  },

  // Stations
  async getStations(state?: string, district?: string) {
    const params = new URLSearchParams();
    if (state) params.append('state', state);
    if (district) params.append('district', district);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return fetchJson<{ total_stations: number; stations: any[] }>(`/stations${qs}`);
  },

  async getStationHierarchy() {
    return fetchJson<Record<string, Record<string, any[]>>>('/stations/hierarchy');
  },

  async getStationById(stationId: string) {
    return fetchJson<any>(`/stations/${encodeURIComponent(stationId)}`);
  },

  // Historical Analytics
  async getAnalyticsSummary(stationId: string) {
    return fetchJson<any>(`/analytics/summary/${encodeURIComponent(stationId)}`);
  },

  async getAnalyticsTimeseries(stationId: string, limit: number = 365) {
    return fetchJson<any>(`/analytics/timeseries/${encodeURIComponent(stationId)}?limit=${limit}`);
  },

  async getObservations(filters?: { state?: string; district?: string; stationId?: string }, limit: number = 100) {
    const params = new URLSearchParams();
    const st = filters?.state?.trim();
    const dist = filters?.district?.trim();
    const stn = filters?.stationId?.trim();
    if (st && st !== 'ALL' && st.toLowerCase() !== 'undefined' && st.toLowerCase() !== 'null') params.append('state', st);
    if (dist && dist !== 'ALL' && dist.toLowerCase() !== 'undefined' && dist.toLowerCase() !== 'null') params.append('district', dist);
    if (stn && stn !== 'ALL' && stn.toLowerCase() !== 'undefined' && stn.toLowerCase() !== 'null') params.append('station_id', stn);
    params.append('limit', String(limit));
    return fetchJson<{ scope: any; total_records: number; data: any[] }>(`/analytics/observations?${params.toString()}`);
  },

  async getScopedTimeseries(filters?: { state?: string; district?: string; stationId?: string }, limit: number = 365) {
    const params = new URLSearchParams();
    const st = filters?.state?.trim();
    const dist = filters?.district?.trim();
    const stn = filters?.stationId?.trim();
    if (st && st !== 'ALL' && st.toLowerCase() !== 'undefined' && st.toLowerCase() !== 'null') params.append('state', st);
    if (dist && dist !== 'ALL' && dist.toLowerCase() !== 'undefined' && dist.toLowerCase() !== 'null') params.append('district', dist);
    if (stn && stn !== 'ALL' && stn.toLowerCase() !== 'undefined' && stn.toLowerCase() !== 'null') params.append('station_id', stn);
    params.append('limit', String(limit));
    return fetchJson<{ scope: any; total_points: number; data: any[] }>(`/analytics/scoped-timeseries?${params.toString()}`);
  },

  async getStationHistory(stationId: string, limit: number = 30) {
    return fetchJson<{ station_id: string; total_records: number; data: any[] }>(`/analytics/station-history/${encodeURIComponent(stationId)}?limit=${limit}`);
  },

  // Operational Forecast
  async getOperationalTimeline(stationId: string, mode?: string, originDate?: string) {
    const params = new URLSearchParams();
    if (mode) params.append('mode', mode);
    if (originDate) params.append('origin_date', originDate);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return fetchJson<any>(`/forecast/25day-timeline/${encodeURIComponent(stationId)}${qs}`);
  },

  async getMultiHorizonForecast(stationId: string, mode?: string, originDate?: string) {
    const params = new URLSearchParams();
    if (mode) params.append('mode', mode);
    if (originDate) params.append('origin_date', originDate);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return fetchJson<any>(`/forecast/multi-horizon/${encodeURIComponent(stationId)}${qs}`);
  },

  async getCurrentTelemetry(stationId: string, mode?: string, originDate?: string) {
    const params = new URLSearchParams();
    if (mode) params.append('mode', mode);
    if (originDate) params.append('origin_date', originDate);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return fetchJson<any>(`/forecast/current-telemetry/${encodeURIComponent(stationId)}${qs}`);
  },

  // AI Weather Intelligence
  async queryIntelligence(stationId: string, question: string) {
    return fetchJson<any>('/intelligence/query', {
      method: 'POST',
      body: JSON.stringify({ station_id: stationId, question }),
    });
  },

  async getIntelligenceSummary(stationId: string) {
    return fetchJson<any>(`/intelligence/summary/${encodeURIComponent(stationId)}`);
  },

  async getRiskAssessment(stationId: string) {
    return fetchJson<any>(`/intelligence/risk/${encodeURIComponent(stationId)}`);
  },

  // Long-Term Predictor
  async predictLongTerm(stationId: string, targetDate: string) {
    return fetchJson<any>('/long-term-predictor/predict', {
      method: 'POST',
      body: JSON.stringify({ station_id: stationId, target_date: targetDate }),
    });
  },

  async getLongTermClimatology(stationId: string) {
    return fetchJson<any>(`/long-term-predictor/climatology/${encodeURIComponent(stationId)}`);
  },

  // Models Registry
  async getModelRegistry() {
    return fetchJson<any>('/models/registry');
  },
};
