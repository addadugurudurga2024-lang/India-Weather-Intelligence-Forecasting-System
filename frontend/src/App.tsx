import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { FilterProvider } from './context/FilterContext';
import { AppShell } from './components/layout/AppShell';

import { DashboardPage } from './pages/DashboardPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { RainfallPage } from './pages/RainfallPage';
import { ForecastPage } from './pages/ForecastPage';
import { StationsPage } from './pages/StationsPage';
import { MapPage } from './pages/MapPage';
import { ModelsPage } from './pages/ModelsPage';
import { DataPage } from './pages/DataPage';
import { MethodologyPage } from './pages/MethodologyPage';
import { LongTermPredictorPage } from './pages/LongTermPredictorPage';

export const App: React.FC = () => {
  return (
    <ThemeProvider>
      <FilterProvider>
        <BrowserRouter>
          <Routes>
            <Route element={<AppShell />}>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/rainfall" element={<RainfallPage />} />
              <Route path="/forecast" element={<ForecastPage />} />
              <Route path="/long-term-predictor" element={<LongTermPredictorPage />} />
              <Route path="/stations" element={<StationsPage />} />
              <Route path="/map" element={<MapPage />} />
              <Route path="/models" element={<ModelsPage />} />
              <Route path="/data" element={<DataPage />} />
              <Route path="/methodology" element={<MethodologyPage />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </FilterProvider>
    </ThemeProvider>
  );
};

export default App;
