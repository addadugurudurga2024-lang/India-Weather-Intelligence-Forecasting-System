import type { ForecastResult } from '../types';
import stationsData from './authoritativeStations.json';

export const mockForecastResults: ForecastResult[] = stationsData.map((station) => {
  const id = station.station_id;
  const elev = station.elevation_m || 100;
  const lat = station.latitude || 20;

  // Mathematically grounded baseline temperatures by latitude and standard atmospheric lapse rate (6.5°C / 1000m)
  let baseTemp = 27.0 - (lat - 10) * 0.4 - (elev / 1000.0) * 6.5;
  baseTemp = Math.round(Math.max(2.0, Math.min(38.0, baseTemp)) * 10) / 10;

  // Rain occurrence estimation by geographical regime
  let prob = 0.05;
  if (lat > 23 && station.longitude > 88) prob = 0.18; // Northeast
  else if (elev > 1500) prob = 0.22; // High altitude / Himalayan
  else if (lat < 15) prob = 0.10; // Peninsular / Coastal
  else if (lat > 25 && station.longitude < 75) prob = 0.03; // Arid Northwest

  const predRainAmt = prob >= 0.20 ? Math.round(prob * 14.5 * 10) / 10 : 0.0;

  return {
    station_id: id,
    station_name: station.station_name,
    state: station.state,
    district: station.district,
    forecast_date: '2025-02-11',
    predicted_temp: baseTemp,
    predicted_rainfall_amount: predRainAmt,
    predicted_rain_probability: prob,
    predicted_rain_binary: prob >= 0.30,
    model_temperature: 'xgb_temp_fold2_v1',
    model_rainfall: 'xgb_rain_amt_fold2_v1 (log1p)',
    model_classification: 'xgb_rain_cls_fold2_v1',
    generated_at: '2025-02-10T23:59:59Z',
    is_preview: true
  };
});
