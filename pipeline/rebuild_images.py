import os
import sys
import io
import csv
import re
import base64
import shutil

import pandas as pd
import openpyxl
import requests
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import export_data as ed

IMAGES_DIR = os.path.join(ed.PUBLIC_DATA_DIR, 'legislator_images')
AUDIT_DIR = os.path.join(ed.DATA_DIR, 'image_audit')
PASSPORT_DIR = os.path.join(AUDIT_DIR, 'passports')
REPORT = os.path.join(AUDIT_DIR, 'rebuild_report.txt')
PASSPORT_BASE = 'https://admin.placbillstrack.org/passports/'

CONFIRM_HD = 20   # own base64 vs passport -> same person
VERIFIED_HD = 12  # local file vs passport -> verified match

PARTY_SET = {'APC', 'PDP', 'LP', 'YPP', 'SDP', 'NNPP', 'APGA', 'ADC', 'PRP', 'TBD', ''}


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


def image_dh(raw):
    try:
        return dhash(Image.open(io.BytesIO(raw)).convert('RGB'))
    except Exception:
        return None


def file_dh(path):
    try:
        with open(path, 'rb') as fh:
            return image_dh(fh.read())
    except Exception:
        return None


def b64_dh(raw):
    if not raw.startswith('data:image'):
        return None
    try:
        return image_dh(base64.b64decode(raw.split(',', 1)[1]))
    except Exception:
        return None


def slugify(name):
    s = ed.normalize_person_name(name).replace(' ', '_')
    return re.sub(r'[^a-z0-9_]+', '', s) or 'member'


def download_passport(passport, session):
    if not passport:
        return None
    dst = os.path.join(PASSPORT_DIR, passport)
    if os.path.exists(dst):
        with open(dst, 'rb') as fh:
            return fh.read()
    last = None
    for attempt in range(3):
        try:
            r = session.get(PASSPORT_BASE + passport, timeout=30)
            r.raise_for_status()
            with open(dst, 'wb') as fh:
                fh.write(r.content)
            return r.content
        except Exception as e:
            last = e
    print(f'  [warn] passport download failed: {passport} ({last})')
    return None


def load_members():
    members = []
    s_path = os.path.join(ed.DATA_DIR, 'senators_full_joined(in) (1).csv')
    df = pd.read_csv(s_path, encoding='utf-8-sig', dtype=str, keep_default_na=False)
    df.columns = df.columns.str.strip()
    for _, row in df.iterrows():
        nm = str(row.get('By (Senator)', '')).strip()
        if nm.lower() == 'executive':
            continue
        members.append({
            'chamber': 'senate',
            'name': nm,
            'state': str(row.get('State', '')).strip(),
            'official': str(row.get('Official Name', '')).strip(),
            'raw': str(row.get('Images', '')).strip(),
        })
    h_path = os.path.join(ed.DATA_DIR, 'house_of_reps_master_final.xlsx')
    hdf = pd.read_excel(h_path)
    hdf.columns = hdf.columns.str.strip()
    img_col = 'images ' if 'images ' in hdf.columns else 'images'
    for _, row in hdf.iterrows():
        members.append({
            'chamber': 'house',
            'name': str(row.get('House of rep member', '')).strip(),
            'state': str(row.get('State', '')).strip(),
            'official': str(row.get('Official Name', '')).strip(),
            'raw': str(row.get(img_col, '') or '').strip(),
        })
    return members


def run():
    os.makedirs(PASSPORT_DIR, exist_ok=True)
    session = requests.Session()
    ed.load_plac_api_members()

    members = load_members()
    print(f'Members: {len(members)}')

    # preload local candidate dhashes (all files except test_*)
    candidates = {}
    for f in os.listdir(IMAGES_DIR):
        if f.startswith('test_'):
            continue
        dh = file_dh(os.path.join(IMAGES_DIR, f))
        if dh is not None:
            candidates[f] = dh
    print(f'Local candidate files: {len(candidates)}')

    lines = []
    resolved = unresolved = 0
    for m in members:
        api = ed._match_api_member(m['name'], m['state'], m['chamber'])
        ppt = api['passport'] if api else ''
        ppt_raw = download_passport(ppt, session)
        ppt_dh = image_dh(ppt_raw) if ppt_raw else None
        b64_dh_v = b64_dh(m['raw'])
        slug = f"{'sen' if m['chamber'] == 'senate' else 'rep'}_{slugify(m['name'])}.jpg"
        slug_path = os.path.join(IMAGES_DIR, slug)
        slug_dh = file_dh(slug_path) if os.path.exists(slug_path) else None
        verdict = ''
        choice = None  # ('keep' | 'base64' | 'passport' | 'copy', data-or-path)

        if slug_dh is not None:
            if ppt_dh is not None:
                d = hamming(slug_dh, ppt_dh)
                if d <= CONFIRM_HD:
                    verdict = 'SLUG_VERIFIED(%d)' % d
                    choice = ('keep', None)
                else:
                    verdict = 'SLUG_REPLACED(mismatch %d)' % d
                    choice = ('passport', ppt_raw)
            else:
                verdict = 'SLUG_KEPT'
                choice = ('keep', None)
        elif b64_dh_v is not None:
            if ppt_dh is not None:
                d = hamming(b64_dh_v, ppt_dh)
                if d <= CONFIRM_HD:
                    verdict = 'BASE64_CONFIRMED'
                    choice = ('base64', m['raw'])
                else:
                    verdict = 'PASSPORT_OVERRIDE(mismatch %d)' % d
                    choice = ('passport', ppt_raw)
            else:
                verdict = 'BASE64_ONLY'
                choice = ('base64', m['raw'])
        elif ppt_dh is not None:
            best = None
            for fname, dh in candidates.items():
                d = hamming(ppt_dh, dh)
                if d <= VERIFIED_HD and (best is None or d < best[0]):
                    best = (d, fname)
            if best:
                verdict = 'LOCAL_VERIFIED(%d)' % best[0]
                choice = ('copy', os.path.join(IMAGES_DIR, best[1]))
            else:
                verdict = 'PASSPORT'
                choice = ('passport', ppt_raw)
        else:
            verdict = 'NO_IMAGE'

        src_desc = m['raw'][:40] if m['raw'] else ''
        if choice:
            if choice[0] == 'keep':
                pass
            elif choice[0] == 'base64':
                data = base64.b64decode(choice[1].split(',', 1)[1])
                with open(slug_path, 'wb') as fh:
                    fh.write(data)
            elif choice[0] == 'passport':
                with open(slug_path, 'wb') as fh:
                    fh.write(choice[1])
            else:
                if os.path.abspath(choice[1]) != os.path.abspath(slug_path):
                    shutil.copyfile(choice[1], slug_path)
            m['out'] = slug
            resolved += 1
        else:
            m['out'] = ''
            unresolved += 1

        line = f"[{verdict:<34s}] {m['chamber'].upper():6s} {m['name']:<44s} | {m['state']:<14s} | {m['out'] or 'NO-IMAGE'} | ppt={ppt or '-'} | src={src_desc}"
        lines.append(line)
        print(line)

    with open(REPORT, 'w', encoding='utf-8') as fh:
        fh.write(f"resolved={resolved} unresolved={unresolved}\n\n")
        fh.write('\n'.join(lines))
    print(f'\nresolved={resolved} unresolved={unresolved}')
    print(f'Report: {REPORT}')
    print(f'Idempotent run: slug files in {IMAGES_DIR} are the source of truth (no source files rewritten).')


if __name__ == '__main__':
    run()
