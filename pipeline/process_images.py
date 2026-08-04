import os
import json
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

INPUT_DIR = r"c:\Users\Joshua Akintayo\Downloads\PLAC\nass-dashboard\frontend\public\data\legislator_images"
OUTPUT_DIR = r"c:\Users\Joshua Akintayo\Downloads\PLAC\nass-dashboard\frontend\public\data\legislator_images"

def get_face_and_head_bbox(img):
    """
    Estimate head/face vertical span to ensure headroom at top.
    Looks for skin tones, hair contrast, and edge variance in the upper 70% of image.
    """
    w, h = img.size
    arr = np.array(img.convert('RGB'))
    
    # Calculate row-wise variance / activity in upper 70%
    upper_h = int(h * 0.7)
    row_vars = np.var(arr[:upper_h, :, :], axis=(1, 2))
    
    # Find top of head (first row where variance exceeds background threshold)
    threshold = np.min(row_vars) + (np.max(row_vars) - np.min(row_vars)) * 0.15
    active_rows = np.where(row_vars > threshold)[0]
    
    if len(active_rows) > 0:
        top_head_y = max(0, active_rows[0] - int(h * 0.05))
    else:
        top_head_y = 0
        
    return top_head_y

def process_single_image(image_path, target_size=(400, 400)):
    """
    Enhance, head-crop, upscale, and studio-clean a single legislator image.
    """
    with Image.open(image_path) as orig_img:
        img = orig_img.convert('RGB')
        w, h = img.size
        
        top_head_y = get_face_and_head_bbox(img)
        
        # Calculate square crop bounding box with headroom
        headroom = int(h * 0.08) # Headroom padding
        crop_top = max(0, top_head_y - headroom)
        
        # We want a 1:1 aspect ratio square crop centered horizontally
        crop_h = min(h - crop_top, w)
        crop_w = crop_h
        
        crop_left = max(0, (w - crop_w) // 2)
        crop_right = crop_left + crop_w
        crop_bottom = crop_top + crop_h
        
        # If crop_bottom exceeds image height, shift crop up
        if crop_bottom > h:
            diff = crop_bottom - h
            crop_top = max(0, crop_top - diff)
            crop_bottom = h
            
        cropped = img.crop((crop_left, crop_top, crop_right, crop_bottom))
        
        # Upscale to high-def target size using Lanczos anti-aliasing
        upscaled = cropped.resize(target_size, Image.Resampling.LANCZOS)
        
        # Sharpness enhancement (1.35x for crisp facial details)
        sharp = ImageEnhance.Sharpness(upscaled).enhance(1.35)
        
        # Contrast & Color vibrancy balancing
        contrast = ImageEnhance.Contrast(sharp).enhance(1.06)
        enhanced = ImageEnhance.Color(contrast).enhance(1.05)
        
        return enhanced

def run_pipeline():
    print(f"Starting image enhancement pipeline on directory: {INPUT_DIR}")

    if not os.path.exists(INPUT_DIR):
        print(f"Error: {INPUT_DIR} does not exist.")
        return

    files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.jpg') or f.endswith('.png') or f.endswith('.webp')]
    print(f"Found {len(files)} image files to process.")

    processed_count = 0
    error_count = 0

    for idx, fname in enumerate(files, 1):
        fpath = os.path.join(INPUT_DIR, fname)
        try:
            enhanced_img = process_single_image(fpath, target_size=(400, 400))
            
            # Save processed image as high-quality JPEG (400x400)
            base_name, _ = os.path.splitext(fname)
            
            # Save optimized 400x400 JPG (quality 92)
            jpg_out = os.path.join(OUTPUT_DIR, f"{base_name}.jpg")
            enhanced_img.save(jpg_out, "JPEG", quality=92)
            
            processed_count += 1
            if idx % 50 == 0 or idx == len(files):
                print(f"Processed [{idx}/{len(files)}] images...")
        except Exception as e:
            print(f"Error processing {fname}: {e}")
            error_count += 1

    print(f"\nPipeline finished! Successfully processed: {processed_count}, Errors: {error_count}")

if __name__ == "__main__":
    run_pipeline()
