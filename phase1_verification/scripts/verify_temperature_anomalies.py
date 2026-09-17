"""
Phase 1.5 Verification Suite - Temperature Anomalies & 87C Investigation
Categorizes the 95 ordering violations, 1 min>max inversion, 1 extreme outlier, and surrounding temporal context.
"""
import pandas as pd
from pathlib import Path
from data_loader import load_authoritative_data

def verify_temperature_anomalies():
    df = load_authoritative_data()
    
    # 1. min_temp > max_temp
    c_min_gt_max = df['min_temp'] > df['max_temp']
    
    # 2. avg_temp < min_temp
    c_avg_lt_min = df['avg_temp'] < df['min_temp']
    
    # 3. avg_temp > max_temp
    c_avg_gt_max = df['avg_temp'] > df['max_temp']
    
    # 4. max_temp > 60
    c_extreme_max = df['max_temp'] > 60
    
    # 5. Combined mask for all anomalies
    anom_mask = c_min_gt_max | c_avg_lt_min | c_avg_gt_max | c_extreme_max
    anom_df = df[anom_mask].copy()
    
    # Assign anomaly category
    def categorize(row):
        cats = []
        if row['max_temp'] > 60:
            cats.append("EXTREME_OUTLIER_GT_60C")
        if row['min_temp'] > row['max_temp']:
            cats.append("MIN_GT_MAX_INVERSION")
        if row['avg_temp'] < row['min_temp']:
            cats.append("AVG_LT_MIN")
        if row['avg_temp'] > row['max_temp']:
            cats.append("AVG_GT_MAX")
        return "; ".join(cats)
        
    anom_df['anomaly_category'] = anom_df.apply(categorize, axis=1)
    
    out_csv = Path(r"D:\weather_forcasting\phase1_verification\outputs\temperature_anomaly_verification.csv")
    cols_to_export = [
        'date_of_record', 'station_name', 'state', 'district', 'latitude', 'longitude', 'elevation',
        'avg_temp', 'min_temp', 'max_temp', 'anomaly_category'
    ]
    anom_df[cols_to_export].to_csv(out_csv, index=True)
    print(f"Verified {len(anom_df)} total temperature anomaly rows. Exported to {out_csv}")
    return anom_df

if __name__ == "__main__":
    verify_temperature_anomalies()
