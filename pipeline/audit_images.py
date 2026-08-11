import os
import sys
import csv
import io
import re
import json
import base64

import pandas as pd
import requests
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import export_data as ed

IMAGES_DIR = os.path.join(ed.PUBLIC_DATA_DIR, 'legislator_images')
AUDIT_DIR = os.path.join(ed.DATA_DIR, 'image_audit')
PASSPORT_DIR = os.path.join(AUDIT_DIR, 'passports')
BASE64_DIR = os.path.join(AUDIT_DIR, 'base64')
REPORT = os.path.join(AUDIT_DIR, 'audit_report.txt')

PASSPORT_BASE = 'https://admin.placbillstrack.org/passports/'
MATCH_HD = 12
AMBIG_HD = 20


def dhash(img, size=8):
    img = img.convert('L').resize((size + 1, size), Image.LANCZOS)
    px = list(img.getdata())
    h = 0
    bit = 0
    for row in range(size):
        for col in range(size):
            if px[row * (size + 1) + col] < px[row * (size + 1) + col + 1]:
                h |= 1 << bit
            bit += 1
    return h


def hamming(a, b):
    return bin(a ^ b).count('1')


def image_from_bytes(raw):
    try:
        return Image.open(io.BytesIO(raw)).convert('RGB')
    except Exception:
        return None


def load_candidates():
    cands = {}
    for f in os.listdir(IMAGES_DIR):
        if not f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            continue
        if f.startswith('test_'):
            continue
        p = os.path.join(IMAGES_DIR, f)
        try:
            with open(p, 'rb') as fh:
                img = image_from_bytes(fh.read())
            if img is None:
                continue
            cands[f] = dhash(img)
        except Exception:
            continue
    return cands


def download_passport(passport, session):
    if not passport:
        return None
    dst = os.path.join(PASSPORT_DIR, passport)
    if os.path.exists(dst):
        with open(dst, 'rb') as fh:
            return fh.read()
    try:
        r = session.get(PASSPORT_BASE + passport, timeout=30)
        r.raise_for_status()
        with open(dst, 'wb') as fh:
            fh.write(r.content)
        return r.content
    except Exception as e:
        return None


def source_base64(members):
    for m in members:
        raw = m.get('src_base64')
        if not raw:
            continue
        try:
            data = base64.b64decode(raw.split(',', 1)[1] if ',' in raw else raw)
        except Exception:
            data = None
        if not data:
            continue
        img = image_from_bytes(data)
        if img is None:
            continue
        key = f"__base64__{m['name']}_{m['state']}"
        dst = os.path.join(BASE64_DIR, re.sub(r'[^a-z0-9]+', '_', key.lower()) + '.jpg')
        with open(dst, 'wb') as fh:
            fh.write(data)
        m['src_dhash'] = (key, dhash(img))
        m['src_file'] = key


def run():
    os.makedirs(PASSPORT_DIR, exist_ok=True)
    os.makedirs(BASE64_DIR, exist_ok=True)

    session = requests.Session()
    api = ed.load_plac_api_members()
    print(f'API members loaded: {len(api)}')

    # ---- senate members ----
    s_df = pd.read_csv(ed.SENATE_MEMBERS_PATH if hasattr(ed, 'SENATE_MEMBERS_PATH') else os.path.join(ed.DATA_DIR, 'senators_full_joined(in) (1).csv'))
    s_df.columns = s_df.columns.str.strip()
    s_df = s_df[s_df['By (Senator)'].astype(str).str.strip().str.lower() != 'executive']
    s_df = s_df.rename(columns={
        'By (Senator)': 'senator_name',
        'Official Name': 'official_name',
        'State': 'state',
        'District': 'district',
        'Images': 'image_url'
    })
    if 'image_url' not in s_df.columns:
        s_df['image_url'] = ''
    s_df['image_url'] = s_df['image_url'].fillna('').astype(str)
    senators = []
    for _, row in s_df.iterrows():
        senators.append({
            'chamber': 'senate',
            'name': str(row.get('senator_name', '')).strip(),
            'state': str(row.get('state', '')).strip(),
            'official': str(row.get('official_name', '')).strip(),
            'src_raw': str(row.get('image_url', '')).strip(),
            'src_base64': str(row.get('image_url', '')).strip() if str(row.get('image_url', '')).startswith('data:image') else '',
            'current_url': None,
        })

    # ---- house members ----
    h_path = os.path.join(ed.DATA_DIR, 'house_of_reps_master_final.xlsx')
    try:
        h_df = pd.read_excel(h_path, sheet_name='in')
    except ValueError:
        h_df = pd.read_excel(h_path, sheet_name=0)
    h_df.columns = h_df.columns.str.strip()
    h_df = h_df.rename(columns={
        'House of rep member': 'member_name',
        'Official Name': 'official_name',
        'Constituency': 'constituency',
        'State': 'state',
        'images': 'images',
        'images ': 'images'
    })
    if 'images' not in h_df.columns:
        h_df['images'] = ''
    h_df['images'] = h_df['images'].fillna('').astype(str)
    reps = []
    for _, row in h_df.iterrows():
        reps.append({
            'chamber': 'house',
            'name': str(row.get('member_name', '')).strip(),
            'state': str(row.get('state', '')).strip(),
            'official': str(row.get('official_name', '')).strip(),
            'src_raw': str(row.get('images', '')).strip(),
            'src_base64': str(row.get('images', '')).strip() if str(row.get('images', '')).startswith('data:image') else '',
            'current_url': None,
        })

    all_members = senators + reps
    source_base64(all_members)

    # current image urls from the deployed JSONs
    try:
        with open(os.path.join(ed.PUBLIC_DATA_DIR, 'senate.json'), encoding='utf-8') as fh:
            s_json = json.load(fh)['members']
        with open(os.path.join(ed.PUBLIC_DATA_DIR, 'house.json'), encoding='utf-8') as fh:
            h_json = json.load(fh)['members']
        for m in all_members:
            pool = s_json if m['chamber'] == 'senate' else h_json
            for j in pool:
                if ed.normalize_person_name(j.get('name', '')) == ed.normalize_person_name(m['name']) and \
                   str(j.get('state', '')).strip().lower() == m['state'].lower():
                    m['current_url'] = j.get('imageUrl', '')
                    break
    except Exception as e:
        print(f'[warn] could not load current urls: {e}')

    print('Loading candidate photos...')
    candidates = load_candidates()
    print(f'Candidate files: {len(candidates)}')

    # embed base64 candidates into the pool
    for m in all_members:
        if 'src_dhash' in m:
            candidates[m['src_file']] = m['src_dhash'][1]

    lines = []
    no_api = no_pass = 0
    stats = {'MATCH': 0, 'AMBIGUOUS': 0, 'NONE': 0}
    for m in all_members:
        api_m = ed._match_api_member(m['name'], m['state'], m['chamber'])
        passport = api_m['passport'] if api_m else ''
        if not api_m:
            no_api += 1
        raw = download_passport(passport, session)
        pass_dh = None
        if raw:
            img = image_from_bytes(raw)
            if img is not None:
                pass_dh = dhash(img)
        else:
            no_pass += 1

        best = None
        if pass_dh is not None:
            scored = []
            for fname, dh in candidates.items():
                scored.append((hamming(dh, pass_dh), fname))
            scored.sort()
            best = scored[0]
        verdict = 'MATCH' if best and best[0] <= MATCH_HD else ('AMBIGUOUS' if best and best[0] <= AMBIG_HD else 'NONE')
        stats[verdict] += 1
        src = m['src_file'] if 'src_file' in m else (f"base64({len(m['src_base64'])}B)" if m['src_base64'] else (m['src_raw'][:60] if m['src_raw'] else ''))
        best_str = f"{best[0]:>3} {best[1]}" if best else '-'
        lines.append(
            f"[{verdict}] {m['chamber'].upper():6s} {m['name']:<42s} | {m['state']:<14s} | "
            f"passport={passport or 'NONE':<40s} | best={best_str} | src={src}"
        )
        print(lines[-1])

    with open(REPORT, 'w', encoding='utf-8') as fh:
        fh.write(f"Total members: {len(all_members)} | no_api={no_api} no_passport={no_pass}\n")
        fh.write(f"Verdicts: {stats}\n\n")
        fh.write('\n'.join(lines))
    print(f'\nReport written to {REPORT}')
    print(f'Verdicts: {stats} | no_api={no_api} no_passport={no_pass}')


if __name__ == '__main__':
    run()
