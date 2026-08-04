import os
import json
import pandas as pd

senators = ['Monday Okpebholo', 'David Umahi', 'Abba Moro']

print("=== CHECKING SENATE.JSON ===")
with open('nass-dashboard/frontend/public/data/senate.json', 'r', encoding='utf-8') as f:
    s_json = json.load(f)

for m in s_json['members']:
    for s in senators:
        if s.lower() in m['name'].lower() or s.lower() in m.get('officialName', '').lower():
            print(f"Name: {m['name']} | State: {m.get('state')} | Dist: {m.get('constituency')} | imageUrl: {m.get('imageUrl')}")

print("\n=== CHECKING ROOT CSV senators_full_joined(in) (1).csv ===")
df_sen = pd.read_csv('senators_full_joined(in) (1).csv')
for idx, row in df_sen.iterrows():
    rname = str(row.get('By (Senator)', ''))
    oname = str(row.get('Official Name', ''))
    for s in senators:
        if s.lower() in rname.lower() or s.lower() in oname.lower():
            img_val = str(row.get('Images', ''))
            print(f"Row {idx} ({rname}): img_val len={len(img_val)}, prefix={img_val[:80]}")
