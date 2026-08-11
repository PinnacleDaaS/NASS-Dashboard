"""Fill missing member photos from the user's latest source files.

Reads the two new files (Downloads copies of the senate CSV and the house
master xlsx, which contain base64 images and gstatic URLs for nearly every
member), maps them to members by normalized name, and writes the photo to
frontend/public/data/legislator_images/<sen|rep>_<slug>.jpg so the export's
slug-first resolution picks it up.

Only fills members whose slug photo is missing; existing (verified) photos
are left untouched. Source files are never modified.
"""
import os
import re
import sys
import base64
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import export_data as ed
import rebuild_images as rb

NEW_SENATE = r'C:\Users\Joshua Akintayo\Downloads\senators_full_joined(in) (1).csv'
NEW_HOUSE = r'C:\Users\Joshua Akintayo\Downloads\house_of_reps_master_final.xlsx'
IMAGES_DIR = ed.IMAGES_DIR
os.makedirs(IMAGES_DIR, exist_ok=True)

_s = requests.Session()
_s.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'


def token_key(name):
    """Name-order-insensitive key (honorific-stripped, apostrophe-merged, sorted tokens)."""
    return ' '.join(sorted(ed._tokenize_person_name(name))) if hasattr(ed, '_tokenize_person_name') else ed.normalize_person_name(name)


def load_new_images():
    import pandas as pd
    out = {}
    toks = {}
    df = pd.read_csv(NEW_SENATE, encoding='utf-8-sig', dtype=str).fillna('')
    for _, r in df.iterrows():
        nm = r.get('By (Senator)', '')
        if nm and r.get('Images', ''):
            out.setdefault(ed.normalize_person_name(nm), r['Images'].strip())
            toks.setdefault(token_key(nm), r['Images'].strip())
    df = pd.read_excel(NEW_HOUSE, dtype=str).fillna('')
    img_col = next((c for c in df.columns if 'image' in c.lower()), None)
    name_col = next((c for c in df.columns if 'member' in c.lower()), None)
    for _, r in df.iterrows():
        nm = r.get(name_col, '')
        if nm and r.get(img_col, ''):
            out.setdefault(ed.normalize_person_name(nm), r[img_col].strip())
            toks.setdefault(token_key(nm), r[img_col].strip())
    return out, toks


def save_image(nm_key, raw, slug_path):
    """Write a photo (base64 data URL or remote URL) to slug_path."""
    if raw.startswith('data:'):
        data = base64.b64decode(raw.split(',', 1)[1])
        with open(slug_path, 'wb') as fh:
            fh.write(data)
        return 'base64'
    if raw.startswith('http'):
        last = None
        for _ in range(3):
            try:
                r = _s.get(raw, timeout=30)
                r.raise_for_status()
                with open(slug_path, 'wb') as fh:
                    fh.write(r.content)
                return 'url'
            except Exception as e:
                last = e
        raise last
    return None


def main():
    new_imgs, new_toks = load_new_images()
    print(f'New-file image map: {len(new_imgs)} entries')

    members = rb.load_members()
    filled = skipped = missing = failed = 0
    for m in members:
        slug = f"{'sen' if m['chamber'] == 'senate' else 'rep'}_{ed.member_image_slug(m['name'])}.jpg"
        slug_path = os.path.join(IMAGES_DIR, slug)
        if os.path.exists(slug_path):
            skipped += 1
            continue
        nm = ed.normalize_person_name(m['name'])
        raw = new_imgs.get(nm) or new_toks.get(token_key(m['name']))
        if not raw:
            print(f'  [missing-in-new-files] {m["chamber"].upper():6s} {m["name"]}')
            missing += 1
            continue
        try:
            src = save_image(nm, raw, slug_path)
            print(f'  [filled {src}] {m["chamber"].upper():6s} {m["name"]}')
            filled += 1
        except Exception as e:
            print(f'  [FAILED] {m["chamber"].upper():6s} {m["name"]}: {e}')
            failed += 1

    print(f'\nfilled={filled} skipped(existing)={skipped} missing={missing} failed={failed}')


if __name__ == '__main__':
    main()
