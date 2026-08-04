import os
import json
import numpy as np
from PIL import Image, ImageEnhance, ImageOps

IMG_DIR = r"c:\Users\Joshua Akintayo\Downloads\PLAC\nass-dashboard\frontend\public\data\legislator_images"
HOUSE_JSON = r"c:\Users\Joshua Akintayo\Downloads\PLAC\nass-dashboard\frontend\public\data\house.json"
SENATE_JSON = r"c:\Users\Joshua Akintayo\Downloads\PLAC\nass-dashboard\frontend\public\data\senate.json"

def process_image_with_headroom(img, headroom_ratio=0.20, target_size=(400, 400)):
    """
    Adds top headroom padding, enhances contrast/sharpness, and resizes to 400x400 HD.
    """
    img = img.convert('RGB')
    w, h = img.size
    arr = np.array(img)
    
    # Detect if top edge has skin or content touching top
    top_bg_color = tuple(arr[:12, :, :].mean(axis=(0, 1)).astype(int))
    
    # Calculate padding height to shift head down into circular frame
    pad_h = int(h * headroom_ratio)
    new_h = h + pad_h
    new_w = new_h
    
    # Create new canvas filled with top background color
    canvas = Image.new('RGB', (new_w, new_h), top_bg_color)
    
    # Paste original image centered horizontally, shifted down by pad_h
    paste_x = (new_w - w) // 2
    canvas.paste(img, (paste_x, pad_h))
    
    # Resize back to target 400x400 HD using Lanczos anti-aliasing
    upscaled = canvas.resize(target_size, Image.Resampling.LANCZOS)
    
    # Enhance sharpness & contrast
    sharp = ImageEnhance.Sharpness(upscaled).enhance(1.4)
    contrast = ImageEnhance.Contrast(sharp).enhance(1.08)
    enhanced = ImageEnhance.Color(contrast).enhance(1.05)
    
    return enhanced

def run_pipeline():
    print(f"Processing all images in {IMG_DIR} with Headroom Padding & HD Upscaling...")
    files = [f for f in os.listdir(IMG_DIR) if f.endswith('.jpg') or f.endswith('.png')]
    
    count = 0
    for fname in files:
        fpath = os.path.join(IMG_DIR, fname)
        try:
            with Image.open(fpath) as img:
                processed = process_image_with_headroom(img, headroom_ratio=0.22, target_size=(400, 400))
                processed.save(fpath, "JPEG", quality=93)
                count += 1
        except Exception as e:
            print(f"Error processing {fname}: {e}")
            
    print(f"Successfully re-processed {count} images with headroom padding!")

    # Update house.json and senate.json with cache-busting query parameter ?v=3
    print("Updating house.json and senate.json image URLs with cache-buster ?v=3 ...")
    
    with open(HOUSE_JSON, 'r', encoding='utf-8') as f:
        h_data = json.load(f)
    for m in h_data['members']:
        url = m.get('imageUrl', '')
        if url:
            base_url = url.split('?')[0]
            m['imageUrl'] = f"{base_url}?v=3"
    with open(HOUSE_JSON, 'w', encoding='utf-8') as f:
        json.dump(h_data, f, indent=2)

    with open(SENATE_JSON, 'r', encoding='utf-8') as f:
        s_data = json.load(f)
    for m in s_data['members']:
        url = m.get('imageUrl', '')
        if url:
            base_url = url.split('?')[0]
            m['imageUrl'] = f"{base_url}?v=3"
    with open(SENATE_JSON, 'w', encoding='utf-8') as f:
        json.dump(s_data, f, indent=2)

    print("house.json and senate.json image URLs updated with ?v=3 cache buster!")

if __name__ == "__main__":
    run_pipeline()
