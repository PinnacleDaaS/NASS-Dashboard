import os
import io
import base64
import json
import requests
import numpy as np
import pandas as pd
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont

ROOT_DIR = r"c:\Users\Joshua Akintayo\Downloads\PLAC"
HOUSE_EXCEL_ROOT = os.path.join(ROOT_DIR, 'data/house_of_reps_master_final.xlsx')
SENATE_CSV_ROOT = os.path.join(ROOT_DIR, 'data/senators_full_joined(in) (1).csv')

DEST_IMG_DIR = os.path.join(ROOT_DIR, "nass-dashboard", "frontend", "public", "data", "legislator_images")
HOUSE_JSON = os.path.join(ROOT_DIR, "nass-dashboard", "frontend", "public", "data", "house.json")
SENATE_JSON = os.path.join(ROOT_DIR, "nass-dashboard", "frontend", "public", "data", "senate.json")

def decode_image_data(img_str):
    """
    Decodes Base64 data string from the new workbook or fetches HTTP URL.
    """
    if pd.isna(img_str):
        return None
    s = str(img_str).strip()
    if not s or s.lower() == 'nan':
        return None
    
    if s.startswith('data:image'):
        try:
            header, encoded = s.split(',', 1)
            data = base64.b64decode(encoded)
            return Image.open(io.BytesIO(data)).convert('RGB')
        except Exception:
            return None
    elif len(s) > 100 and not s.startswith('http'):
        try:
            data = base64.b64decode(s)
            return Image.open(io.BytesIO(data)).convert('RGB')
        except Exception:
            return None
    elif s.startswith('http://') or s.startswith('https://'):
        try:
            resp = requests.get(s, timeout=6, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code == 200:
                return Image.open(io.BytesIO(resp.content)).convert('RGB')
        except Exception:
            return None
    return None

def create_initials_avatar(name, target_size=(400, 400)):
    """
    Generates a sleek, modern studio initials avatar if a photo is corrupt/missing/solid black.
    """
    img = Image.new('RGB', target_size, color='#0F172A') # Dark slate studio background
    draw = ImageDraw.Draw(img)
    
    clean_name = name.replace("Hon", "").replace("Sen", "").replace("Dr", "").replace("Prof", "").strip()
    parts = clean_name.split()
    initials = f"{parts[0][0]}{parts[1][0]}".upper() if len(parts) >= 2 else (parts[0][0].upper() if parts else "NA")
    
    try:
        font = ImageFont.truetype("arial.ttf", 130)
    except IOError:
        font = ImageFont.load_default()
        
    bbox = draw.textbbox((0, 0), initials, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((400 - w) / 2, (400 - h) / 2 - 15), initials, fill='#10B981', font=font)
    return img

def process_and_clean_image_ai(img, name="", rembg_session=None, target_size=(400, 400)):
    """
    Strips background using AI neural background matting (rembg),
    composites onto pure solid white background (#FFFFFF), adds 22% headroom padding, and resizes to 400x400 HD.
    """
    if img is None:
        return create_initials_avatar(name, target_size)
    
    arr = np.array(img)
    if arr.mean() < 8: # Pure black or corrupt image
        return create_initials_avatar(name, target_size)
        
    # 1. AI Neural Background Removal
    try:
        import rembg
        rgba_img = rembg.remove(img, session=rembg_session)
        # Composite onto pure solid white canvas
        white_bg = Image.new("RGBA", rgba_img.size, (255, 255, 255, 255))
        white_bg.alpha_composite(rgba_img)
        studio_img = white_bg.convert("RGB")
    except Exception as e:
        print(f"rembg AI notice for {name}: {e}")
        studio_img = img.convert("RGB")
    
    # 2. Add 22% top headroom padding so forehead/hair/cap are never cut off
    w, h = studio_img.size
    top_bg_color = (255, 255, 255) # Pure white studio
    
    pad_h = int(h * 0.22)
    new_h = h + pad_h
    new_w = new_h
    
    canvas = Image.new('RGB', (new_w, new_h), top_bg_color)
    paste_x = (new_w - w) // 2
    canvas.paste(studio_img, (paste_x, pad_h))
    
    # 3. Resize to 400x400 HD Lanczos
    upscaled = canvas.resize(target_size, Image.Resampling.LANCZOS)
    
    # 4. Sharpness & Contrast enhancement
    sharp = ImageEnhance.Sharpness(upscaled).enhance(1.4)
    contrast = ImageEnhance.Contrast(sharp).enhance(1.08)
    enhanced = ImageEnhance.Color(contrast).enhance(1.05)
    
    return enhanced

def execute_pipeline():
    print("=== Executing Full AI Neural Background Removal Pipeline ===")
    os.makedirs(DEST_IMG_DIR, exist_ok=True)
    
    # Pre-load rembg session
    rembg_session = None
    try:
        import rembg
        rembg_session = rembg.new_session("u2netp") # Fast lightweight model
        print("AI Neural Background Matting Session initialized successfully!")
    except Exception as e:
        print(f"rembg session init notice: {e}")
    
    # 1. House of Representatives
    print(f"\nProcessing House Reps from NEW Workbook: {HOUSE_EXCEL_ROOT}")
    df_h = pd.read_excel(HOUSE_EXCEL_ROOT)
    
    with open(HOUSE_JSON, 'r', encoding='utf-8') as f:
        h_json = json.load(f)

    h_success = 0
    for idx, row in df_h.iterrows():
        name = row.get('House of rep member', f'Rep_{idx+1}')
        raw_img_val = row.get('images ', None)
        
        img_obj = decode_image_data(raw_img_val)
        cleaned_img = process_and_clean_image_ai(img_obj, name=name, rembg_session=rembg_session, target_size=(400, 400))
        
        img_id = idx + 1
        out_name = f"{img_id}.jpg"
        out_path = os.path.join(DEST_IMG_DIR, out_name)
        cleaned_img.save(out_path, "JPEG", quality=93)
        h_success += 1
        
        if idx < len(h_json['members']):
            h_json['members'][idx]['imageUrl'] = f"/data/legislator_images/{out_name}?v=7"
            
        if (idx + 1) % 50 == 0 or (idx + 1) == len(df_h):
            print(f"House Reps Processed with AI: [{idx+1}/{len(df_h)}]")

    with open(HOUSE_JSON, 'w', encoding='utf-8') as f:
        json.dump(h_json, f, indent=2)
    print(f"Saved {h_success} House Reps images and updated house.json!")

    # 2. Senate
    print(f"\nProcessing Senators from NEW Workbook: {SENATE_CSV_ROOT}")
    df_s = pd.read_csv(SENATE_CSV_ROOT)
    
    with open(SENATE_JSON, 'r', encoding='utf-8') as f:
        s_json = json.load(f)

    s_success = 0
    for idx, row in df_s.iterrows():
        name = row.get('By (Senator)', f'Senator_{idx+1}')
        raw_img_val = row.get('Images', None)
        
        img_obj = decode_image_data(raw_img_val)
        cleaned_img = process_and_clean_image_ai(img_obj, name=name, rembg_session=rembg_session, target_size=(400, 400))
        
        img_id = idx + 1
        out_name = f"senate_{img_id}.jpg"
        out_path = os.path.join(DEST_IMG_DIR, out_name)
        cleaned_img.save(out_path, "JPEG", quality=93)
        s_success += 1
        
        if idx < len(s_json['members']):
            s_json['members'][idx]['imageUrl'] = f"/data/legislator_images/{out_name}?v=7"
            
        if (idx + 1) % 30 == 0 or (idx + 1) == len(df_s):
            print(f"Senators Processed with AI: [{idx+1}/{len(df_s)}]")

    with open(SENATE_JSON, 'w', encoding='utf-8') as f:
        json.dump(s_json, f, indent=2)
    print(f"Saved {s_success} Senate images and updated senate.json!")

    print("\n=== All Images Processed with AI Background Removal & Synced! ===")

if __name__ == "__main__":
    execute_pipeline()
