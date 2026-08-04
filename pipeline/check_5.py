import os
import json
import pandas as pd

names = [
    'Adesola Ayoola Elegbeji',
    'Ibrahim Abdullahi Ali',
    'Abubakar Hassan Fulata',
    'Uchenna Clement Nwachukwu',
    'Isaac Kyale Kwallu'
]

print("=== CHECKING HOUSE.JSON ===")
with open('nass-dashboard/frontend/public/data/house.json', 'r', encoding='utf-8') as f:
    h_json = json.load(f)

for m in h_json['members']:
    for n in names:
        if n.lower() in m['name'].lower() or n.lower() in m.get('officialName', '').lower():
            print(f"Name: {m['name']} | State: {m.get('state')} | Const: {m.get('constituency')} | imageUrl: {m.get('imageUrl')}")

print("\n=== CHECKING ROOT EXCEL house_of_reps_master_final.xlsx ===")
df_root = pd.read_excel('house_of_reps_master_final.xlsx')
for idx, row in df_root.iterrows():
    rname = str(row.get('House of rep member', ''))
    oname = str(row.get('Official Name', ''))
    for n in names:
        if n.lower() in rname.lower() or n.lower() in oname.lower():
            img_val = str(row.get('images ', ''))
            print(f"Row {idx} ({rname}): img_val len={len(img_val)}, prefix={img_val[:80]}")
