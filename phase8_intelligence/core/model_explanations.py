"""
Phase 8 Model-Aware Explanations Engine
Explains model architectures, training baselines, and Phase 6 TreeSHAP feature attributions.
CRITICAL NON-CAUSAL RULE:
Explanations strictly describe statistical sensitivity and model predictive contribution.
Never uses causal language (e.g. 'variable X caused rain' or 'cloud insulation').
Uses approved formulation: 'the model assigned greater predictive contribution to...'.
"""

from typing import Dict, Any, List
from phase8_intelligence.core.schemas import ModelContextOutput


class ModelExplanationEngine:
    """Provides grounded, non-causal explanations of model predictions and attributions."""

    @staticmethod
    def get_model_context() -> ModelContextOutput:
        top_features = [
            "avg_temp_clean: surface thermal baseline (mean |SHAP| = 2.83°C predictive contribution)",
            "rolling_7d_temp_mean: synoptic background baseline (mean |SHAP| = 0.41°C predictive contribution)",
            "rolling_3d_temp_mean: short-term thermal momentum (mean |SHAP| = 0.37°C predictive contribution)",
            "lag_1_avg_temp: previous day diurnal anchor (mean |SHAP| = 0.29°C predictive contribution)",
            "doy_cos / doy_sin: deterministic solar declination calendar cycle",
            "elevation: orographic adiabatic altitude adjustment",
        ]

        limitations = [
            "Extreme precipitation (>35 mm/day) is underpredicted due to square-error loss penalization on rare events.",
            "January–February holdout period is dominated by dry season climatology; monsoon generalizability requires continuous validation.",
            "Direct multi-horizon models evaluate static origin state X_0 with future calendar harmonics, not dynamic intermediate NWP physics.",
        ]

        return ModelContextOutput(
            primary_architecture="Direct Multi-Horizon XGBoost Gradient Boosted Trees (84 models, T+1 to T+12)",
            supported_horizons="T+1 to T+12 days ahead",
            attribution_methodology="Phase 6 TreeSHAP Feature Attributions (Statistical Predictive Contribution)",
            top_predictive_features=top_features,
            limitations=limitations,
        )

    @staticmethod
    def explain_temperature_prediction(t_val: float, horizon: int) -> str:
        return (
            f"For horizon T+{horizon}, the direct XGBoost temperature model generated an expected average of {t_val:.1f}°C. "
            f"Statistically, the model assigned primary predictive contribution to the current baseline surface temperature "
            f"and 7-day rolling thermal momentum, combined with future calendar day-of-year solar harmonics. "
            f"This attribution reflects statistical model sensitivity, not physical atmospheric causation."
        )

    @staticmethod
    def explain_rain_probability(prob: float, horizon: int) -> str:
        return (
            f"For horizon T+{horizon}, the direct XGBoost classifier estimated a {prob * 100:.1f}% probability of rain. "
            f"In model feature space, the classifier assigned greatest predictive contribution to prior precipitation history, "
            f"surface minimum-temperature predictive contribution, and seasonal calendar harmonics. "
            f"This value represents a calibrated statistical likelihood, not physical cloud simulation."
        )
