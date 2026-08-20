import json
import csv
import os
import re
import sys
import requests
from datetime import datetime

# Resolve paths relative to project root (one level up from pipeline/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from export_data import normalize_house_sponsor_name, normalize_senate_sponsor_name

CACHE_FILE = os.path.join(DATA_DIR, "temp_bills_cache.json")
PDF_BASE_URL = "https://admin.placbillstrack.org/bill-uploads/"

def fetch_lookups():
    """Fetch categories, parties, and states from the API with safe fallbacks."""
    categories_map = {}
    parties_map = {}
    states_map = {}
    
    # 1. Fetch Categories
    try:
        r = requests.get("https://admin.placbillstrack.org/api/categories", timeout=10)
        r.raise_for_status()
        for cat in r.json().get('data', []):
            if cat.get('id') and cat.get('title'):
                categories_map[cat['id']] = cat['title']
        print(f"[+] Loaded {len(categories_map)} categories from API.")
    except Exception as e:
        print(f"[Warning] Failed to fetch categories from API: {e}. Using cached definitions.")

    # 2. Fetch Parties
    try:
        r = requests.get("https://admin.placbillstrack.org/api/parties", timeout=10)
        r.raise_for_status()
        for party in r.json().get('data', []):
            if party.get('id') and party.get('acronym'):
                parties_map[party['id']] = party['acronym']
        print(f"[+] Loaded {len(parties_map)} parties from API.")
    except Exception as e:
        print(f"[Warning] Failed to fetch parties from API: {e}. Using cached definitions.")

    # 3. Fetch States
    try:
        r = requests.get("https://admin.placbillstrack.org/api/states", timeout=10)
        r.raise_for_status()
        for state in r.json().get('data', []):
            if state.get('id') and state.get('title'):
                states_map[state['id']] = state['title']
        print(f"[+] Loaded {len(states_map)} states from API.")
    except Exception as e:
        print(f"[Warning] Failed to fetch states from API: {e}. Using cached definitions.")
        
    return categories_map, parties_map, states_map

def clean_text(text):
    """Normalize text by removing multi-spaces, control characters, and line breaks."""
    if not text:
        return ""
    # Replace newlines, carriage returns, tabs, and multiple spaces with a single space
    cleaned = re.sub(r'[\r\n\t]+', ' ', text)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    return cleaned.strip()

def parse_date(date_str):
    """Parse various date formats into YYYY-MM-DD."""
    if not date_str:
        return None
    # Extract just the date part if it has timestamp
    date_part = date_str.split('T')[0].strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_part, fmt)
        except ValueError:
            continue
    return None

def _normalize_sponsor_key(name, chamber_type):
    """Normalize a sponsor name the same way export_data.py keys its party lookup."""
    if str(chamber_type).strip().lower() == 'senate':
        return normalize_senate_sponsor_name(name)
    return normalize_house_sponsor_name(name)


def load_committed_parties(sponsors_file):
    """Load (chamber, normalized-name) -> party from the existing committed sponsors
    CSV. These are reviewed/correct values and MUST win over live PLAC data, so the
    pipeline never overwrites already-correct party info with blank/NaN scraps."""
    if not os.path.exists(sponsors_file):
        return {}
    existing = {}
    with open(sponsors_file, encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            chamber = str(row.get('chamber_type') or '').strip().lower()
            key = _normalize_sponsor_key(row.get('sponsor_name') or '', chamber)
            party = str(row.get('sponsor_party') or '').strip()
            if key and party:
                existing.setdefault((chamber, key), party)
    return existing


def main():
    if not os.path.exists(CACHE_FILE):
        print(f"[Error] Raw cache file '{CACHE_FILE}' not found! Please run the scraper first.")
        return

    print(f"[+] Loading raw bills from cache: {CACHE_FILE}...")
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)
    
    raw_bills = cache.get("bills", [])
    print(f"[+] Successfully loaded {len(raw_bills)} raw bill records.")

    # Fetch lookup maps
    categories_map, parties_map, states_map = fetch_lookups()

    committed_parties = load_committed_parties(os.path.join(DATA_DIR, "plac_10th_assembly_bills_sponsors.csv"))

    cleaned_bills = []
    sponsors_records = []
    seen_bill_ids = set()
    
    print("[+] Starting data cleaning, translation, and milestone parsing...")

    for bill in raw_bills:
        bill_id = bill.get("id")
        if not bill_id:
            continue
            
        # Deduplication check
        if bill_id in seen_bill_ids:
            continue
        seen_bill_ids.add(bill_id)

        # 1. Basic Fields
        bill_no = clean_text(bill.get("bill_no"))
        title = clean_text(bill.get("title"))
        status = clean_text(bill.get("status"))
        seat = clean_text(bill.get("seat"))
        concurrence = clean_text(bill.get("concurrence", "NOT STARTED"))
        harmonization = clean_text(bill.get("harmonization", "NOT STARTED"))
        is_act = "Yes" if bill.get("bill_is_act") == 1 else "No"

        # 2. Category Lookup & Standardization
        category_title = ""
        category = bill.get("category")
        if isinstance(category, dict):
            category_title = category.get("title", "")
        elif categories_map and bill.get("category_id"):
            category_title = categories_map.get(bill["category_id"], "")
        category_title = clean_text(category_title) or "General/Uncategorized"

        # 3. Assembly & Committee
        assembly_title = ""
        assembly = bill.get("assembly")
        if isinstance(assembly, dict):
            assembly_title = assembly.get("title", "")
        assembly_title = clean_text(assembly_title) or "10th Assembly"

        committee_title = ""
        committee = bill.get("committee")
        if isinstance(committee, dict):
            committee_title = committee.get("title", "")
        committee_title = clean_text(committee_title) or "Not Yet Referred"

        # 4. Text Standardizations
        bill_analysis = clean_text(bill.get("bill_analysis"))
        bill_content = clean_text(bill.get("bill_content"))

        # 5. direct PDF links
        pdf_initial = f"{PDF_BASE_URL}{bill.get('bill_upload')}" if bill.get("bill_upload") else ""
        pdf_passed = f"{PDF_BASE_URL}{bill.get('bill_upload_passed')}" if bill.get("bill_upload_passed") else ""
        pdf_signed = f"{PDF_BASE_URL}{bill.get('bill_upload_act')}" if bill.get("bill_upload_act") else ""
        pdf_committee = f"{PDF_BASE_URL}{bill.get('bill_upload_report')}" if bill.get("bill_upload_report") else ""

        # 6. Sponsor Parsing
        house_sponsors = bill.get("house_sponsors") or []
        senate_sponsors = bill.get("senate_sponsors") or []
        all_sponsors = []

        # Gather Sponsors
        for sp in house_sponsors:
            if isinstance(sp, dict):
                sp["chamber_type"] = "House"
                all_sponsors.append(sp)
        for sp in senate_sponsors:
            if isinstance(sp, dict):
                sp["chamber_type"] = "Senate"
                all_sponsors.append(sp)

        # Parse each sponsor for the relational table
        parsed_sponsors = []
        for idx, sp in enumerate(all_sponsors):
            title_prefix = clean_text(sp.get("title", ""))
            name = clean_text(sp.get("name", ""))
            
            # Standardize prefixes
            if title_prefix.upper() in ("REP", "REP.", "REPRESENTATIVE"):
                title_prefix = "Rep."
            elif title_prefix.upper() in ("SEN", "SEN.", "SENATOR"):
                title_prefix = "Sen."
            
            full_name = f"{title_prefix} {name}".strip() if title_prefix else name
            
            # Resolve party acronym
            party_acronym = ""
            party_data = sp.get("party")
            if isinstance(party_data, dict):
                party_acronym = party_data.get("acronym", "")
            elif parties_map and sp.get("party_id"):
                party_acronym = parties_map.get(sp["party_id"], "")
            party_acronym = clean_text(party_acronym).upper()

            # Committed party wins: live PLAC data must never overwrite the
            # reviewed/correct party values already in the sponsors CSV.
            sponsor_chamber = str(sp['chamber_type']).strip().lower()
            saved_party = committed_parties.get(
                (sponsor_chamber, _normalize_sponsor_key(full_name, sponsor_chamber)))
            if saved_party:
                party_acronym = saved_party

            # Resolve state title
            state_title = ""
            state_data = sp.get("state")
            if isinstance(state_data, dict):
                state_title = state_data.get("title", "")
            elif states_map and sp.get("state_id"):
                state_title = states_map.get(sp["state_id"], "")
            state_title = clean_text(state_title).title()

            constituency = clean_text(sp.get("constituency", ""))
            is_primary = "Yes" if idx == 0 else "No"

            sponsors_records.append({
                "bill_id": bill_id,
                "bill_number": bill_no,
                "sponsor_name": full_name,
                "chamber_type": sp["chamber_type"],
                "sponsor_party": party_acronym,
                "sponsor_state": state_title,
                "sponsor_constituency": constituency,
                "is_primary": is_primary
            })

            parsed_sponsors.append({
                "name": full_name,
                "party": party_acronym,
                "state": state_title,
                "constituency": constituency
            })

        # Extract Primary Sponsor Details for flat sheet
        primary_sponsor_name = ""
        primary_sponsor_party = ""
        primary_sponsor_state = ""
        primary_sponsor_constituency = ""
        if parsed_sponsors:
            primary_sponsor_name = parsed_sponsors[0]["name"]
            primary_sponsor_party = parsed_sponsors[0]["party"]
            primary_sponsor_state = parsed_sponsors[0]["state"]
            primary_sponsor_constituency = parsed_sponsors[0]["constituency"]

        # Concatenate multi-sponsor lists for flat sheet
        sponsors_names_str = "; ".join([s["name"] for s in parsed_sponsors])
        sponsors_parties_str = "; ".join(set([s["party"] for s in parsed_sponsors if s["party"]]))
        sponsors_states_str = "; ".join(set([s["state"] for s in parsed_sponsors if s["state"]]))
        
        sponsors_details_list = []
        for s in parsed_sponsors:
            parts = []
            if s["party"]: parts.append(s["party"])
            if s["state"]: parts.append(s["state"])
            if s["constituency"]: parts.append(f"Constituency: {s['constituency']}")
            desc = s["name"]
            if parts:
                desc += f" ({', '.join(parts)})"
            sponsors_details_list.append(desc)
        sponsors_details_str = "; ".join(sponsors_details_list)

        # 7. Timeline Chronological Milestone Parsing
        stages = bill.get("stages") or []
        try:
            sorted_stages = sorted(stages, key=lambda x: x.get("order", 0))
        except Exception:
            sorted_stages = stages

        # Define milestone variables
        date_first_reading = None
        date_second_reading = None
        date_committee_report = None
        date_passed = None
        date_assented = None
        current_stage_parsed = ""

        for stg in sorted_stages:
            if not isinstance(stg, dict):
                continue
            stg_title = stg.get("title", "").strip()
            pivot = stg.get("pivot") or {}
            
            # Capture stage date
            stg_date_str = pivot.get("occurred_in_house_on") or pivot.get("occurred_in_senate_on")
            stg_date = parse_date(stg_date_str)

            # Map to milestone
            stg_title_lower = stg_title.lower()
            if "first reading" in stg_title_lower or "1st reading" in stg_title_lower:
                date_first_reading = date_first_reading or stg_date
            elif "second reading" in stg_title_lower or "2nd reading" in stg_title_lower:
                date_second_reading = date_second_reading or stg_date
            elif "committee" in stg_title_lower or "report" in stg_title_lower:
                date_committee_report = date_committee_report or stg_date
            elif "third reading" in stg_title_lower or "passed" in stg_title_lower:
                date_passed = date_passed or stg_date
            elif "assent" in stg_title_lower or "signed" in stg_title_lower or "act" in stg_title_lower:
                date_assented = date_assented or stg_date

            if pivot.get("current") in (1, 2, "1", "2"):
                current_stage_parsed = stg_title

        # Re-build chronological string
        timeline_events = []
        for stg in sorted_stages:
            stg_title = stg.get("title", "")
            pivot = stg.get("pivot") or {}
            occ_house = pivot.get("occurred_in_house_on")
            occ_senate = pivot.get("occurred_in_senate_on")
            d_parts = []
            if occ_house: d_parts.append(f"House: {occ_house}")
            if occ_senate: d_parts.append(f"Senate: {occ_senate}")
            d_desc = f" ({', '.join(d_parts)})" if d_parts else " (Not Started)"
            timeline_events.append(f"{stg_title}{d_desc}")
        timeline_history_str = " -> ".join(timeline_events)

        if not current_stage_parsed:
            current_stage_parsed = status

        # Calculate durations in days
        days_first_to_second = ""
        days_in_committee = ""
        days_total_to_passage = ""

        if date_first_reading and date_second_reading:
            diff = (date_second_reading - date_first_reading).days
            days_first_to_second = str(diff) if diff >= 0 else "0"

        if date_second_reading and date_committee_report:
            diff = (date_committee_report - date_second_reading).days
            days_in_committee = str(diff) if diff >= 0 else "0"

        if date_first_reading and date_passed:
            diff = (date_passed - date_first_reading).days
            days_total_to_passage = str(diff) if diff >= 0 else "0"

        # Format dates to string
        date_first_reading_str = date_first_reading.strftime("%Y-%m-%d") if date_first_reading else ""
        date_second_reading_str = date_second_reading.strftime("%Y-%m-%d") if date_second_reading else ""
        date_committee_report_str = date_committee_report.strftime("%Y-%m-%d") if date_committee_report else ""
        date_passed_str = date_passed.strftime("%Y-%m-%d") if date_passed else ""
        date_assented_str = date_assented.strftime("%Y-%m-%d") if date_assented else ""

        # Basic Timestamps
        date_created = clean_text(bill.get("created_at"))
        date_updated = clean_text(bill.get("updated_at"))

        # Append to main flat list
        cleaned_bills.append({
            "bill_id": bill_id,
            "bill_number": bill_no,
            "title": title,
            "originating_chamber": seat,
            "assembly": assembly_title,
            "category": category_title,
            "current_status": status,
            "current_stage": current_stage_parsed,
            "concurrence": concurrence,
            "harmonization": harmonization,
            "is_act": is_act,
            "committee": committee_title,
            "primary_sponsor_name": primary_sponsor_name,
            "primary_sponsor_party": primary_sponsor_party,
            "primary_sponsor_state": primary_sponsor_state,
            "primary_sponsor_constituency": primary_sponsor_constituency,
            "sponsors_names": sponsors_names_str,
            "sponsors_parties": sponsors_parties_str,
            "sponsors_states": sponsors_states_str,
            "sponsors_full_details": sponsors_details_str,
            "date_first_reading": date_first_reading_str,
            "date_second_reading": date_second_reading_str,
            "date_committee_report": date_committee_report_str,
            "date_passed": date_passed_str,
            "date_assented": date_assented_str,
            "days_first_to_second_reading": days_first_to_second,
            "days_in_committee": days_in_committee,
            "total_days_to_passage": days_total_to_passage,
            "timeline_history": timeline_history_str,
            "bill_analysis": bill_analysis,
            "bill_content": bill_content,
            "pdf_initial_bill": pdf_initial,
            "pdf_passed_bill": pdf_passed,
            "pdf_signed_act": pdf_signed,
            "pdf_committee_report": pdf_committee,
            "date_created": date_created,
            "date_updated": date_updated
        })

    # Save Output CSVs
    cleaned_file = os.path.join(DATA_DIR, "plac_10th_assembly_bills_cleaned.csv")
    sponsors_file = os.path.join(DATA_DIR, "plac_10th_assembly_bills_sponsors.csv")
    
    print(f"\n[+] Saving cleaned flat dataset to: {cleaned_file}...")
    headers_cleaned = [
        "bill_id", "bill_number", "title", "originating_chamber", "assembly", "category",
        "current_status", "current_stage", "concurrence", "harmonization", "is_act", "committee",
        "primary_sponsor_name", "primary_sponsor_party", "primary_sponsor_state", "primary_sponsor_constituency",
        "sponsors_names", "sponsors_parties", "sponsors_states", "sponsors_full_details",
        "date_first_reading", "date_second_reading", "date_committee_report", "date_passed", "date_assented",
        "days_first_to_second_reading", "days_in_committee", "total_days_to_passage",
        "timeline_history", "bill_analysis", "bill_content",
        "pdf_initial_bill", "pdf_passed_bill", "pdf_signed_act", "pdf_committee_report",
        "date_created", "date_updated"
    ]
    with open(cleaned_file, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers_cleaned)
        writer.writeheader()
        for row in cleaned_bills:
            writer.writerow(row)
            
    print(f"[+] Saving normalized sponsors dataset to: {sponsors_file}...")
    headers_sponsors = [
        "bill_id", "bill_number", "sponsor_name", "chamber_type", "sponsor_party", 
        "sponsor_state", "sponsor_constituency", "is_primary"
    ]
    with open(sponsors_file, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers_sponsors)
        writer.writeheader()
        for row in sponsors_records:
            writer.writerow(row)

    print(f"\n[+] SUCCESS! Data cleaning completed.")
    print(f"    - Cleaned Flat Table: {len(cleaned_bills)} bills saved to '{cleaned_file}'")
    print(f"    - Cleaned Sponsors Table: {len(sponsors_records)} rows saved to '{sponsors_file}'")

if __name__ == "__main__":
    main()
