import os
import json
import base64
import re
from io import BytesIO

import requests
from PIL import Image

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DATA_DIR = os.path.join(PROJECT_ROOT, "frontend", "public", "data")
IMAGES_DIR = os.path.join(PUBLIC_DATA_DIR, "legislator_images")
os.makedirs(IMAGES_DIR, exist_ok=True)

TARGET_SIZE = (300, 300)
BG_COLOR = (245, 245, 245)

def decode_image(image_url):
    if not image_url:
        return None

    s = image_url.strip()

    if s.startswith('data:image/'):
        try:
            match = re.match(r'data:image/[^;]+;base64,(.+)', s)
            if match:
                data = base64.b64decode(match.group(1))
                return Image.open(BytesIO(data))
        except Exception as e:
            print(f"  [Warning] Failed to decode base64: {e}")
            return None

    if s.startswith('http://') or s.startswith('https://'):
        try:
            resp = requests.get(s, timeout=15, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            resp.raise_for_status()
            return Image.open(BytesIO(resp.content))
        except Exception as e:
            print(f"  [Warning] Failed to download {s[:60]}: {e}")
            return None

    return None


def process_image(img):
    if img.mode in ('RGBA', 'LA', 'P'):
        bg = Image.new('RGB', img.size, BG_COLOR)
        if img.mode == 'P':
            img = img.convert('RGBA')
        bg.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = bg
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    w, h = img.size
    size = min(w, h)
    bias = int(h * 0.15)
    left = (w - size) // 2
    top = max(0, (h - size) // 2 - bias)
    top = min(top, h - size)

    img = img.crop((left, top, left + size, top + size))
    img = img.resize(TARGET_SIZE, Image.LANCZOS)

    return img


def process_member_images():
    for chamber_file in ['house.json', 'senate.json']:
        filepath = os.path.join(PUBLIC_DATA_DIR, chamber_file)
        if not os.path.exists(filepath):
            print(f"[Warning] {chamber_file} not found, skipping...")
            continue

        print(f"[+] Processing {chamber_file}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        members = data.get('members', [])
        updated = 0
        failed = 0
        skipped = 0

        for member in members:
            mid = member['id']
            image_url = member.get('imageUrl', '')

            if not image_url:
                skipped += 1
                continue

            name = member.get('name', '?')
            img = decode_image(image_url)
            if img is None:
                print(f"  [Skip] {name} (id={mid}) — no valid image source")
                failed += 1
                continue

            try:
                img = process_image(img)
                out_path = os.path.join(IMAGES_DIR, f"{mid}.jpg")
                img.save(out_path, 'JPEG', quality=90)
                member['imageUrl'] = f"/data/legislator_images/{mid}.jpg"
                updated += 1
                print(f"  [OK] {name} (id={mid})")
            except Exception as e:
                print(f"  [Error] {name} (id={mid}): {e}")
                failed += 1

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        print(f"  => {updated} processed, {failed} failed, {skipped} no image ({len(members)} total)")


if __name__ == "__main__":
    process_member_images()
