import authoritativeStations from './authoritativeStations.json';
import authoritativeMetrics from './authoritativeMetrics.json';
import authoritativeModelRegistry from './authoritativeModelRegistry.json';
import authoritative25DayTimeline from './authoritative25DayTimeline.json';
import authoritativeMultiHorizonSummary from './authoritativeMultiHorizonSummary.json';
import { mockWeatherObservations } from './mockWeather';
import { mockForecastResults } from './mockForecasts';
import type { Station, MetricsSummary, ModelRegistry, MultiHorizonSummary } from '../types';

export const stations: Station[] = authoritativeStations as Station[];
export const metricsSummary: MetricsSummary = authoritativeMetrics as MetricsSummary;
export const modelRegistry: ModelRegistry = authoritativeModelRegistry as ModelRegistry;
export const multiHorizonSummary: MultiHorizonSummary = authoritativeMultiHorizonSummary as MultiHorizonSummary;
export const timelines25DayPayload = authoritative25DayTimeline;

export { mockWeatherObservations, mockForecastResults, authoritative25DayTimeline, authoritativeMultiHorizonSummary };

