"""
Phase 6: Task 26 - Explainability Visualization Artifacts Generator
Generates publication-quality evaluation and explainability plots:
1. feature_importance_shap_ranking.png
2. reliability_calibration_diagram.png
3. threshold_tuning_curve.png
4. elevation_error_distribution.png
5. model_benchmark_comparison_matrix.png
"""

import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DATA_PATH = ROOT_DIR / "phase6_evaluation" / "data" / "phase6_evaluation_summary.json"
PLOTS_DIR = ROOT_DIR / "phase6_evaluation" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["font.size"] = 9

def plot_shap_feature_importance():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    
    # 1. Temperature SHAP
    temp_feats = data["explainability"]["temperature_shap_rankings"][:10][::-1]
    names_t = [f["feature"].replace("_", " ") for f in temp_feats]
    values_t = [f["mean_abs_shap"] for f in temp_feats]
    
    bars1 = ax1.barh(names_t, values_t, color="#38bdf8", edgecolor="#0284c7")
    ax1.set_title("XGBoost Temperature Regressor\nMean |SHAP| Feature Attributions", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Mean Absolute SHAP Value (°C)")
    ax1.bar_label(bars1, fmt="%.3f", padding=3, fontsize=8)
    
    # 2. Rain Classification SHAP
    cls_feats = data["explainability"]["rain_classification_shap_rankings"][:10][::-1]
    names_c = [f["feature"].replace("_", " ") for f in cls_feats]
    values_c = [f["mean_abs_shap"] for f in cls_feats]
    
    bars2 = ax2.barh(names_c, values_c, color="#34d399", edgecolor="#059669")
    ax2.set_title("XGBoost Rain Classifier\nMean |SHAP| Feature Attributions", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Mean Absolute SHAP Value (Log-odds)")
    ax2.bar_label(bars2, fmt="%.3f", padding=3, fontsize=8)
    
    plt.tight_layout()
    out = PLOTS_DIR / "feature_importance_shap_ranking.png"
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"Saved: {out}")

def plot_reliability_diagram():
    fig, ax = plt.subplots(figsize=(6.5, 6))
    rel_bins = data["calibration"]["reliability_bins"]
    ece = data["calibration"]["expected_calibration_error"]
    brier = data["calibration"]["brier_score"]
    
    pred_probs = [b["mean_predicted_prob"] for b in rel_bins]
    emp_freqs = [b["empirical_rain_frequency"] for b in rel_bins]
    
    # Perfect calibration line
    ax.plot([0, 1], [0, 1], "k--", label="Perfect Calibration", linewidth=1.5, alpha=0.7)
    
    # Model reliability curve
    ax.plot(pred_probs, emp_freqs, marker="o", color="#0284c7", linewidth=2, markersize=7, label="XGBoost Holdout Predictions")
    
    ax.set_title("Holdout Rain Probability Calibration Curve\n(Reliability Diagram)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Mean Predicted Probability", fontsize=10)
    ax.set_ylabel("Empirical Rain Frequency", fontsize=10)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    
    # Info badge box
    textstr = f"Expected Calibration Error: {ece:.4f}\nBrier Score Loss: {brier:.4f}\nSamples: 16,323 holdout days"
    props = dict(boxstyle="round,pad=0.5", facecolor="#f8fafc", edgecolor="#cbd5e1", alpha=0.9)
    ax.text(0.05, 0.92, textstr, transform=ax.transAxes, fontsize=9, verticalalignment="top", bbox=props)
    
    ax.legend(loc="lower right", frameon=True)
    plt.tight_layout()
    out = PLOTS_DIR / "reliability_calibration_diagram.png"
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"Saved: {out}")

def plot_threshold_tuning_curve():
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    sweep = data["threshold_analysis"]["sweep"]
    
    thresh = [s["threshold"] for s in sweep]
    prec = [s["precision"] for s in sweep]
    rec = [s["recall"] for s in sweep]
    f1 = [s["f1"] for s in sweep]
    
    ax.plot(thresh, prec, label="Precision", color="#38bdf8", linewidth=2)
    ax.plot(thresh, rec, label="Recall", color="#f59e0b", linewidth=2)
    ax.plot(thresh, f1, label="F1-Score", color="#10b981", linewidth=2.5)
    
    opt_t = data["threshold_analysis"]["optimal_f1_threshold"]
    max_f1 = data["threshold_analysis"]["max_f1"]
    
    ax.axvline(opt_t, color="#dc2626", linestyle=":", label=f"F1-Optimal Threshold (τ={opt_t})")
    ax.axvline(0.50, color="#64748b", linestyle="--", label="Default Threshold (τ=0.50)")
    
    ax.set_title("Rain Classification Threshold Sensitivity Curve\nTrade-off Across Decision Boundaries (τ)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Decision Threshold (τ)", fontsize=10)
    ax.set_ylabel("Metric Score", fontsize=10)
    ax.set_ylim(0, 1.05)
    ax.legend(loc="center right", frameon=True, fontsize=8.5)
    
    plt.tight_layout()
    out = PLOTS_DIR / "threshold_tuning_curve.png"
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"Saved: {out}")

def plot_elevation_error_distribution():
    fig, ax = plt.subplots(figsize=(8, 4.5))
    slices = data["error_slices"]["elevation_slices"]
    
    bands = [s["band"] for s in slices]
    maes = [s["mae"] for s in slices]
    counts = [s["count"] for s in slices]
    
    bars = ax.bar(bands, maes, color=["#c084fc", "#a855f7", "#38bdf8", "#34d399", "#2dd4bf"], edgecolor="black", width=0.55)
    ax.set_title("Temperature Forecast Error by Topographic Elevation Band\n(2025 Holdout Validation)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Mean Absolute Error (°C)", fontsize=10)
    ax.set_ylim(0, max(maes) * 1.25)
    
    for b, c in zip(bars, counts):
        h = b.get_height()
        ax.annotate(f"{h:.3f}°C\n(N={c:,})",
                    xy=(b.get_x() + b.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8)
                    
    plt.xticks(rotation=15, ha="right", fontsize=8.5)
    plt.tight_layout()
    out = PLOTS_DIR / "elevation_error_distribution.png"
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"Saved: {out}")

def plot_benchmark_matrix():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    
    models = ["Persistence", "XGBoost (Candidate)", "PyTorch LSTM"]
    temp_maes = [0.7235, 0.6527, 0.6441]
    rain_maes = [0.5026, 0.4344, 0.4368]
    
    x = np.arange(len(models))
    width = 0.35
    
    b1 = ax1.bar(x - width/2, temp_maes, width, label="Temperature MAE (°C)", color="#38bdf8", edgecolor="#0284c7")
    b2 = ax1.bar(x + width/2, rain_maes, width, label="Rainfall Overall MAE (mm)", color="#34d399", edgecolor="#059669")
    
    ax1.set_ylabel("Error Metric (Lower is Better)")
    ax1.set_title("Regression Targets Holdout Benchmarking\n(Temperature & Rainfall Amount)", fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, fontsize=9)
    ax1.legend(loc="upper right")
    ax1.bar_label(b1, fmt="%.4f", padding=3, fontsize=8)
    ax1.bar_label(b2, fmt="%.4f", padding=3, fontsize=8)
    
    # Classification Holdout
    cls_models = ["Majority Class", "XGBoost (Candidate)", "PyTorch LSTM"]
    accuracies = [89.59, 89.19, 88.32]
    roc_aucs = [50.00, 83.66, 82.56]
    
    x2 = np.arange(len(cls_models))
    b3 = ax2.bar(x2 - width/2, accuracies, width, label="Accuracy (%)", color="#818cf8", edgecolor="#4f46e5")
    b4 = ax2.bar(x2 + width/2, roc_aucs, width, label="ROC-AUC (%)", color="#facc15", edgecolor="#ca8a04")
    
    ax2.set_ylabel("Score % (Higher is Better)")
    ax2.set_title("Binary Rain Classification Holdout Benchmarking\n(Accuracy vs Discrimination AUC)", fontweight="bold")
    ax2.set_xticks(x2)
    ax2.set_xticklabels(cls_models, fontsize=9)
    ax2.legend(loc="lower right")
    ax2.bar_label(b3, fmt="%.2f%%", padding=3, fontsize=8)
    ax2.bar_label(b4, fmt="%.2f%%", padding=3, fontsize=8)
    
    plt.tight_layout()
    out = PLOTS_DIR / "model_benchmark_comparison_matrix.png"
    plt.savefig(out, dpi=200)
    plt.close()
    print(f"Saved: {out}")

if __name__ == "__main__":
    plot_shap_feature_importance()
    plot_reliability_diagram()
    plot_threshold_tuning_curve()
    plot_elevation_error_distribution()
    plot_benchmark_matrix()
    print("[PASS] All Phase 6 evaluation and explainability plots generated successfully.")
