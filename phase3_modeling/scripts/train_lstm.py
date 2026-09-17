import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import json
from pathlib import Path
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

import model_config as cfg
from data_loaders import get_lstm_dataloaders

class WeatherLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, dropout, task="regression"):
        super(WeatherLSTM, self).__init__()
        self.task = task
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        self.fc = nn.Linear(hidden_size, 1)
        
    def forward(self, x):
        # x shape: (batch_size, seq_len, input_size)
        out, _ = self.lstm(x)
        # Take the output from the last time step
        last_out = out[:, -1, :] # shape: (batch_size, hidden_size)
        logits = self.fc(last_out)
        return logits.squeeze(-1) # shape: (batch_size)

def train_and_evaluate_lstm(fold_id=1, task="regression"):
    print(f"--- Training LSTM for {task.upper()} (Fold {fold_id}) ---")
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    target = cfg.TARGET_TEMP if task == "regression" else cfg.TARGET_RAIN_BIN
    train_loader, val_loader = get_lstm_dataloaders(fold_id=fold_id, target=target)
    
    input_size = len(cfg.FEATURE_COLS)
    
    model = WeatherLSTM(
        input_size=input_size,
        hidden_size=cfg.LSTM_CONFIG["hidden_size"],
        num_layers=cfg.LSTM_CONFIG["num_layers"],
        dropout=cfg.LSTM_CONFIG["dropout"],
        task=task
    ).to(device)
    
    optimizer = optim.Adam(model.parameters(), lr=cfg.LSTM_CONFIG["learning_rate"])
    
    if task == "regression":
        criterion = nn.MSELoss()
    else:
        # Calculate pos_weight for BCEWithLogitsLoss
        # A simple estimate is 1.0, can be refined based on class distribution
        criterion = nn.BCEWithLogitsLoss()
        
    best_val_loss = float('inf')
    patience_counter = 0
    best_model_state = None
    
    for epoch in range(cfg.LSTM_CONFIG["epochs"]):
        model.train()
        train_loss = 0.0
        
        for X_batch, y_batch in train_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            
            optimizer.zero_grad()
            preds = model(X_batch)
            loss = criterion(preds, y_batch)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * X_batch.size(0)
            
        train_loss /= len(train_loader.dataset)
        
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch, y_batch = X_batch.to(device), y_batch.to(device)
                preds = model(X_batch)
                loss = criterion(preds, y_batch)
                val_loss += loss.item() * X_batch.size(0)
                
        val_loss /= len(val_loader.dataset)
        
        print(f"Epoch {epoch+1}/{cfg.LSTM_CONFIG['epochs']} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
        
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            best_model_state = model.state_dict()
        else:
            patience_counter += 1
            if patience_counter >= cfg.LSTM_CONFIG["patience"]:
                print(f"Early stopping at epoch {epoch+1}")
                break
                
    # Load best model for evaluation
    model.load_state_dict(best_model_state)
    
    # Final evaluation on validation set
    model.eval()
    all_preds = []
    all_targets = []
    
    with torch.no_grad():
        for X_batch, y_batch in val_loader:
            X_batch, y_batch = X_batch.to(device), y_batch.to(device)
            preds = model(X_batch)
            if task == "classification":
                probs = torch.sigmoid(preds)
                binary_preds = (probs > 0.5).float()
                all_preds.extend(binary_preds.cpu().numpy())
            else:
                all_preds.extend(preds.cpu().numpy())
            all_targets.extend(y_batch.cpu().numpy())
            
    metrics = evaluate_predictions(all_targets, all_preds, task)
    print(f"Validation Metrics: {metrics}")
    
    # Save model
    model_path = cfg.MODELS_DIR / "lstm" / f"lstm_{task}_fold{fold_id}.pt"
    torch.save(best_model_state, model_path)
    
    return metrics, model

def evaluate_predictions(y_true, y_pred, task="regression"):
    if task == "regression":
        return {
            "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "mae": float(mean_absolute_error(y_true, y_pred)),
            "r2": float(r2_score(y_true, y_pred))
        }
    else:
        return {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, zero_division=0)),
            "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_true, y_pred))
        }

if __name__ == "__main__":
    train_and_evaluate_lstm(fold_id=1, task="regression")
    train_and_evaluate_lstm(fold_id=1, task="classification")
