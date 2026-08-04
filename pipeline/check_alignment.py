import os
import json
import pandas as pd

print("=== CHECKING HOUSE OF REPS ALIGNMENT ===")
df_h = pd.read_excel('house_of_reps_master_final.xlsx')
with open('nass-dashboard/frontend/public/data/house.json', 'r', encoding='utf-8') as f:
    h_json = json.load(f)

h_mismatches = 0
for idx in range(min(len(df_h), len(h_json['members']))):
    df_name = str(df_h.iloc[idx]['House of rep member']).strip()
    df_off = str(df_h.iloc[idx].get('Official Name', '')).strip()
    
    json_name = str(h_json['members'][idx]['name']).strip()
    json_off = str(h_json['members'][idx].get('officialName', '')).strip()
    
    # Check if names match
    match = (df_name.lower() in json_name.lower() or json_name.lower() in df_name.lower() or
             df_name.lower() in json_off.lower() or json_off.lower() in df_name.lower() or
             df_off.lower() in json_name.lower() or json_name.lower() in df_off.lower())
             
    if not match:
        h_mismatches += 1
        if h_mismatches <= 15:
            print(f"Row {idx}: DF='{df_name}' / '{df_off}' <---> JSON='{json_name}' / '{json_off}'")

print(f"Total House Mismatches by Index: {h_mismatches} / {min(len(df_h), len(h_json['members']))}")


print("\n=== CHECKING SENATE ALIGNMENT ===")
df_s = pd.read_csv('senators_full_joined(in) (1).csv')
with open('nass-dashboard/frontend/public/data/senate.json', 'r', encoding='utf-8') as f:
    s_json = json.load(f)

s_mismatches = 0
for idx in range(min(len(df_s), len(s_json['members']))):
    df_name = str(df_s.iloc[idx]['By (Senator)']).strip()
    df_off = str(df_s.iloc[idx].get('Official Name', '')).strip()
    
    json_name = str(s_json['members'][idx]['name']).strip()
    json_off = str(s_json['members'][idx].get('officialName', '')).strip()
    
    match = (df_name.lower() in json_name.lower() or json_name.lower() in df_name.lower() or
             df_name.lower() in json_off.lower() or json_off.lower() in df_name.lower() or
             df_off.lower() in json_name.lower() or json_name.lower() in df_off.lower())
             
    if not match:
        s_mismatches += 1
        if s_mismatches <= 15:
            print(f"Row {idx}: DF='{df_name}' / '{df_off}' <---> JSON='{json_name}' / '{json_off}'")

print(f"Total Senate Mismatches by Index: {s_mismatches} / {min(len(df_s), len(s_json['members']))}")
