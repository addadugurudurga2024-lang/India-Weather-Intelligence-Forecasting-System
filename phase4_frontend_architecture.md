# Phase 4 — Frontend Architecture Specification

## India Weather Forecasting & Intelligence System

---

### 1. Executive Summary

Phase 4 establishes the frontend application layer for the India Weather Forecasting & Intelligence System. Built with **React 19**, **TypeScript 6**, and **Vite 8**, the frontend provides a production-grade, highly responsive, and accessible user experience across desktop, tablet, and mobile devices.

The architecture enforces a strict boundary: the frontend is decoupled from direct database access and future backend implementation through a typed **API Service Abstraction Layer**. All visualization components consume authoritative data derived directly from Phase 2 canonical datasets and Phase 3 model training artifacts.

---

### 2. Directory & Module Hierarchy

```text
frontend/
├── index.html                    # HTML5 shell with responsive viewport & meta tags
├── vite.config.ts                # Vite build and dev server configuration
├── tsconfig.json                 # TypeScript project configuration (strict mode enabled)
├── package.json                  # React 19, react-router-dom v7, lucide-react
├── public/                       # Static public assets
└── src/
    ├── types/
    │   └── index.ts              # Canonical domain interfaces (Station, Observation, Metric, etc.)
    ├── styles/
    │   ├── tokens.css            # CSS custom properties (color palette, spacing, typography, elevation)
    │   ├── base.css              # Global resets, typography rules, responsive layout foundation
    │   └── components.css        # Reusable component classes, cards, badges, inputs, buttons
    ├── context/
    │   ├── ThemeContext.tsx      # Dark / Light theme state machine with localStorage persistence
    │   └── FilterContext.tsx     # Global filter state (State, District, Station, Date Range, Season)
    ├── data/
    │   ├── authoritativeStations.json # 413 physical stations from Phase 2 station metadata
    │   ├── authoritativeMetrics.json  # Exact Phase 3 cross-validation and holdout metrics
    │   ├── authoritativeModelRegistry.json # Phase 3 model registry metadata
    │   ├── mockWeather.ts        # Centralized deterministic historical observations
    │   ├── mockForecasts.ts      # Centralized deterministic multi-model forecast outputs
    │   └── index.ts              # Unified data exporter
    ├── services/
    │   ├── stationService.ts     # Station directory and geographic hierarchy services
    │   ├── weatherService.ts     # Historical weather telemetry and time-series services
    │   ├── forecastService.ts    # Multi-model forecast queries and comparison services
    │   ├── modelService.ts       # Model registry, holdout evaluations, and residual services
    │   ├── analyticsService.ts   # Aggregate KPIs and spatial-temporal summaries
    │   └── index.ts              # Service hub
    ├── components/
    │   ├── layout/
    │   │   ├── AppShell.tsx      # Core responsive application wrapper
    │   │   ├── Header.tsx        # Top navigation, global search trigger, theme toggle, mobile drawer
    │   │   ├── Sidebar.tsx       # Primary navigation bar with route status and badges
    │   │   └── GlobalSearchModal.tsx # Cmd+K / Ctrl+K keyboard-accessible search modal
    │   ├── filters/
    │   │   └── GlobalFilterBar.tsx # Cascading dropdowns (State -> District -> Station -> Date Range)
    │   ├── common/
    │   │   ├── MetricCard.tsx    # High-impact KPI display cards with trend indicators
    │   │   ├── PreviewBanner.tsx # Standardized visual banner for development/preview states
    │   │   └── LoadingState.tsx  # Skeletons, spinners, empty states, and error boundary fallback
    │   ├── charts/
    │   │   ├── TemperatureTrendChart.tsx # SVG daily line & min/max shaded envelope chart
    │   │   ├── RainfallBarChart.tsx      # SVG hyetograph with rainy-day threshold indicators
    │   │   ├── ModelComparisonBarChart.tsx # Multi-model comparative bar chart across metrics
    │   │   ├── ConfusionMatrixChart.tsx  # Rain classification contingency matrix
    │   │   └── ROCCurveChart.tsx         # ROC discrimination curve with AUC display
    │   ├── maps/
    │   │   └── IndiaStationMap.tsx       # Interactive 413-station geographic map with zoom/pan
    │   ├── tables/
    │   │   └── DataExplorerTable.tsx     # Paginated, sortable, searchable table with row expansion
    │   └── weather/
    │       └── WeatherIntelligenceWidgets.tsx # Rain risk, alerts, and model explainability cards
    ├── pages/
    │   ├── DashboardPage.tsx     # Executive command center with live telemetry and KPIs
    │   ├── AnalyticsPage.tsx     # Deep temperature time-series and anomaly analytics
    │   ├── RainfallPage.tsx      # Hyetograph, monthly patterns, and rainy-day distribution
    │   ├── ForecastPage.tsx      # Multi-model forward forecast comparisons
    │   ├── StationsPage.tsx      # 413-station directory, physical telemetry, and sensor history
    │   ├── MapPage.tsx           # Full-screen geographic station mapping with elevation styling
    │   ├── ModelsPage.tsx        # Scientific benchmark comparing XGBoost, LSTM, and Persistence
    │   ├── DataPage.tsx          # Data explorer with dynamic filters and CSV export
    │   └── MethodologyPage.tsx   # Mathematical formulations, audit trail, and validation methodology
    ├── App.tsx                   # Client-side router configuration (React Router v7)
    └── main.tsx                  # Application bootstrap
```

---

### 3. Client-Side Routing Architecture

The application implements client-side routing via `react-router-dom` v7 with 10 dedicated routes:

| Route | View Component | Key Capabilities |
| :--- | :--- | :--- |
| `/` | `DashboardPage` | Redirects / default view: Overview KPI cards, telemetry sparklines, active station context. |
| `/dashboard` | `DashboardPage` | National overview, latest observations, temperature trend, rainfall volume, active station status. |
| `/analytics` | `AnalyticsPage` | Historical temperature curves, min/max diurnal spreads, anomaly bands, seasonal distributions. |
| `/forecast` | `ForecastPage` | 2025 holdout predictions, multi-model consensus, rain probabilities, temperature forecast. |
| `/rainfall` | `RainfallPage` | Rainfall distribution, rainy-day threshold compliance, monthly hyetographs, null preservation. |
| `/stations` | `StationsPage` | 413 canonical physical stations, lat/lon/elevation, observation completeness, operational dates. |
| `/map` | `MapPage` | Geographic station layout, interactive tooltip telemetry, elevation heat mapping, zoom/pan. |
| `/models` | `ModelsPage` | Authoritative Phase 3 benchmark: MAE, RMSE, R², Accuracy, ROC-AUC across validation & holdout. |
| `/data` | `DataPage` | Paginated data grid, search, column sorting, expanded row telemetry, missing data flags. |
| `/methodology` | `MethodologyPage` | Documentation of Phase 1 audit, Phase 2 data cleaning, Phase 3 cross-validation, and metrics. |

---

### 4. API Service Abstraction & Future FastAPI Integration

Components never make ad-hoc fetch requests or inspect raw data files directly. Instead, all views depend strictly on the **Service Layer** (`src/services/`):

```text
React View Component
       │
       ▼
Service Method (e.g. weatherService.getObservations(filters))
       │
       ├── Phase 4: Resolves via centralized typed data in src/data/
       │
       └── Phase 8: Drops in fetch(`${API_BASE}/observations?station_id=...`) without changing UI
```

Every service method returns a typed `Promise<T>`. When Phase 8 introduces the production FastAPI endpoints, the service implementations will swap their internal mock data resolution with HTTP fetch calls to `http://localhost:8000/api/v1/` without requiring any changes to React page components.

---

### 5. State Management & Cascading Global Filters

State management follows a clean, decoupled architecture:
1. **`ThemeContext`**:
   - Manages `'dark'`, `'light'`, and `'system'` themes.
   - Automatically synchronizes with `localStorage` and `prefers-color-scheme`.
   - Modifies the root `data-theme` attribute on `<html>` to toggle CSS variables.
2. **`FilterContext`**:
   - Maintains the global filtering state: `state`, `district`, `stationId`, `dateRange`, `season`, `weatherVariable`.
   - Supports cascading logic: selecting a State automatically restricts available Districts; selecting a District automatically restricts Stations.
   - Preserves `'ALL'` selection to enable nationwide aggregations.
3. **`GlobalSearchModal`**:
   - Provides global keyboard shortcuts (`Cmd+K` or `Ctrl+K`) and an accessible modal.
   - Searches across all 413 stations, 32 states, and districts with immediate route and filter activation.

---

### 6. Component Modularity & Design Principles

- **Pure SVG Visualizations**: All charts (`TemperatureTrendChart`, `RainfallBarChart`, `ModelComparisonBarChart`, `ConfusionMatrixChart`, `ROCCurveChart`) are engineered as lightweight, high-performance SVG components with zero external charting library bloat, ensuring instant rendering and complete theme reactivity.
- **Micro-Animations & Transitions**: CSS custom variables define restrained transition timings (`--transition-fast: 150ms`, `--transition-normal: 250ms`).
- **Null Safety**: Observations with missing rainfall render explicit visual indicators ("Missing / Unrecorded") rather than zero, maintaining strict fidelity to Phase 1 data audit findings.
