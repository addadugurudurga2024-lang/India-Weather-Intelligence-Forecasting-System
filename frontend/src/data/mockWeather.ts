import type { WeatherObservation } from '../types';
import stationsData from './authoritativeStations.json';

// Generate representative deterministic historical observations for key hub stations
// across India's distinct agro-climatic zones
function generateStationHistory(stationId: string, baseTemp: number, annualVariance: number, monsoonIntensity: number): WeatherObservation[] {
  const observations: WeatherObservation[] = [];
  const station = stationsData.find((s) => s.station_id === stationId);
  const stationName = station?.station_name || stationId;
  const state = station?.state || 'IN';
  const district = station?.district || 'District';

  // Generate 60 recent days up to 2025-02-10
  const endDate = new Date('2025-02-10T00:00:00Z');
  
  for (let i = 59; i >= 0; i--) {
    const d = new Date(endDate);
    d.setUTCDate(d.getUTCDate() - i);
    const dateStr = d.toISOString().split('T')[0];
    
    // Deterministic pseudo-randomness based on date and station
    const dayOfYear = Math.floor((d.getTime() - new Date('2025-01-01').getTime()) / (1000 * 60 * 60 * 24)) + 31;
    const seed = (stationId.length * 37 + i * 19) % 100;
    const noise = (seed - 50) / 50; // -1 to 1

    // Winter seasonal curve in Jan-Feb
    const tempOffset = Math.sin((dayOfYear / 365) * 2 * Math.PI - Math.PI / 2) * annualVariance;
    const avgTemp = Math.round((baseTemp + tempOffset + noise * 1.8) * 10) / 10;
    const minTemp = Math.round((avgTemp - 4.5 - Math.abs(noise)) * 10) / 10;
    const maxTemp = Math.round((avgTemp + 5.2 + Math.abs(noise)) * 10) / 10;

    // Winter precipitation in India (mostly 0 except occasional western disturbances)
    let rainfall: number | null = 0.0;
    if ((stationId.includes('shimla') || stationId.includes('delhi')) && (i === 12 || i === 28)) {
      rainfall = Math.round((8.5 + noise * 4) * 10) / 10;
    } else if (stationId.includes('port_blair') && i % 7 === 0) {
      rainfall = Math.round((14.2 + noise * 6) * 10) / 10;
    } else if (i === 44 && noise > 0.4) {
      rainfall = Math.round((3.2 * monsoonIntensity) * 10) / 10;
    }

    const windSpeed = Math.round((7.5 + noise * 3.5) * 10) / 10;
    const airPressure = Math.round((1014.2 - (station?.elevation_m || 100) * 0.11 + noise * 2) * 10) / 10;

    observations.push({
      station_id: stationId,
      station_name: stationName,
      state,
      district,
      date_of_record: dateStr,
      avg_temp: avgTemp,
      min_temp: minTemp,
      max_temp: maxTemp,
      rainfall: rainfall,
      wind_speed: windSpeed,
      air_pressure: airPressure,
      is_rainy: rainfall !== null && rainfall > 0
    });
  }

  return observations;
}

export const mockWeatherObservations: WeatherObservation[] = [
  ...generateStationHistory('new_delhi_safdarjung_28.5833_77.2000_216m', 15.5, 14, 1.0),
  ...generateStationHistory('mumbai_santacruz_19.1167_72.8500_14m', 25.8, 5, 2.5),
  ...generateStationHistory('bengaluru_12.9667_77.5833_921m', 22.1, 4, 1.2),
  ...generateStationHistory('kolkata_alipore_22.5333_88.3333_6m', 21.4, 9, 1.8),
  ...generateStationHistory('chennai_meenambakkam_13.0000_80.1833_16m', 26.2, 5, 1.5),
  ...generateStationHistory('jaipur_sanganer_26.8167_75.8000_390m', 17.2, 13, 0.8),
  ...generateStationHistory('shimla_31.1000_77.1667_2205m', 7.5, 11, 1.4),
  ...generateStationHistory('shillong_25.5667_91.8833_1500m', 11.2, 8, 2.2),
  ...generateStationHistory('agartala_23.8833_91.2500_15m', 19.8, 8, 1.6),
  ...generateStationHistory('port_blair_11.6667_92.7167_79m', 27.5, 3, 2.0)
];
