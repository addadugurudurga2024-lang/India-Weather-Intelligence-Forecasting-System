"""
Phase 1.5 Verification Suite - State & UT Reconciliation
Reconciles the 32 unique codes vs 36 political States/UTs discrepancy.
"""
import pandas as pd
from pathlib import Path
from data_loader import load_authoritative_data

# Authoritative mapping of ISO/Standard postal 2-letter codes for Indian States and Union Territories
STATE_MAP = {
    'AN': 'Andaman and Nicobar Islands (UT)',
    'AP': 'Andhra Pradesh',
    'AR': 'Arunachal Pradesh',
    'AS': 'Assam',
    'BR': 'Bihar',
    'CH': 'Chandigarh (UT)',
    'CT': 'Chhattisgarh',
    'DD': 'Daman and Diu / Dadra and Nagar Haveli (UT)',
    'DL': 'Delhi (NCT)',
    'GA': 'Goa',
    'GJ': 'Gujarat',
    'HP': 'Himachal Pradesh',
    'HR': 'Haryana',
    'JK': 'Jammu and Kashmir (UT)',
    'KA': 'Karnataka',
    'KL': 'Kerala',
    'LD': 'Lakshadweep (UT)',
    'MH': 'Maharashtra',
    'ML': 'Meghalaya',
    'MN': 'Manipur',
    'MP': 'Madhya Pradesh',
    'MZ': 'Mizoram',
    'NL': 'Nagaland',
    'OR': 'Odisha',
    'PB': 'Punjab',
    'PY': 'Puducherry (UT)',
    'RJ': 'Rajasthan',
    'SK': 'Sikkim',
    'TN': 'Tamil Nadu',
    'TR': 'Tripura',
    'UP': 'Uttar Pradesh',
    'WB': 'West Bengal'
}

# The 4 missing entities from the 36 constitutional total (28 States + 8 UTs):
MISSING_ENTITIES = [
    'JH (Jharkhand)',
    'UT / UK (Uttarakhand)',
    'TG / TS (Telangana)',
    'LA (Ladakh)'
]

def verify_states():
    df = load_authoritative_data()
    state_counts = df['state'].value_counts()
    
    rows = []
    for code, count in state_counts.items():
        name = STATE_MAP.get(code, "Unknown")
        entity_type = "UT" if "(UT)" in name or "(NCT)" in name else "State"
        rows.append({
            "state_code": code,
            "entity_name": name,
            "entity_type": entity_type,
            "record_count": count,
            "pct_share": round((count / len(df)) * 100, 4)
        })
        
    res_df = pd.DataFrame(rows)
    out_csv = Path(r"D:\weather_forcasting\phase1_verification\outputs\state_reconciliation.csv")
    res_df.to_csv(out_csv, index=False)
    print("State reconciliation CSV written to:", out_csv)
    return res_df

if __name__ == "__main__":
    verify_states()
