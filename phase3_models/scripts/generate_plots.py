import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, roc_curve, precision_recall_curve

BASE_DIR = Path(r"d:\weather_forcasting\phase3_models")
PRED_DIR = BASE_DIR / "predictions"
PLOTS_DIR = BASE_DIR / "plots"
METRICS_DIR = BASE_DIR / "metrics"

def generate_evaluation_plots():
    print("Generating comprehensive diagnostic plots...")
    
    # 1. Temperature Actual vs Predicted & Residuals (Holdout)
    xgb_temp_holdout = PRED_DIR / "xgb_temp_preds_holdout.parquet"
    if xgb_temp_holdout.exists():
        df_temp = pd.read_parquet(xgb_temp_holdout)
        sample = df_temp.sample(min(5000, len(df_temp)), random_state=42)
        
        plt.figure(figsize=(12, 5))
        plt.subplot(1, 2, 1)
        plt.scatter(sample["actual"], sample["predicted"], alpha=0.3, color="#1f77b4", s=15)
        min_v = min(sample["actual"].min(), sample["predicted"].min())
        max_v = max(sample["actual"].max(), sample["predicted"].max())
        plt.plot([min_v, max_v], [min_v, max_v], 'r--', lw=2)
        plt.title("XGBoost Temperature: Actual vs Predicted (Holdout 2025)")
        plt.xlabel("Actual Temperature (°C)")
        plt.ylabel("Predicted Temperature (°C)")
        
        plt.subplot(1, 2, 2)
        residuals = sample["actual"] - sample["predicted"]
        plt.hist(residuals, bins=40, color="#1f77b4", edgecolor="black", alpha=0.7)
        plt.axvline(0, color="red", linestyle="--")
        plt.title("Temperature Prediction Residuals (°C)")
        plt.xlabel("Error (Actual - Predicted)")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / "temp_eval_actual_vs_pred_residuals.png", dpi=150)
        plt.close()

    # 2. Rainfall Amount Actual vs Predicted & Error Distribution
    xgb_rain_holdout = PRED_DIR / "xgb_rain_preds_holdout.parquet"
    if xgb_rain_holdout.exists():
        df_rain = pd.read_parquet(xgb_rain_holdout)
        rainy_sample = df_rain[df_rain["actual"] > 0]
        
        plt.figure(figsize=(12, 5))
        plt.subplot(1, 2, 1)
        plt.scatter(rainy_sample["actual"], rainy_sample["predicted"], alpha=0.5, color="#2ca02c", s=18)
        max_r = max(rainy_sample["actual"].max(), rainy_sample["predicted"].max())
        plt.plot([0, max_r], [0, max_r], 'r--', lw=2)
        plt.title("Rainfall Amount (Rainy Days > 0mm): Actual vs Predicted")
        plt.xlabel("Actual Rainfall (mm)")
        plt.ylabel("Predicted Rainfall (mm)")
        
        plt.subplot(1, 2, 2)
        rain_errors = df_rain["actual"] - df_rain["predicted"]
        plt.hist(rain_errors.clip(-20, 20), bins=40, color="#2ca02c", edgecolor="black", alpha=0.7)
        plt.title("Rainfall Error Distribution (Clipped [-20, 20]mm)")
        plt.xlabel("Error (mm)")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / "rain_amount_eval_scatter_and_error.png", dpi=150)
        plt.close()

    # 3. Rain Classification: Confusion Matrix, ROC Curve, PR Curve
    xgb_cls_holdout = PRED_DIR / "xgb_rain_cls_preds_holdout.parquet"
    if xgb_cls_holdout.exists():
        df_cls = pd.read_parquet(xgb_cls_holdout)
        y_true = df_cls["actual"].values
        y_prob = df_cls["probability"].values
        y_pred = df_cls["predicted"].values
        
        cm = confusion_matrix(y_true, y_pred)
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        precision, recall, _ = precision_recall_curve(y_true, y_prob)
        
        plt.figure(figsize=(15, 4.5))
        
        # Confusion Matrix
        plt.subplot(1, 3, 1)
        plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
        plt.title("Confusion Matrix (Holdout)")
        plt.colorbar()
        classes = ["Dry (0)", "Rain (1)"]
        tick_marks = np.arange(len(classes))
        plt.xticks(tick_marks, classes)
        plt.yticks(tick_marks, classes)
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                plt.text(j, i, format(cm[i, j], 'd'),
                         horizontalalignment="center",
                         color="white" if cm[i, j] > cm.max() / 2 else "black")
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        
        # ROC Curve
        plt.subplot(1, 3, 2)
        plt.plot(fpr, tpr, color="#d62728", lw=2, label="ROC (Holdout)")
        plt.plot([0, 1], [0, 1], 'k--', lw=1)
        plt.title("ROC Curve")
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.legend(loc="lower right")

        # PR Curve
        plt.subplot(1, 3, 3)
        plt.plot(recall, precision, color="#9467bd", lw=2, label="PR Curve")
        plt.title("Precision-Recall Curve")
        plt.xlabel("Recall")
        plt.ylabel("Precision")
        plt.legend(loc="lower left")

        plt.tight_layout()
        plt.savefig(PLOTS_DIR / "rain_cls_eval_cm_roc_pr.png", dpi=150)
        plt.close()
        
    # 4. Cross-Model Benchmark Comparison Plot (if metrics_summary.json exists)
    summary_path = METRICS_DIR / "metrics_summary.json"
    if summary_path.exists():
        with open(summary_path, "r") as f:
            summary = json.load(f)
            
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))
        
        # Temp MAE
        models = ["Baseline", "XGBoost", "LSTM"]
        temp_maes = [
            summary["target_a_temperature"]["baseline"]["fold2_val"]["mae"],
            summary["target_a_temperature"]["xgboost"]["fold2"]["mae"],
            summary["target_a_temperature"]["lstm"]["fold2"]["mae"]
        ]
        axes[0].bar(models, temp_maes, color=["#7f7f7f", "#1f77b4", "#ff7f0e"], alpha=0.85)
        axes[0].set_title("Temperature Validation MAE (°C, Fold 2)")
        axes[0].set_ylabel("MAE (°C)")
        for i, v in enumerate(temp_maes):
            axes[0].text(i, v + 0.01, f"{v:.4f}", ha="center", fontweight="bold")
            
        # Rain Amount MAE
        rain_maes = [
            summary["target_b_rainfall_amount"]["baseline"]["fold2_val"]["mae"],
            summary["target_b_rainfall_amount"]["xgboost"]["fold2"]["mae"],
            summary["target_b_rainfall_amount"]["lstm"]["fold2"]["mae"]
        ]
        axes[1].bar(models, rain_maes, color=["#7f7f7f", "#2ca02c", "#d62728"], alpha=0.85)
        axes[1].set_title("Rainfall Amount Validation MAE (mm, Fold 2)")
        axes[1].set_ylabel("MAE (mm)")
        for i, v in enumerate(rain_maes):
            axes[1].text(i, v + 0.05, f"{v:.2f}", ha="center", fontweight="bold")
            
        # Rain Classification F1
        rain_f1s = [
            summary["target_c_rain_binary"]["baseline"]["fold2_val"]["f1"],
            summary["target_c_rain_binary"]["xgboost"]["fold2"]["f1"],
            summary["target_c_rain_binary"]["lstm"]["fold2"]["f1"]
        ]
        axes[2].bar(models, rain_f1s, color=["#7f7f7f", "#9467bd", "#8c564b"], alpha=0.85)
        axes[2].set_title("Rain/No-Rain Validation F1 (Fold 2)")
        axes[2].set_ylabel("F1 Score")
        for i, v in enumerate(rain_f1s):
            axes[2].text(i, v + 0.02, f"{v:.4f}", ha="center", fontweight="bold")
            
        plt.tight_layout()
        plt.savefig(PLOTS_DIR / "cross_model_benchmark_comparison.png", dpi=150)
        plt.close()
        
    print("All diagnostic plots generated in phase3_models/plots/")

if __name__ == "__main__":
    generate_evaluation_plots()
