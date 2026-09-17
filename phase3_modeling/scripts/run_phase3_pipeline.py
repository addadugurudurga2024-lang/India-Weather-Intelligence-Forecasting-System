import argparse
import sys
import logging
from pathlib import Path
from train_xgboost import train_and_evaluate_xgboost
from train_lstm import train_and_evaluate_lstm
from evaluate_models import run_evaluation
import model_config as cfg

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    parser = argparse.ArgumentParser(description="Phase 3 Modeling Pipeline")
    parser.add_argument("--folds", nargs="+", type=int, default=[1, 2], help="Folds to train on")
    parser.add_argument("--models", nargs="+", type=str, default=["xgboost", "lstm"], help="Models to train")
    parser.add_argument("--tasks", nargs="+", type=str, default=["regression", "classification"], help="Tasks to run")
    parser.add_argument("--skip_train", action="store_true", help="Skip training and only evaluate")
    args = parser.parse_args()

    if not args.skip_train:
        for fold in args.folds:
            for task in args.tasks:
                if "xgboost" in args.models:
                    logging.info(f"Starting XGBoost {task} for fold {fold}")
                    train_and_evaluate_xgboost(fold_id=fold, task=task)
                    
                if "lstm" in args.models:
                    logging.info(f"Starting LSTM {task} for fold {fold}")
                    train_and_evaluate_lstm(fold_id=fold, task=task)
                    
    logging.info("Running Holdout Evaluation")
    run_evaluation()
    
    logging.info("Phase 3 Pipeline completed successfully!")

if __name__ == "__main__":
    main()
