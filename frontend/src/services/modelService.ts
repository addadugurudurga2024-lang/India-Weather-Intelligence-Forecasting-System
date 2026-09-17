import { metricsSummary, modelRegistry } from '../data';
import type { MetricsSummary, ModelRegistry } from '../types';

export const modelService = {
  async getMetricsSummary(): Promise<MetricsSummary> {
    return Promise.resolve(metricsSummary);
  },

  async getModelRegistry(): Promise<ModelRegistry> {
    return Promise.resolve(modelRegistry);
  }
};
