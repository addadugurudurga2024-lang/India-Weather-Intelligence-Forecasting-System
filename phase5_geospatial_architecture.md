# Phase 5 — Geospatial & Visualization Architecture

## System Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                            PHASE 5 GEOSPATIAL ENGINE                              |
+-----------------------------------------------------------------------------------+
                                          |
          +-------------------------------+-------------------------------+
          |                               |                               |
+---------------------+         +---------------------+         +---------------------+
| Phase 2 Parquet     |         | Phase 3 Predictions |         | Station Registry    |
| canonical_weather_  |         | xgb_temp / rain /   |         | authoritativeStations|
| forecasting.parquet |         | cls_preds_holdout   |         | .json (413 stns)    |
+---------------------+         +---------------------+         +---------------------+
          |                               |                               |
          +-------------------------------+-------------------------------+
                                          |
                                          v
                    [extract_geospatial_authoritative_data.py]
                                          |
                    +---------------------+---------------------+
                    |                                           |
                    v                                           v
     [authoritativeObservationsSnapshot.json]    [authoritativeForecastSnapshots.json]
     (16,732 records, 41 dates in 2025)          (16,322 holdout preds, 40 dates)
                    |                                           |
                    +---------------------+---------------------+
                                          |
                                          v
                              [GeographicService.ts]
               - projectCoordinates(lat, lon, w, h)
               - getIMDRainfallIntensity(mm)
               - getElevationCategory(m)
               - getTemperatureColor(temp)
               - getForecastRiskLevel(prob, mm)
               - getStateAggregates(state, date)
                                          |
                                          v
                              [IndiaMapCanvas.tsx]
       +----------------------------------+----------------------------------+
       |                                  |                                  |
       v                                  v                                  v
 [LayerControl.tsx]              [TimeControl.tsx]                  [MapLegend.tsx]
 (6 thematic layers)             (Play/Pause & scrub)               (Scientific ramps)
       |                                  |                                  |
       v                                  v                                  v
 [StationMarkerLayer.tsx]        [StateOverlayLayer.tsx]            [MapTooltip.tsx]
 (413 SVG beacons)               (Regional choropleth)              (Contextual HUD)
                                          |
                                          v
                          [GeographicComparisonModal.tsx]
                          (Side-by-side 3-station telemetry)
```

## Component Responsibility Matrix

| Component | File Path | Architectural Role | Performance Guarantee |
| :--- | :--- | :--- | :--- |
| `GeographicService` | `services/geographicService.ts` | Central adapter for stations, observations, forecasts, projection math | O(1) keyed lookups; zero duplicate transforms |
| `IndiaMapCanvas` | `components/maps/IndiaMapCanvas.tsx` | Master SVG viewport, pan/zoom engine, keyboard listener | Hardware accelerated CSS transforms |
| `StationMarkerLayer` | `components/maps/StationMarkerLayer.tsx` | Pure SVG rendering for 413 stations with layer styling | Dynamic radius scaling, memoized geometry |
| `StateOverlayLayer` | `components/maps/StateOverlayLayer.tsx` | State boundaries & station density choropleth | Path memoization, derived aggregate labeling |
| `LayerControl` | `components/maps/LayerControl.tsx` | Accessible layer & metric switcher HUD | Accessible ARIA buttons & active pills |
| `TimeControl` | `components/maps/TimeControl.tsx` | Date stepper, scrub slider, play/pause animation | `setInterval` cleanup, zero memory leaks |
| `MapLegend` | `components/maps/MapLegend.tsx` | Categorical & continuous scientific legends | Distinct missing-data indicators |
| `MapTooltip` | `components/maps/MapTooltip.tsx` | Hover telemetry card with lat/lon, altitude, metrics | Debounced cursor tracking, non-blocking DOM |
| `GeographicComparisonModal` | `components/maps/GeographicComparisonModal.tsx` | Multi-station side-by-side analytical comparator | Scoped modal portal, responsive grid |

## Projection Formula & Geographic Bounds
The coordinate transformation translates latitude ($\phi$) and longitude ($\lambda$) into two-dimensional canvas coordinates $(x, y)$ via an Equirectangular mapping:

$$x = \frac{\lambda - \lambda_{\min}}{\lambda_{\max} - \lambda_{\min}} \times W$$

$$y = \frac{\phi_{\max} - \phi}{\phi_{\max} - \phi_{\min}} \times H$$

Where:
- $\phi_{\min} = 6.5^\circ\text{N}$, $\phi_{\max} = 37.5^\circ\text{N}$
- $\lambda_{\min} = 68.0^\circ\text{E}$, $\lambda_{\max} = 97.5^\circ\text{E}$
- $W = 800\text{ px}$, $H = 720\text{ px}$
