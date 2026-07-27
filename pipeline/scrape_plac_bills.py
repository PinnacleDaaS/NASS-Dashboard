import time
import requests
import csv
import json
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Resolve paths relative to project root (one level up from pipeline/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
os.makedirs(DATA_DIR, exist_ok=True)

BASE_LIST_URL = "https://admin.placbillstrack.org/api/bills"
PDF_BASE_URL = "https://admin.placbillstrack.org/bill-uploads/"
CACHE_FILE = os.path.join(DATA_DIR, "temp_bills_cache.json")

# Safe multi-threaded concurrency configuration
CONCURRENT_THREADS = 5
THREAD_SLEEP = 0.8  # Seconds to sleep in each worker thread to pace requests safely

cache_lock = threading.Lock()

def load_cache():
    """Load already fetched bills from cache file."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[Warning] Failed to load cache file: {e}. Starting fresh.")
    return {"pages_fetched": [], "bills": []}

def save_cache(cache_data):
    """Save fetched bills and page progress to cache file atomically with retries for Windows file locking."""
    tmp_file = CACHE_FILE + ".tmp"
    try:
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=4)
        for attempt in range(5):
            try:
                os.replace(tmp_file, CACHE_FILE)
                break
            except PermissionError:
                time.sleep(0.1)
        else:
            os.replace(tmp_file, CACHE_FILE)
    except Exception as e:
        print(f"[Error] Failed to write cache file: {e}")

def fetch_page_with_backoff(page):
    """Fetch a single page, backing off exponentially on 429 Too Many Requests."""
    url = f"{BASE_LIST_URL}?page={page}&sort=title_asc"
    sleep_time = 15  # Initial wait time when rate limited
    
    for attempt in range(6):
        try:
            response = requests.get(url, timeout=20)
            
            if response.status_code == 429:
                print(f"[Rate Limit] Hit 429 Too Many Requests on page {page}. Sleeping for {sleep_time} seconds before retry (Attempt {attempt+1}/6)...")
                time.sleep(sleep_time)
                sleep_time += 15  # Linear increase in sleep time
                continue
                
            response.raise_for_status()
            data = response.json()
            return data['data']['data']
            
        except requests.exceptions.RequestException as e:
            print(f"[Network Warning] Failed to fetch page {page} on attempt {attempt+1}: {e}")
            if attempt < 5:
                print(f"Sleeping 5 seconds before retrying...")
                time.sleep(5)
            else:
                raise e
    
    raise Exception(f"Failed to fetch page {page} after maximum retries due to persistent rate limiting.")

def parse_bill(bill, categories_map=None, parties_map=None, states_map=None):
    """Parse a raw bill JSON object into a flat dictionary suitable for CSV output."""
    # Direct basic fields
    bill_id = bill.get("id")
    bill_no = bill.get("bill_no")
    title = bill.get("title")
    status = bill.get("status")
    seat = bill.get("seat")
    concurrence = bill.get("concurrence", "NOT STARTED")
    harmonization = bill.get("harmonization", "NOT STARTED")
    
    # Bill is act flag (Yes/No)
    is_act = "Yes" if bill.get("bill_is_act") == 1 else "No"
    
    # Nested dictionaries (Category, Assembly, Committee)
    category_title = ""
    category = bill.get("category")
    if isinstance(category, dict):
        category_title = category.get("title", "")
    elif categories_map and bill.get("category_id"):
        category_title = categories_map.get(bill["category_id"], "")
        
    assembly_title = ""
    assembly = bill.get("assembly")
    if isinstance(assembly, dict):
        assembly_title = assembly.get("title", "")
        
    committee_title = ""
    committee = bill.get("committee")
    if isinstance(committee, dict):
        committee_title = committee.get("title", "")
        
    # Timestamps
    created_at = bill.get("created_at")
    updated_at = bill.get("updated_at")
    
    # Bill analysis & content description (stripped of newlines for clean CSV output)
    bill_analysis = bill.get("bill_analysis")
    if bill_analysis:
        bill_analysis = " ".join(bill_analysis.split())
    else:
        bill_analysis = ""
        
    bill_content = bill.get("bill_content")
    if bill_content:
        bill_content = " ".join(bill_content.split())
    else:
        bill_content = ""
 
    # Construct PDF direct download links
    bill_upload_link = f"{PDF_BASE_URL}{bill.get('bill_upload')}" if bill.get("bill_upload") else ""
    bill_upload_passed_link = f"{PDF_BASE_URL}{bill.get('bill_upload_passed')}" if bill.get("bill_upload_passed") else ""
    bill_upload_act_link = f"{PDF_BASE_URL}{bill.get('bill_upload_act')}" if bill.get("bill_upload_act") else ""
    bill_upload_report_link = f"{PDF_BASE_URL}{bill.get('bill_upload_report')}" if bill.get("bill_upload_report") else ""
 
    # Lawmaker Sponsors (House & Senate)
    house_sponsors = bill.get("house_sponsors") or []
    senate_sponsors = bill.get("senate_sponsors") or []
    
    sponsor_names = []
    sponsor_parties = []
    sponsor_states = []
    sponsor_details = []
    
    all_sponsors = house_sponsors + senate_sponsors
    for sp in all_sponsors:
        if not isinstance(sp, dict):
            continue
        title_prefix = sp.get("title", "")
        name = sp.get("name", "")
        full_name = f"{title_prefix} {name}".strip() if title_prefix else name
        
        # Get Party
        party_acronym = ""
        party_data = sp.get("party")
        if isinstance(party_data, dict):
            party_acronym = party_data.get("acronym", "")
        elif parties_map and sp.get("party_id"):
            party_acronym = parties_map.get(sp["party_id"], "")
            
        # Get State
        state_title = ""
        state_data = sp.get("state")
        if isinstance(state_data, dict):
            state_title = state_data.get("title", "")
        elif states_map and sp.get("state_id"):
            state_title = states_map.get(sp["state_id"], "")
            
        constituency = sp.get("constituency", "")
        
        # Append lists
        if full_name:
            sponsor_names.append(full_name)
        if party_acronym:
            sponsor_parties.append(party_acronym)
        if state_title:
            sponsor_states.append(state_title)
            
        # Detail string
        desc_parts = []
        if party_acronym:
            desc_parts.append(party_acronym)
        if state_title:
            desc_parts.append(state_title)
        if constituency:
            desc_parts.append(f"Constituency: {constituency}")
            
        desc_str = f"{full_name}"
        if desc_parts:
            desc_str += f" ({', '.join(desc_parts)})"
        sponsor_details.append(desc_str)

    # Semicolon-separated strings
    sponsors_names_str = "; ".join(sponsor_names)
    sponsors_parties_str = "; ".join(set(sponsor_parties))
    sponsors_states_str = "; ".join(set(sponsor_states))
    sponsors_details_str = "; ".join(sponsor_details)

    # Interactive Timeline / Stages History
    stages = bill.get("stages") or []
    timeline_events = []
    current_stage = ""
    
    try:
        sorted_stages = sorted(stages, key=lambda x: x.get("order", 0))
    except Exception:
        sorted_stages = stages
        
    for stg in sorted_stages:
        if not isinstance(stg, dict):
            continue
        stage_title = stg.get("title", "")
        pivot = stg.get("pivot") or {}
        is_current = pivot.get("current", 0)
        
        occurred_house = pivot.get("occurred_in_house_on")
        occurred_senate = pivot.get("occurred_in_senate_on")
        
        dates_desc = []
        if occurred_house:
            dates_desc.append(f"House: {occurred_house}")
        if occurred_senate:
            dates_desc.append(f"Senate: {occurred_senate}")
            
        date_str = f" ({', '.join(dates_desc)})" if dates_desc else " (Not Started)"
        timeline_events.append(f"{stage_title}{date_str}")
        
        if is_current == 2 or is_current == 1 or is_current == "2" or is_current == "1":
            current_stage = stage_title

    timeline_history_str = " -> ".join(timeline_events)
    
    if not current_stage:
        current_stage = status

    return {
        "bill_id": bill_id,
        "bill_number": bill_no,
        "title": title,
        "originating_chamber": seat,
        "assembly": assembly_title,
        "category": category_title,
        "current_status": status,
        "current_stage": current_stage,
        "concurrence": concurrence,
        "harmonization": harmonization,
        "is_act": is_act,
        "committee": committee_title,
        "sponsors_names": sponsors_names_str,
        "sponsors_parties": sponsors_parties_str,
        "sponsors_states": sponsors_states_str,
        "sponsors_full_details": sponsors_details_str,
        "timeline_history": timeline_history_str,
        "bill_analysis": bill_analysis,
        "bill_content": bill_content,
        "pdf_initial_bill": bill_upload_link,
        "pdf_passed_bill": bill_upload_passed_link,
        "pdf_signed_act": bill_upload_act_link,
        "pdf_committee_report": bill_upload_report_link,
        "date_created": created_at,
        "date_updated": updated_at
    }

def fetch_lookups():
    """Fetch categories, parties, and states from the API to build lookup maps."""
    categories_map = {}
    parties_map = {}
    states_map = {}
    
    # 1. Fetch Categories
    try:
        r = requests.get("https://admin.placbillstrack.org/api/categories", timeout=15)
        r.raise_for_status()
        for cat in r.json().get('data', []):
            if cat.get('id') and cat.get('title'):
                categories_map[cat['id']] = cat['title']
        print(f"[+] Loaded {len(categories_map)} categories for lookup.")
    except Exception as e:
        print(f"[Warning] Failed to fetch categories: {e}")

    # 2. Fetch Parties
    try:
        r = requests.get("https://admin.placbillstrack.org/api/parties", timeout=15)
        r.raise_for_status()
        for party in r.json().get('data', []):
            if party.get('id') and party.get('acronym'):
                parties_map[party['id']] = party['acronym']
        print(f"[+] Loaded {len(parties_map)} parties for lookup.")
    except Exception as e:
        print(f"[Warning] Failed to fetch parties: {e}")

    # 3. Fetch States
    try:
        r = requests.get("https://admin.placbillstrack.org/api/states", timeout=15)
        r.raise_for_status()
        for state in r.json().get('data', []):
            if state.get('id') and state.get('title'):
                states_map[state['id']] = state['title']
        print(f"[+] Loaded {len(states_map)} states for lookup.")
    except Exception as e:
        print(f"[Warning] Failed to fetch states: {e}")
        
    return categories_map, parties_map, states_map

def main():
    print("[+] Querying page 1 to discover total pages and metadata...")
    for attempt in range(5):
        try:
            response = requests.get(f"{BASE_LIST_URL}?page=1&sort=title_asc", timeout=15)
            response.raise_for_status()
            list_data = response.json()
            break
        except Exception as e:
            print(f"[Error] Failed to connect to server: {e}. Retrying in 10s...")
            time.sleep(10)
    else:
        print("[Error] Fatal: Could not connect to the API. Exiting.")
        return

    total_items = list_data['data']['total']
    total_pages = list_data['data']['last_page']
    print(f"[+] Server has {total_items} bills across {total_pages} total pages.")

    # Check for refresh flag in arguments
    force_refresh = "--refresh" in sys.argv or "--force-refresh" in sys.argv or "-f" in sys.argv or True

    # Load cache for resumable scraping
    cache = load_cache()
    if force_refresh:
        print("[+] Refresh mode active. Re-fetching all pages to capture new & updated bills...")
        pages_fetched = []
    else:
        pages_fetched = cache.get("pages_fetched", [])

    # Index existing bills by ID for upserting
    bills_map = {}
    for b in cache.get("bills", []):
        if isinstance(b, dict) and b.get("id"):
            bills_map[b["id"]] = b

    print(f"[+] Loaded cache. Previously cached {len(bills_map)} unique bills.")

    pages_to_fetch = [p for p in range(1, total_pages + 1) if p not in pages_fetched]

    if not pages_to_fetch:
        print("[+] All pages already fetched!")
    else:
        print(f"[+] Starting concurrent fetches for {len(pages_to_fetch)} pages using {CONCURRENT_THREADS} threads...")
        
        def worker(page):
            try:
                bills = fetch_page_with_backoff(page)
                
                # Slower pacing inside the threads to prevent rate limit triggers
                time.sleep(THREAD_SLEEP)
                
                with cache_lock:
                    for b in bills:
                        if isinstance(b, dict) and b.get("id"):
                            bills_map[b["id"]] = b
                    if page not in pages_fetched:
                        pages_fetched.append(page)
                    
                    # Update cache in a thread-safe block
                    cache["pages_fetched"] = pages_fetched
                    cache["bills"] = list(bills_map.values())
                    save_cache(cache)
                    
                    # Log progress occasionally
                    if len(pages_fetched) % 10 == 0 or len(pages_fetched) == total_pages:
                        print(f"    Progress Status: {len(pages_fetched)}/{total_pages} pages saved. Total unique bills: {len(bills_map)}")
                
                print(f"[*] Fetched page {page}/{total_pages}")
            except Exception as e:
                print(f"[Error] Thread failed on page {page}: {e}")

        # ThreadPoolExecutor to run tasks concurrently
        with ThreadPoolExecutor(max_workers=CONCURRENT_THREADS) as executor:
            futures = [executor.submit(worker, p) for p in pages_to_fetch]
            # Wait for all futures to complete
            for future in as_completed(futures):
                pass

    bills_collected = list(bills_map.values())
    print(f"\n[+] Scraping complete! Total unique bills in cache: {len(bills_collected)}")
    print("[+] Formatting data and writing to CSV...")

    categories_map, parties_map, states_map = fetch_lookups()
    parsed_bills = []
    for raw_bill in bills_collected:
        parsed_bills.append(parse_bill(raw_bill, categories_map, parties_map, states_map))

    # Define CSV Headers
    headers = [
        "bill_number",
        "title",
        "originating_chamber",
        "assembly",
        "category",
        "current_status",
        "current_stage",
        "concurrence",
        "harmonization",
        "is_act",
        "committee",
        "sponsors_names",
        "sponsors_parties",
        "sponsors_states",
        "sponsors_full_details",
        "timeline_history",
        "bill_analysis",
        "bill_content",
        "pdf_initial_bill",
        "pdf_passed_bill",
        "pdf_signed_act",
        "pdf_committee_report",
        "date_created",
        "date_updated",
        "bill_id"
    ]

    csv_file_path = os.path.join(DATA_DIR, "plac_10th_assembly_bills.csv")
    backup_file_path = os.path.join(DATA_DIR, "plac_10th_assembly_bills_updated.csv")
    
    # Save the backup CSV first to ensure the user has the data immediately
    print(f"[+] Saving to backup CSV file (non-blocking): {backup_file_path}...")
    try:
        with open(backup_file_path, mode='w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for pb in parsed_bills:
                writer.writerow(pb)
        print(f"[+] Successfully saved backup CSV to: {backup_file_path}")
    except Exception as e:
        print(f"[Warning] Failed to write backup CSV: {e}")

    # Now save to the primary CSV file with retry loop
    print(f"[+] Saving to primary CSV file: {csv_file_path}...")
    for attempt in range(5):
        try:
            # Use utf-8-sig for perfect Excel compatibility on Windows (adds BOM)
            with open(csv_file_path, mode='w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                for pb in parsed_bills:
                    writer.writerow(pb)
            break
        except PermissionError:
            print(f"[Warning] '{csv_file_path}' is locked by another application. Retrying in 2 seconds ({attempt+1}/5)...")
            time.sleep(2)
        except Exception as e:
            print(f"[Error] Failed to write CSV: {e}")
            break

    # Keep the raw json cache file as requested by the user
    print(f"[+] Raw JSON cache preserved at '{CACHE_FILE}'.")

    print(f"\n[+] SUCCESS! {len(parsed_bills)} bills successfully extracted and saved to '{csv_file_path}'.")

if __name__ == "__main__":
    start_time = time.time()
    main()
    print(f"Elapsed Time: {time.time() - start_time:.2f} seconds.")
