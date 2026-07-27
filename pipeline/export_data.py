import os
import json
import re
import pandas as pd
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
PUBLIC_DATA_DIR = os.path.join(PROJECT_ROOT, "frontend", "public", "data")
os.makedirs(PUBLIC_DATA_DIR, exist_ok=True)

# ----------------------------------------------------
# Name Normalization & Hardcoded Maps
# ----------------------------------------------------

def normalize_person_name(name):
    name = str(name).lower()
    name = re.sub(r'\b(senator|sen|hon|rt|dr|mr|mrs|ms|prof|chief|alhaji|alh|engr|arc|barr)\b\.?', ' ', name)
    name = re.sub(r'[^a-z ]+', ' ', name)
    return ' '.join(name.split())

HOUSE_SPONSOR_NAME_MAP = {
    'yusuf ahmad badau': 'yusuf badau',
    'canice moore nwachukwu': 'canice moore chukwugozi nwachukwu',
    'aderemi abasi oseni': 'oseni abasi aderemi',
    'isaac kwallu': 'isaac kyale kwallu',
    'adeyemi benjamin olabinjo': 'olabinjo benjamin adeyemi',
    'chinwe clara nnabuife': 'nnabuife chinwe clara',
    'chinedu ogah': 'chinedu nweke ogah',
    'muhammed bello shehu': 'mohammed bello shehu',
    'aliyu sani madaki': 'aliyu sani madakin',
    'dumnamene robinson dekor': 'dekor dumnamene robinson',
    'abdullahi ibrahim ali': 'ibrahim abdullahi ali',
    'nnolim john nnaji': 'nnaji nnolim john',
    'lemke emil inyang': 'lemke emil inyang',
    'bello ambarura isah': 'isah bello ambarura',
    'abubakar hassan nalaraba': 'hassan abdullakar nalaraba',
    'makki yalleman abubakar': 'makki yalloman abubakar',
    'jafaru gambe leko': 'jafaru gambe leko',
    'akanni enitan dolapo badru': 'akanni enitan dolapo badru',
    'abubakar hassan fulata': 'abubakar hassan fulata',
    'peter gyendeng': 'peter gyendeng',
    'david agada ogewu': 'david ogewu',
    'olufemi ogunbanwo': 'ogunbanwo adeleke olufemi',
    'tijjani zannah zakariya': 'zakariya tijjani zannah',
    'uchenna clement nwachukwu': 'uchenna clement nwachukwu',
    'ojema ojotu': 'ojema ojotu',
    'cornelius abidun aderin': 'adesida abiodun cornelius aderin',
    'adesida abiodun': 'adesida abiodun cornelius aderin',
    'aliyu iliyasu': 'aliyu ilyasu',
    'alfred ajang iliya': 'ajang alfred iliya',
    'daniel amos': 'amos daniel',
    'akeem adeniyi adeyemi': 'adeyemi akeem adeniyi',
    'adeboye paul kalejaiye': 'kalejaiye adeboye paul',
    'abubakar ahmad mohammed': 'abubakar ahmad mohammad',
}

SENATE_SPONSOR_NAME_MAP = {
    'ndubueze patrick chiwuba': 'ndubueze patrick chinwuba',
    'yar adua abdulaziz musa': 'abdulaziz yar adua',
    'konbowel benson friday': 'konbowei benson friday',
    'mohammed dandutse muntari': 'dandutse muntari mohammed',
    'dafinone ede omueya': 'omueya dafinone edeh',
    'nwokocha darlington': 'darlington nwokocha',
}

def normalize_house_sponsor_name(name):
    key = normalize_person_name(name)
    return HOUSE_SPONSOR_NAME_MAP.get(key, key)

def normalize_senate_sponsor_name(name):
    key = normalize_person_name(name)
    return SENATE_SPONSOR_NAME_MAP.get(key, key)

def extract_third_reading_status(timeline_history):
    match = re.search(r'Third Reading/Concurrence \(([^)]*)\)', str(timeline_history))
    if not match:
        return ''
    return match.group(1).strip()

def has_passed_third_reading(third_reading_status):
    status = str(third_reading_status).strip()
    return bool(status) and status.lower() != 'not started'

def format_date_str(val):
    if pd.isna(val) or not str(val).strip():
        return ''
    try:
        dt = pd.to_datetime(val, errors='coerce')
        if pd.notna(dt):
            return dt.strftime('%Y-%m-%d')
    except Exception:
        pass
    return str(val).strip()

# ----------------------------------------------------
# Load Sponsor Join Table
# ----------------------------------------------------

def load_bill_sponsors_data(chamber_type):
    path = os.path.join(DATA_DIR, 'plac_10th_assembly_bills_sponsors.csv')
    if not os.path.exists(path):
        return pd.DataFrame()

    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    for col in ['bill_id', 'sponsor_name', 'chamber_type', 'sponsor_party', 'sponsor_state', 'sponsor_constituency', 'is_primary']:
        if col not in df.columns:
            df[col] = ''
        df[col] = df[col].fillna('').astype(str)

    df = df[df['chamber_type'].str.strip().str.lower().eq(str(chamber_type).lower())].copy()
    if df.empty:
        return df

    if str(chamber_type).lower() == 'senate':
        df['sponsor_key'] = df['sponsor_name'].apply(normalize_senate_sponsor_name)
    else:
        df['sponsor_key'] = df['sponsor_name'].apply(normalize_house_sponsor_name)

    df['is_primary_bool'] = df['is_primary'].str.strip().str.lower().eq('yes')
    return df

# ----------------------------------------------------
# Build House Data
# ----------------------------------------------------

def build_house_data():
    print("[+] Exporting House of Representatives data...")
    house_members_path = os.path.join(DATA_DIR, 'house_of_reps_master_final.xlsx')
    house_bills_path = os.path.join(DATA_DIR, 'cleaned_house_bills_final.xlsx')

    if not os.path.exists(house_members_path) or not os.path.exists(house_bills_path):
        print("[Warning] House source files missing!")
        return

    m_df = pd.read_excel(house_members_path, sheet_name='in').iloc[:360]
    m_df.columns = m_df.columns.str.strip()
    m_df = m_df.rename(columns={
        'House of rep member': 'rep_name',
        'Official Name': 'official_name',
        'Constituency': 'constituency',
        'State': 'state',
        'images': 'image_url',
        'images ': 'image_url'
    })
    if 'image_url' not in m_df.columns:
        m_df['image_url'] = ''
    m_df['image_url'] = m_df['image_url'].fillna('').astype(str)

    # Overrides from app.py
    override_image = """data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxMSEhUSExIVFRUXFRUVFxYWFRUVFxcVFRUXFhcVFRUYHSggGBolHRUVITEhJSkrLi4vFx8zODMsNygtLisBCgoKDg0OFRAQGC8dHSItLS0tLS0tLS0tKy0tLSstLS0tKy0tLS0tKy0tLSsrLS0uKy0rLS0tKy0tLS0tLS0tLf/AABEIAOEA4AMBIgACEQEDEQH/xAAcAAABBQEBAQ~~~~~~~~"""
    mask1 = m_df['rep_name'].astype(str).str.strip().str.lower().str.contains('adetunji abidemi olusoji', na=False)
    mask2 = m_df['official_name'].astype(str).str.strip().str.lower().str.contains('adetunji abidemi olusoji', na=False)
    if mask1.any() or mask2.any():
        m_df.loc[mask1 | mask2, 'image_url'] = override_image

    adewale_hameed_image = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRTgSAnhTL7Yg_9OLCxATIEn0Z0LrAP7CbFnjGjX_eD3w&s'
    adewale_hameed_mask = (
        m_df['rep_name'].astype(str).str.strip().str.lower().eq('hon adewale hameed')
        | m_df['official_name'].astype(str).str.strip().str.lower().eq('hammed adewale waheed')
    )
    m_df.loc[adewale_hameed_mask, 'image_url'] = adewale_hameed_image

    m_df['rep_key'] = m_df['rep_name'].apply(normalize_person_name)
    m_df['official_key'] = m_df['official_name'].apply(normalize_person_name)

    # Bills Data
    b_df = pd.read_excel(house_bills_path, sheet_name='in')
    b_df.columns = b_df.columns.str.strip()
    for col in ['bill_id', 'title', 'date_first_reading', 'date_second_reading', 'timeline_history', 'primary_sponsor_name', 'sponsors_names', 'sponsors_full_details', 'committee']:
        if col not in b_df.columns:
            b_df[col] = ''
        b_df[col] = b_df[col].fillna('').astype(str)

    b_df['third_reading_status'] = b_df['timeline_history'].apply(extract_third_reading_status)
    b_df['passed_third_reading'] = b_df['third_reading_status'].apply(has_passed_third_reading)
    b_df['sponsor_key'] = b_df['primary_sponsor_name'].apply(normalize_house_sponsor_name)

    sponsor_table = load_bill_sponsors_data('House')
    if not sponsor_table.empty:
        sponsor_keys_by_bill = sponsor_table.groupby('bill_id')['sponsor_key'].apply(list).to_dict()
        cosponsor_keys_by_bill = sponsor_table[~sponsor_table['is_primary_bool']].groupby('bill_id')['sponsor_key'].apply(list).to_dict()
        b_df['sponsor_keys'] = b_df['bill_id'].map(sponsor_keys_by_bill).apply(lambda v: v if isinstance(v, list) else [])
        b_df['cosponsor_keys'] = b_df['bill_id'].map(cosponsor_keys_by_bill).apply(lambda v: v if isinstance(v, list) else [])
    else:
        b_df['sponsor_keys'] = b_df['sponsors_names'].apply(lambda x: [normalize_house_sponsor_name(n) for n in str(x).split(';') if n])
        b_df['cosponsor_keys'] = b_df['sponsor_keys'].apply(lambda k: k[1:] if len(k) > 1 else [])

    # Process members and their linked bills
    members_list = []
    constituencies_by_state = {}

    for idx, row in m_df.iterrows():
        m_id = str(idx + 1)
        name = str(row.get('rep_name', '')).strip()
        official_name = str(row.get('official_name', '')).strip()
        state = str(row.get('state', '')).strip()
        constituency = str(row.get('constituency', '')).strip()
        image_url = str(row.get('image_url', '')).strip()

        if state and constituency and state.lower() != 'tbd':
            constituencies_by_state.setdefault(state, set()).add(constituency)

        keys = {row.get('rep_key', ''), row.get('official_key', '')} - {''}

        # Find sponsored bills
        sponsored_mask = b_df['sponsor_key'].isin(keys)
        sponsored_bills_df = b_df[sponsored_mask]

        # Find co-sponsored bills
        cosponsored_mask = b_df['cosponsor_keys'].apply(lambda c_keys: bool(keys.intersection(set(c_keys))))
        cosponsored_bills_df = b_df[cosponsored_mask & (~sponsored_mask)]

        def format_bill_obj(b_row):
            return {
                "billId": str(b_row.get('bill_id', '')),
                "title": str(b_row.get('title', '')),
                "dateFirstReading": format_date_str(b_row.get('date_first_reading', '')),
                "dateSecondReading": format_date_str(b_row.get('date_second_reading', '')),
                "committee": str(b_row.get('committee', '')),
                "thirdReadingStatus": str(b_row.get('third_reading_status', '')),
                "passedThirdReading": bool(b_row.get('passed_third_reading', False)),
                "primarySponsor": str(b_row.get('primary_sponsor_name', '')),
                "sponsorsDetails": str(b_row.get('sponsors_full_details', ''))
            }

        sponsored_bills = [format_bill_obj(r) for _, r in sponsored_bills_df.iterrows()]
        cosponsored_bills = [format_bill_obj(r) for _, r in cosponsored_bills_df.iterrows()]

        total_sponsored = len(sponsored_bills)
        total_cosponsored = len(cosponsored_bills)
        total_linked = total_sponsored + total_cosponsored

        passed_count = sum(1 for b in sponsored_bills if b['passedThirdReading'])
        conversion_rate = round((passed_count / total_sponsored) * 100) if total_sponsored > 0 else 0

        # Calculate first and latest bill dates
        all_dates = []
        for b in sponsored_bills + cosponsored_bills:
            if b['dateFirstReading']:
                all_dates.append(b['dateFirstReading'])
        all_dates.sort()
        first_date = all_dates[0] if all_dates else ""
        latest_date = all_dates[-1] if all_dates else ""

        members_list.append({
            "id": m_id,
            "name": name,
            "officialName": official_name,
            "state": state,
            "constituency": constituency,
            "imageUrl": image_url,
            "sponsoredBills": sponsored_bills,
            "cosponsoredBills": cosponsored_bills,
            "totalBills": total_linked,
            "sponsoredCount": total_sponsored,
            "cosponsoredCount": total_cosponsored,
            "conversionRate": conversion_rate,
            "billsPassed": passed_count,
            "firstBillDate": first_date,
            "latestBillDate": latest_date
        })

    # Stats & Leaderboards
    total_members = len(members_list)
    members_with_bills = sum(1 for m in members_list if m['totalBills'] > 0)
    total_unique_bills = len(b_df)

    # Sort members by total bills for leaderboards
    members_with_linked = [m for m in members_list if m['totalBills'] > 0]
    members_with_linked_sorted = sorted(members_with_linked, key=lambda x: x['totalBills'], reverse=True)

    def format_lb_entry(m):
        return {
            "id": m['id'],
            "name": m['name'],
            "state": m['state'],
            "constituency": m['constituency'],
            "billCount": m['totalBills'],
            "sponsoredCount": m['sponsoredCount'],
            "cosponsoredCount": m['cosponsoredCount'],
            "conversionRate": m['conversionRate']
        }

    top_20 = [format_lb_entry(m) for m in members_with_linked_sorted[:20]]
    least_20 = [format_lb_entry(m) for m in members_with_linked_sorted[-20:][::-1]]

    states_list = sorted(list({m['state'] for m in members_list if m['state']}))
    constituencies_dict = {st: sorted(list(c_set)) for st, c_set in constituencies_by_state.items()}

    last_updated_str = datetime.now().strftime("%B %d, %Y")

    house_payload = {
        "lastUpdated": last_updated_str,
        "members": members_list,
        "stats": {
            "totalMembers": total_members,
            "totalBills": total_unique_bills,
            "membersWithBills": members_with_bills
        },
        "leaderboards": {
            "top20": top_20,
            "least20": least_20
        },
        "states": states_list,
        "constituencies": constituencies_dict
    }

    out_file = os.path.join(PUBLIC_DATA_DIR, "house.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(house_payload, f, indent=2)

    print(f"[+] Successfully exported {total_members} House members to '{out_file}'.")

# ----------------------------------------------------
# Build Senate Data
# ----------------------------------------------------

def build_senate_data():
    print("[+] Exporting Senate data...")
    senate_members_path = os.path.join(DATA_DIR, 'senators_full_joined(in) (1).csv')
    senate_bills_path = os.path.join(DATA_DIR, 'cleaned_hreps_bills_final.xlsx')

    if not os.path.exists(senate_members_path) or not os.path.exists(senate_bills_path):
        print("[Warning] Senate source files missing!")
        return

    m_df = pd.read_csv(senate_members_path)
    m_df.columns = m_df.columns.str.strip()
    m_df = m_df[m_df['By (Senator)'].astype(str).str.strip().str.lower() != 'executive'].iloc[:109]
    m_df = m_df.rename(columns={
        'By (Senator)': 'senator_name',
        'Official Name': 'official_name',
        'State': 'state',
        'District': 'district',
        'Images': 'image_url'
    })
    if 'image_url' not in m_df.columns:
        m_df['image_url'] = ''
    m_df['image_url'] = m_df['image_url'].fillna('').astype(str)

    m_df['senator_key'] = m_df['senator_name'].apply(normalize_person_name)
    m_df['official_key'] = m_df['official_name'].apply(normalize_person_name)

    # Bills Data
    b_df = pd.read_excel(senate_bills_path, sheet_name='in')
    b_df.columns = b_df.columns.str.strip()
    for col in ['bill_id', 'title', 'date_first_reading', 'date_second_reading', 'timeline_history', 'primary_sponsor_name', 'sponsors_names', 'sponsors_full_details', 'committee']:
        if col not in b_df.columns:
            b_df[col] = ''
        b_df[col] = b_df[col].fillna('').astype(str)

    b_df['third_reading_status'] = b_df['timeline_history'].apply(extract_third_reading_status)
    b_df['passed_third_reading'] = b_df['third_reading_status'].apply(has_passed_third_reading)
    b_df['sponsor_key'] = b_df['primary_sponsor_name'].apply(normalize_senate_sponsor_name)

    sponsor_table = load_bill_sponsors_data('Senate')
    if not sponsor_table.empty:
        sponsor_keys_by_bill = sponsor_table.groupby('bill_id')['sponsor_key'].apply(list).to_dict()
        cosponsor_keys_by_bill = sponsor_table[~sponsor_table['is_primary_bool']].groupby('bill_id')['sponsor_key'].apply(list).to_dict()
        b_df['sponsor_keys'] = b_df['bill_id'].map(sponsor_keys_by_bill).apply(lambda v: v if isinstance(v, list) else [])
        b_df['cosponsor_keys'] = b_df['bill_id'].map(cosponsor_keys_by_bill).apply(lambda v: v if isinstance(v, list) else [])
    else:
        b_df['sponsor_keys'] = b_df['sponsors_names'].apply(lambda x: [normalize_senate_sponsor_name(n) for n in str(x).split(';') if n])
        b_df['cosponsor_keys'] = b_df['sponsor_keys'].apply(lambda k: k[1:] if len(k) > 1 else [])

    members_list = []
    districts_by_state = {}

    for idx, row in m_df.iterrows():
        m_id = str(idx + 1)
        name = str(row.get('senator_name', '')).strip()
        official_name = str(row.get('official_name', '')).strip()
        state = str(row.get('state', '')).strip()
        district = str(row.get('district', '')).strip()
        image_url = str(row.get('image_url', '')).strip()

        if state and district and state.lower() != 'tbd':
            districts_by_state.setdefault(state, set()).add(district)

        keys = {row.get('senator_key', ''), row.get('official_key', '')} - {''}

        # Find sponsored bills
        sponsored_mask = b_df['sponsor_key'].isin(keys)
        sponsored_bills_df = b_df[sponsored_mask]

        # Find co-sponsored bills
        cosponsored_mask = b_df['cosponsor_keys'].apply(lambda c_keys: bool(keys.intersection(set(c_keys))))
        cosponsored_bills_df = b_df[cosponsored_mask & (~sponsored_mask)]

        def format_bill_obj(b_row):
            return {
                "billId": str(b_row.get('bill_id', '')),
                "title": str(b_row.get('title', '')),
                "dateFirstReading": format_date_str(b_row.get('date_first_reading', '')),
                "dateSecondReading": format_date_str(b_row.get('date_second_reading', '')),
                "committee": str(b_row.get('committee', '')),
                "thirdReadingStatus": str(b_row.get('third_reading_status', '')),
                "passedThirdReading": bool(b_row.get('passed_third_reading', False)),
                "primarySponsor": str(b_row.get('primary_sponsor_name', '')),
                "sponsorsDetails": str(b_row.get('sponsors_full_details', ''))
            }

        sponsored_bills = [format_bill_obj(r) for _, r in sponsored_bills_df.iterrows()]
        cosponsored_bills = [format_bill_obj(r) for _, r in cosponsored_bills_df.iterrows()]

        total_sponsored = len(sponsored_bills)
        total_cosponsored = len(cosponsored_bills)
        total_linked = total_sponsored + total_cosponsored

        passed_count = sum(1 for b in sponsored_bills if b['passedThirdReading'])
        conversion_rate = round((passed_count / total_sponsored) * 100) if total_sponsored > 0 else 0

        all_dates = []
        for b in sponsored_bills + cosponsored_bills:
            if b['dateFirstReading']:
                all_dates.append(b['dateFirstReading'])
        all_dates.sort()
        first_date = all_dates[0] if all_dates else ""
        latest_date = all_dates[-1] if all_dates else ""

        members_list.append({
            "id": m_id,
            "name": name,
            "officialName": official_name,
            "state": state,
            "constituency": district,  # Frontend uses constituency field generically for district
            "imageUrl": image_url,
            "sponsoredBills": sponsored_bills,
            "cosponsoredBills": cosponsored_bills,
            "totalBills": total_linked,
            "sponsoredCount": total_sponsored,
            "cosponsoredCount": total_cosponsored,
            "conversionRate": conversion_rate,
            "billsPassed": passed_count,
            "firstBillDate": first_date,
            "latestBillDate": latest_date
        })

    # Stats & Leaderboards
    total_members = len(members_list)
    members_with_bills = sum(1 for m in members_list if m['totalBills'] > 0)
    total_unique_bills = len(b_df)

    members_with_linked = [m for m in members_list if m['totalBills'] > 0]
    members_with_linked_sorted = sorted(members_with_linked, key=lambda x: x['totalBills'], reverse=True)

    def format_lb_entry(m):
        return {
            "id": m['id'],
            "name": m['name'],
            "state": m['state'],
            "constituency": m['constituency'],
            "billCount": m['totalBills'],
            "sponsoredCount": m['sponsoredCount'],
            "cosponsoredCount": m['cosponsoredCount'],
            "conversionRate": m['conversionRate']
        }

    top_20 = [format_lb_entry(m) for m in members_with_linked_sorted[:20]]
    least_20 = [format_lb_entry(m) for m in members_with_linked_sorted[-20:][::-1]]

    states_list = sorted(list({m['state'] for m in members_list if m['state']}))
    districts_dict = {st: sorted(list(d_set)) for st, d_set in districts_by_state.items()}

    last_updated_str = datetime.now().strftime("%B %d, %Y")

    senate_payload = {
        "lastUpdated": last_updated_str,
        "members": members_list,
        "stats": {
            "totalMembers": total_members,
            "totalBills": total_unique_bills,
            "membersWithBills": members_with_bills
        },
        "leaderboards": {
            "top20": top_20,
            "least20": least_20
        },
        "states": states_list,
        "constituencies": districts_dict
    }

    out_file = os.path.join(PUBLIC_DATA_DIR, "senate.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(senate_payload, f, indent=2)

    print(f"[+] Successfully exported {total_members} Senators to '{out_file}'.")

if __name__ == "__main__":
    build_house_data()
    build_senate_data()
    print("[+] Data export pipeline finished successfully!")
