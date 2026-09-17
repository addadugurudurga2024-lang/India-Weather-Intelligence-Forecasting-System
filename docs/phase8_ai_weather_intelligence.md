# Phase 8 — AI Weather Intelligence: Technical Reference & Architecture Manual

**Project:** India Weather Forecasting & Intelligence System  
**Phase:** Phase 8 — AI Weather Intelligence  
**Status:** COMPLETED & VERIFIED  
**Audience:** Production Engineering, Meteorological Data Science, Future Phase 9 Backend Teams  

---

## 1. Architectural Overview

The AI Weather Intelligence layer is a deterministic, fact-grounded reasoning pipeline built directly atop the Phase 1–7 foundational assets. It replaces unconstrained generative text generation with an auditable, six-stage pipeline:

```
Authoritative Timeline Input (D-12..D-1 Historical, D0 Telemetry, T+1..T+12 Forecasts)
                                    ↓
                       Context Builder & Validator
                                    ↓
                        Data Availability Evaluator
                  (AVAILABLE | PARTIAL | UNAVAILABLE)
                                    ↓
                       Structured Reasoning Engines
      - TemperatureIntelligenceEngine (trends, diurnal range, interval widening)
      - RainfallIntelligenceEngine (occurrence prob vs predicted volume, wet spells)
      - PrecipitationRiskEngine (calibrated LOW/MODERATE/HIGH risk classification)
      - MultiHorizonIntelligenceEngine (near, mid, extended tranche synthesis)
      - TimelineInterpreter (temporal boundary & provenance preservation)
      - AnomalyIntelligenceEngine (2-sigma climatological departure checks)
      - ForecastChangeDetector (day-over-day derivatives & probability shifts)
                                    ↓
              Scientific Explainability & Controlled Confidence
        - ModelExplanationEngine (Phase 6 TreeSHAP attribution & model limitations)
        - ConfidenceLanguageEngine (strict prohibition of certainty terms)
        - RecommendationSafeEngine (conservative operational cautions)
                                    ↓
               Natural-Language Generation (NLG) Renderer
           (Controlled Markdown & Text Assembly from Fact Graph)
                                    ↓
                   Grounding Validator & Security Gate
         (Verifies exact numbers, bounds, units, stations, and vocabulary)
                                    ↓
                     Grounded Intelligence Output
```

---

## 2. Core Operational Modules & Packages

All Phase 8 code is organized cleanly within `phase8_intelligence/`:

| Module Path | Primary Responsibility |
| :--- | :--- |
| `phase8_intelligence/core/contracts.py` | Strict Pydantic v2 data contracts for timeline days, prediction intervals, and station metadata. |
| `phase8_intelligence/core/schemas.py` | Structured output schemas defining exact JSON schemas for intelligence objects. |
| `phase8_intelligence/core/availability.py` | Rigorous tri-state availability logic (`AVAILABLE`, `PARTIAL`, `UNAVAILABLE`) preventing missing-data imputation. |
| `phase8_intelligence/core/context_builder.py` | Ingestion parser converting Phase 7 operational timelines into validated context objects. |
| `phase8_intelligence/core/temperature_intel.py` | Computes warming/cooling trajectories, expected ranges, diurnal spreads, and interval expansions. |
| `phase8_intelligence/core/rainfall_intel.py` | Analyzes $P(\text{rain} > 0)$, conditional amounts, peak probability horizons, and spell dynamics. |
| `phase8_intelligence/core/risk_engine.py` | Maps model outputs to deterministic risk levels (`LOW`, `MODERATE`, `HIGH`) using IMD thresholds. |
| `phase8_intelligence/core/multi_horizon_intel.py` | Decomposes forecasts into Near-Term (T+1..T+3), Medium-Range (T+4..T+7), and Extended (T+8..T+12). |
| `phase8_intelligence/core/timeline_interpreter.py` | Enforces the 25-day temporal partition: D-12..D-1 (Actual), D0 (Current), D+1..D+12 (Forecast). |
| `phase8_intelligence/core/historical_context.py` | Provides IMD 4-season baselines and monthly climatological benchmarks. |
| `phase8_intelligence/core/anomaly_detector.py` | Detects statistical departures exceeding $\pm 2.0\sigma$ from historical monthly baselines. |
| `phase8_intelligence/core/change_detector.py` | Computes daily step-change derivatives and flags abrupt temperature/rain shifts. |
| `phase8_intelligence/core/model_explanations.py` | Presents Phase 6 TreeSHAP attributions with strict non-causal language. |
| `phase8_intelligence/core/confidence_language.py` | Generates controlled uncertainty statements and audits text against forbidden terms. |
| `phase8_intelligence/core/summary_generator.py` | Produces 7 standard structured summaries (Current, T+1, 3-Day, 12-Day, Rain, Temp, Uncertainty). |
| `phase8_intelligence/core/comparison_engine.py` | Provides controlled comparisons: Station vs Station, Today vs History, and External Benchmarks. |
| `phase8_intelligence/core/recommendation_safe.py` | Emits conservative, evidence-based planning cautions without high-stakes advice. |
| `phase8_intelligence/core/nlg_renderer.py` | Controlled template-and-fact-bound markdown generator. |
| `phase8_intelligence/core/qa_interface.py` | Q&A router handling 7 supported intents and providing safe refusal for unsupported topics. |
| `phase8_intelligence/core/grounding_validator.py` | Pre-flight audit gate validating factual compliance before output release. |
| `phase8_intelligence/core/engine.py` | Master orchestrator unifying the pipeline. |
| `phase8_intelligence/fixtures/test_fixtures.py` | 10 synthetic meteorological fixtures for end-to-end quality and boundary testing. |

---

## 3. Strict Grounding & Anti-Hallucination Invariants

### 3.1 Zero Data Fabrication Rule
- If current telemetry (D0) is missing, status is set to `UNAVAILABLE`, temperatures/rainfall are `None`, and narrative explicitly states `"Current telemetry for origin date is UNAVAILABLE. No synthetic observations are substituted."`
- The engine NEVER imputes or estimates missing current observations using model forecasts or climatological averages.

### 3.2 Occurrence Probability vs. Precipitation Volume
- The engine explicitly distinguishes between the probability of rain occurrence ($P(\text{rain} > 0)$ from `xgb_rain_cls_h{h}`) and the conditional rainfall accumulation ($\text{mm}$ from `xgb_rain_amt_h{h}`).
- An 80% rain probability is described as *"an 80.0% likelihood of measurable precipitation"*, never as *"80 mm of rain"* or *"80% heavy rain"*.

### 3.3 Non-Causal SHAP Attribution
- TreeSHAP feature attributions are strictly described as statistical predictive sensitivity or model weighting:
  - *Approved:* `"the model assigned greater predictive contribution to surface thermal baseline and 7-day rolling momentum..."`
  - *Prohibited:* `"atmospheric cloud cover caused nocturnal warming..."` or `"low pressure caused rainfall..."`

### 3.4 Banned Certainty Vocabulary
The following terms are banned by the `ConfidenceLanguageEngine` and `GroundingValidator`:
`"guaranteed"`, `"guarantee"`, `"certain"`, `"certainty"`, `"100% accurate"`, `"perfect"`, `"flawless"`, `"absolute certainty"`, `"foolproof"`.

### 3.5 External Benchmark Status
- Comparisons with external models (e.g., Open-Meteo, ECMWF, GFS) are explicitly categorized as *"external numerical weather prediction benchmark references"*, NEVER as ground truth.
- Actual recorded observations remain the sole ground truth.

---

## 4. Question-Answering Support & Refusal Policy

### 4.1 Supported Question Categories
1. **Forecast Summary:** *"What is the forecast for Jaipur?"*
2. **Rainfall Occurrence:** *"Will it rain tomorrow?"*
3. **Temperature Trajectory:** *"How will the temperature change over the next 12 days?"*
4. **Peak Rain Day:** *"Which day has the highest probability of rain?"*
5. **Forecast Uncertainty:** *"How uncertain is the day 12 forecast?"*
6. **Recent History Comparison:** *"How does today compare with recent observations?"*
7. **Risk Rationale:** *"Why is precipitation risk considered high?"*

### 4.2 Transparent Refusal for Unsupported Variables
The system strictly refuses queries concerning variables outside the Phase 1–7 modeled features. Queries mentioning:
- Relative humidity
- Cloud cover
- Sunshine duration / UV index
- Hourly rain timing
- Air Quality Index (AQI) / particulate pollution
- Radar / Satellite imagery
- Medical, emergency evacuation, or aviation flight planning

Return the following standardized transparent refusal:
> *"Query regarding '[topic]' cannot be answered. The India Weather Forecasting & Intelligence System is strictly validated for daily temperature, precipitation occurrence & amount, wind speed, and surface pressure. Variable '[topic]' is not modeled by the Phase 7 multi-horizon engine. Data unavailable."*

---

## 5. Phase Boundary & Future Phase 9 (FastAPI) Interface

Phase 8 defines the standalone Python intelligence engine. The clean boundary with Phase 9 is established as follows:

```python
# Phase 9 FastAPI endpoint pattern (future implementation):
@app.get("/api/v1/intelligence/{station_id}", response_model=WeatherIntelligenceOutput)
def get_station_intelligence(station_id: str, origin_date: str = "2025-01-20"):
    # 1. Fetch Phase 7 operational timeline
    timeline_dict = operational_ingestion_service.build_operational_timeline(station_id, origin_date)
    # 2. Build verified context input
    context = WeatherContextBuilder.from_operational_timeline_dict(timeline_dict)
    # 3. Execute Phase 8 intelligence engine
    intelligence = WeatherIntelligenceEngine.generate_intelligence(context)
    return intelligence
```

Phase 8 contains zero FastAPI decorators, zero HTTP route handlers, and zero database migration logic, preserving complete separation of concerns.
