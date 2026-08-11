import os
import sys

import numpy as np
from PIL import Image, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import export_data as ed

IMAGES_DIR = ed.IMAGES_DIR
AUDIT_DIR = os.path.join(ed.DATA_DIR, 'image_audit')
REPORT = os.path.join(AUDIT_DIR, 'ai_clean_report.txt')

HEADROOM_RATIO = 0.22
TARGET_SIZE = (400, 400)
SHARPNESS = 1.4
CONTRAST = 1.08
COLOR = 1.05
JPEG_QUALITY = 93
BLACK_GUARD = 8.0

IMAGE_EXTS = ('.jpg', '.jpeg', '.png')

try:
    import rembg
    REMBG_OK = True
except ImportError:
    REMBG_OK = False

session = None


def clean_image(img):
    """AI matting -> white canvas -> 22% headroom -> 400x400 HD with edge polish.

    Returns the processed image, or None for near-black/corrupt input.
    """
    arr = np.array(img)
    if arr.mean() < BLACK_GUARD:
        return None

    if REMBG_OK:
        global session
        try:
            if session is None:
                session = rembg.new_session('u2netp')
            rgba = rembg.remove(img, session=session)
            white = Image.new('RGBA', rgba.size, (255, 255, 255, 255))
            white.alpha_composite(rgba)
            studio = white.convert('RGB')
        except Exception:
            studio = img.convert('RGB')
    else:
        studio = img.convert('RGB')

    w, h = studio.size
    pad_h = int(h * HEADROOM_RATIO)
    new_size = h + pad_h
    canvas = Image.new('RGB', (new_size, new_size), (255, 255, 255))
    canvas.paste(studio, ((new_size - w) // 2, pad_h))

    upscaled = canvas.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
    sharp = ImageEnhance.Sharpness(upscaled).enhance(SHARPNESS)
    contrast = ImageEnhance.Contrast(sharp).enhance(CONTRAST)
    return ImageEnhance.Color(contrast).enhance(COLOR)


def run():
    if not REMBG_OK:
        print('rembg is not installed. Run: py -m pip install rembg onnxruntime')
        return 1

    files = [f for f in sorted(os.listdir(IMAGES_DIR)) if f.lower().endswith(IMAGE_EXTS)]
    print(f'Processing {len(files)} images in {IMAGES_DIR} ...')
    print('(first run downloads the u2netp model, ~4 MB)')

    os.makedirs(AUDIT_DIR, exist_ok=True)
    lines = []
    cleaned = skipped = failed = 0

    for i, fname in enumerate(files, 1):
        fpath = os.path.join(IMAGES_DIR, fname)
        try:
            with Image.open(fpath) as img:
                processed = clean_image(img.convert('RGB'))
            if processed is None:
                skipped += 1
                lines.append(f'[SKIPPED_BLACK] {fname}')
                print(f'[{i}/{len(files)}] SKIP  {fname}')
            else:
                processed.save(fpath, 'JPEG', quality=JPEG_QUALITY)
                cleaned += 1
                lines.append(f'[CLEANED] {fname}')
                print(f'[{i}/{len(files)}] OK    {fname}')
        except Exception as e:
            failed += 1
            lines.append(f'[FAILED] {fname} ({e})')
            print(f'[{i}/{len(files)}] FAIL  {fname} ({e})')

    with open(REPORT, 'w', encoding='utf-8') as fh:
        fh.write(f'cleaned={cleaned} skipped_black={skipped} failed={failed} total={len(files)}\n\n')
        fh.write('\n'.join(lines))

    print(f'\ncleaned={cleaned} skipped_black={skipped} failed={failed} total={len(files)}')
    print(f'Report: {REPORT}')
    return 0


if __name__ == '__main__':
    sys.exit(run())
