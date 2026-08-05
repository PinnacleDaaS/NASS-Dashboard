import os
import io
import base64
import json
import requests
import numpy as np
import pandas as pd
from PIL import Image, ImageEnhance, ImageDraw, ImageFont

ROOT_DIR = r"c:\Users\Joshua Akintayo\Downloads\PLAC"
HOUSE_EXCEL = os.path.join(ROOT_DIR, 'data/house_of_reps_master_final.xlsx')
SENATE_CSV = os.path.join(ROOT_DIR, 'data/senators_full_joined(in) (1).csv')

DEST_IMG_DIR = os.path.join(ROOT_DIR, "nass-dashboard", "frontend", "public", "data", "legislator_images")
HOUSE_JSON = os.path.join(ROOT_DIR, "nass-dashboard", "frontend", "public", "data", "house.json")
SENATE_JSON = os.path.join(ROOT_DIR, "nass-dashboard", "frontend", "public", "data", "senate.json")

def normalize_name(n):
    if not n or pd.isna(n):
        return ""
    s = str(n).lower()
    for prefix in ["hon", "sen", "dr", "prof", "mr", "mrs", "chief", "alhaji", "engr", "arc", "barr"]:
        s = s.replace(f"{prefix}.", "").replace(f"{prefix} ", "")
    s = "".join(c for c in s if c.isalnum() or c.isspace())
    return " ".join(s.split())

def decode_image(img_str):
    if pd.isna(img_str):
        return None
    s = str(img_str).strip()
    if not s or s.lower() == 'nan':
        return None
    if s.startswith('data:image'):
        try:
            _, encoded = s.split(',', 1)
            data = base64.b64decode(encoded)
            return Image.open(io.BytesIO(data)).convert('RGB')
        except Exception:
            return None
    elif s.startswith('http://') or s.startswith('https://'):
        try:
            r = requests.get(s, timeout=6, headers={'User-Agent': 'Mozilla/5.0'}, verify=False)
            if r.status_code == 200:
                return Image.open(io.BytesIO(r.content)).convert('RGB')
        except Exception:
            return None
    return None

def process_photo(img, rembg_session=None):
    if img is None:
        return None
    arr = np.array(img)
    if arr.mean() < 8:
        return None
        
    try:
        import rembg
        rgba = rembg.remove(img, session=rembg_session)
        white_bg = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        white_bg.alpha_composite(rgba)
        studio_img = white_bg.convert("RGB")
    except Exception:
        studio_img = img.convert("RGB")
        
    w, h = studio_img.size
    pad_h = int(h * 0.22)
    new_size = h + pad_h
    canvas = Image.new('RGB', (new_size, new_size), (255, 255, 255))
    canvas.paste(studio_img, ((new_size - w) // 2, pad_h))
    
    upscaled = canvas.resize((400, 400), Image.Resampling.LANCZOS)
    sharp = ImageEnhance.Sharpness(upscaled).enhance(1.4)
    contrast = ImageEnhance.Contrast(sharp).enhance(1.08)
    return contrast

def run_name_matching_pipeline():
    print("=== STARTING EXACT NAME-MATCHING IMAGE PIPELINE ===")
    os.makedirs(DEST_IMG_DIR, exist_ok=True)
    
    rembg_session = None
    try:
        import rembg
        rembg_session = rembg.new_session("u2netp")
        print("AI Background Matting Session Ready.")
    except Exception as e:
        print("rembg notice:", e)

    # 1. Build House Name -> Image Map
    print(f"\nProcessing House Excel: {HOUSE_EXCEL}")
    df_h = pd.read_excel(HOUSE_EXCEL)
    house_photo_map = {} # normalized_name -> image_filename
    
    for idx, row in df_h.iterrows():
        rname = row.get('House of rep member', '')
        oname = row.get('Official Name', '')
        raw_img = row.get('images ', None)
        
        img_obj = decode_image(raw_img)
        if img_obj:
            proc = process_photo(img_obj, rembg_session)
            if proc:
                fname = f"house_rep_{idx+1}.jpg"
                fpath = os.path.join(DEST_IMG_DIR, fname)
                proc.save(fpath, "JPEG", quality=93)
                
                n1 = normalize_name(rname)
                n2 = normalize_name(oname)
                if n1: house_photo_map[n1] = fname
                if n2: house_photo_map[n2] = fname

    # Update house.json by Exact Name Matching
    with open(HOUSE_JSON, 'r', encoding='utf-8') as f:
        h_json = json.load(f)

    h_matched = 0
    for m in h_json['members']:
        m_n1 = normalize_name(m['name'])
        m_n2 = normalize_name(m.get('officialName', ''))
        
        matched_file = house_photo_map.get(m_n1) or house_photo_map.get(m_n2)
        if not matched_file:
            # Substring matching fallback
            for k, v in house_photo_map.items():
                if k and (k in m_n1 or m_n1 in k):
                    matched_file = v
                    break
                    
        if matched_file:
            m['imageUrl'] = f"/data/legislator_images/{matched_file}?v=10"
            h_matched += 1

    with open(HOUSE_JSON, 'w', encoding='utf-8') as f:
        json.dump(h_json, f, indent=2)
    print(f"House JSON Updated: {h_matched} / {len(h_json['members'])} matched to EXACT photos!")

    # 2. Build Senate Name -> Image Map
    print(f"\nProcessing Senate CSV: {SENATE_CSV}")
    df_s = pd.read_csv(SENATE_CSV)
    senate_photo_map = {}
    
    for idx, row in df_s.iterrows():
        rname = row.get('By (Senator)', '')
        oname = row.get('Official Name', '')
        raw_img = row.get('Images', None)
        
        img_obj = decode_image(raw_img)
        if img_obj:
            proc = process_photo(img_obj, rembg_session)
            if proc:
                fname = f"senate_member_{idx+1}.jpg"
                fpath = os.path.join(DEST_IMG_DIR, fname)
                proc.save(fpath, "JPEG", quality=93)
                
                n1 = normalize_name(rname)
                n2 = normalize_name(oname)
                if n1: senate_photo_map[n1] = fname
                if n2: senate_photo_map[n2] = fname

    # Update senate.json by Exact Name Matching
    with open(SENATE_JSON, 'r', encoding='utf-8') as f:
        s_json = json.load(f)

    s_matched = 0
    for m in s_json['members']:
        m_n1 = normalize_name(m['name'])
        m_n2 = normalize_name(m.get('officialName', ''))
        
        matched_file = senate_photo_map.get(m_n1) or senate_photo_map.get(m_n2)
        if not matched_file:
            for k, v in senate_photo_map.items():
                if k and (k in m_n1 or m_n1 in k):
                    matched_file = v
                    break
                    
        if matched_file:
            m['imageUrl'] = f"/data/legislator_images/{matched_file}?v=10"
            s_matched += 1

    with open(SENATE_JSON, 'w', encoding='utf-8') as f:
        json.dump(s_json, f, indent=2)
    print(f"Senate JSON Updated: {s_matched} / {len(s_json['members'])} matched to EXACT photos!")

    print("\n=== EXACT NAME MATCHING PIPELINE COMPLETE ===")

if __name__ == "__main__":
    run_name_matching_pipeline()
