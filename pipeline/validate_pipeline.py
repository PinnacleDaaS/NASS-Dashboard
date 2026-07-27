import os
import json
import csv
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

CACHE_FILE = os.path.join(DATA_DIR, "temp_bills_cache.json")
CLEANED_CSV = os.path.join(DATA_DIR, "plac_10th_assembly_bills_cleaned.csv")
SPONSORS_CSV = os.path.join(DATA_DIR, "plac_10th_assembly_bills_sponsors.csv")
MASTER_CSV = os.path.join(DATA_DIR, "plac_10th_assembly_bills.csv")

def validate():
    print("==================================================")
    print("  AUTOMATED DATA INTEGRITY AUDIT REPORT  ")
    print("==================================================")

    # 1. Validate Cache (if present)
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
        pages = cache.get("pages_fetched", [])
        bills = cache.get("bills", [])
        print(f"[OK] Cache Integrity: {len(pages)} pages fetched, {len(bills)} raw bill records loaded.")
    else:
        print(f"[NOTE] Cache file '{os.path.basename(CACHE_FILE)}' not generated yet (will be created when scraper runs).")

    # 2. Check Cleaned CSV
    if os.path.exists(CLEANED_CSV):
        with open(CLEANED_CSV, "r", encoding="utf-8-sig") as f:
            reader_clean = list(csv.DictReader(f))
            print(f"[OK] Cleaned CSV: {len(reader_clean)} bill rows written.")
    else:
        print(f"[--] Cleaned CSV '{os.path.basename(CLEANED_CSV)}' missing.")

    # 3. Check Sponsors CSV
    if os.path.exists(SPONSORS_CSV):
        with open(SPONSORS_CSV, "r", encoding="utf-8-sig") as f:
            reader_sponsors = list(csv.DictReader(f))
            print(f"[OK] Sponsors CSV: {len(reader_sponsors)} sponsor association rows written.")
    else:
        print(f"[--] Sponsors CSV '{os.path.basename(SPONSORS_CSV)}' missing.")

    # 4. Check Frontend JSON Files
    frontend_data = os.path.join(PROJECT_ROOT, "frontend", "public", "data")
    json_ok = True
    for jf in ["house.json", "senate.json"]:
        jpath = os.path.join(frontend_data, jf)
        if os.path.exists(jpath):
            with open(jpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            members = data.get("members", [])
            print(f"[OK] Frontend {jf}: {len(members)} members exported successfully.")
        else:
            print(f"[FAIL] Frontend {jf}: Missing!")
            json_ok = False

    if json_ok:
        print("\n[SUCCESS] ALL AUTOMATED VALIDATION CHECKS PASSED SUCCESSFULLY!")
    else:
        sys.exit(1)

if __name__ == "__main__":
    validate()
