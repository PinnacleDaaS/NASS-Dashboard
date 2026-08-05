import os
import json
import pandas as pd

HOUSE_EXCEL_ROOT = r"c:\Users\Joshua Akintayo\Downloads\PLAC\nass-dashboard\data\house_of_reps_master_final.xlsx"
HOUSE_EXCEL_DATA = r"c:\Users\Joshua Akintayo\Downloads\PLAC\nass-dashboard\data\house_of_reps_master_final.xlsx"

SENATE_CSV_ROOT = r"c:\Users\Joshua Akintayo\Downloads\PLAC\nass-dashboard\data\senators_full_joined(in) (1).csv"
SENATE_CSV_DATA = r"c:\Users\Joshua Akintayo\Downloads\PLAC\nass-dashboard\data\senators_full_joined(in) (1).csv"

HOUSE_JSON = r"c:\Users\Joshua Akintayo\Downloads\PLAC\nass-dashboard\frontend\public\data\house.json"
SENATE_JSON = r"c:\Users\Joshua Akintayo\Downloads\PLAC\nass-dashboard\frontend\public\data\senate.json"

def sync():
    print("Syncing master datasets and frontend JSON...")

    # Load JSON files
    with open(HOUSE_JSON, 'r', encoding='utf-8') as f:
        h_json = json.load(f)

    with open(SENATE_JSON, 'r', encoding='utf-8') as f:
        s_json = json.load(f)

    # 1. Update House Excel files
    df_h = pd.read_excel(HOUSE_EXCEL_ROOT)
    for i, m in enumerate(h_json['members']):
        if i < len(df_h):
            df_h.at[i, 'images '] = m.get('imageUrl', f'/data/legislator_images/{i+1}.jpg')
            # Clear 'nc' flag if present
            if 'nc' in df_h.columns and df_h.at[i, 'nc'] == 'nc':
                df_h.at[i, 'nc'] = 'Cleaned & Upscaled'

    df_h.to_excel(HOUSE_EXCEL_ROOT, index=False)
    if os.path.exists(os.path.dirname(HOUSE_EXCEL_DATA)):
        df_h.to_excel(HOUSE_EXCEL_DATA, index=False)
    print("Updated House Excel master files.")

    # 2. Update Senate CSV files
    df_s = pd.read_csv(SENATE_CSV_ROOT)
    for i, m in enumerate(s_json['members']):
        if i < len(df_s):
            df_s.at[i, 'Images'] = m.get('imageUrl', f'/data/legislator_images/{i+1}.jpg')

    df_s.to_csv(SENATE_CSV_ROOT, index=False)
    if os.path.exists(os.path.dirname(SENATE_CSV_DATA)):
        df_s.to_csv(SENATE_CSV_DATA, index=False)
    print("Updated Senate CSV master files.")

    print("All master dataset files successfully updated!")

if __name__ == "__main__":
    sync()
