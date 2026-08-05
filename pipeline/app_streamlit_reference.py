import streamlit as st
import pandas as pd
from pathlib import Path
import base64
import io
import re
import html

def parse_bill_date(series):
    return pd.to_datetime(series, errors='coerce', format='mixed', dayfirst=False)

@st.cache_data
def load_house_data(file_mtime=None):
    path = Path('data/house_of_reps_master_final.xlsx')
    df = pd.read_excel(path, sheet_name='in')
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        'House of rep member': 'rep_name',
        'Official Name': 'official_name',
        'Constituency': 'constituency',
        'State': 'state',
        'images': 'image_url',
        'images ': 'image_url'
    })
    if 'image_url' not in df.columns:
        df['image_url'] = ''
    df['image_url'] = df['image_url'].fillna('').astype(str)
    # If you need to override or correct specific member images, add them here.
    # Update Hon Adetunji Abidemi Olusoji with provided base64 image
    override_image = """data:image/jpeg;base64,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"""
    try:
        mask1 = df['rep_name'].astype(str).str.strip().str.lower().str.contains('adetunji abidemi olusoji')
    except Exception:
        mask1 = pd.Series(False, index=df.index)
    try:
        mask2 = df['official_name'].astype(str).str.strip().str.lower().str.contains('adetunji abidemi olusoji')
    except Exception:
        mask2 = pd.Series(False, index=df.index)
    if mask1.any() or mask2.any():
        df.loc[mask1 | mask2, 'image_url'] = override_image
    adewale_hameed_image = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRTgSAnhTL7Yg_9OLCxATIEn0Z0LrAP7CbFnjGjX_eD3w&s'
    adewale_hameed_mask = (
        df['rep_name'].astype(str).str.strip().str.lower().eq('hon adewale hameed')
        | df['official_name'].astype(str).str.strip().str.lower().eq('hammed adewale waheed')
    )
    df.loc[adewale_hameed_mask, 'image_url'] = adewale_hameed_image
    df['rep_key'] = df['rep_name'].apply(normalize_person_name)
    df['official_key'] = df['official_name'].apply(normalize_person_name)
    return df


@st.cache_data
def load_house_bills_data():
    path = Path('cleaned_house_bills_final.xlsx')
    df = pd.read_excel(path, sheet_name='in')
    df.columns = df.columns.str.strip()
    for col in [
        'bill_id',
        'title',
        'date_first_reading',
        'date_second_reading',
        'timeline_history',
        'primary_sponsor_name',
        'sponsors_names',
        'sponsors_full_details',
        'committee'
    ]:
        if col not in df.columns:
            df[col] = ''
        df[col] = df[col].fillna('').astype(str)
    df['first_reading_date'] = parse_bill_date(df['date_first_reading'])
    df['second_reading_date'] = parse_bill_date(df['date_second_reading'])
    df['third_reading_status'] = df['timeline_history'].apply(extract_third_reading_status)
    df['passed_third_reading'] = df['third_reading_status'].apply(has_passed_third_reading)
    df['sponsor_key'] = df['primary_sponsor_name'].apply(normalize_house_sponsor_name)
    sponsor_table = load_bill_sponsors_data('House')
    if not sponsor_table.empty:
        sponsor_keys_by_bill = sponsor_table.groupby('bill_id')['sponsor_key'].apply(list).to_dict()
        cosponsor_keys_by_bill = (
            sponsor_table[~sponsor_table['is_primary_bool']]
            .groupby('bill_id')['sponsor_key']
            .apply(list)
            .to_dict()
        )
        cosponsor_details_by_bill = (
            sponsor_table[~sponsor_table['is_primary_bool']]
            .groupby('bill_id')['sponsor_display']
            .apply(lambda values: '; '.join(values))
            .to_dict()
        )
        df['sponsor_keys'] = df['bill_id'].map(sponsor_keys_by_bill).apply(lambda value: value if isinstance(value, list) else [])
        df['cosponsor_keys'] = df['bill_id'].map(cosponsor_keys_by_bill).apply(lambda value: value if isinstance(value, list) else [])
        df['cosponsor_details'] = df['bill_id'].map(cosponsor_details_by_bill).fillna('')
    else:
        df['sponsor_keys'] = df['sponsors_names'].apply(house_sponsor_keys_from_names)
        df['cosponsor_keys'] = df['sponsor_keys'].apply(lambda keys: keys[1:] if len(keys) > 1 else [])
        df['cosponsor_details'] = ''
    return df


@st.cache_data
def load_senate_data():
    path = Path('data/senators_full_joined(in) (1).csv')
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df = df.rename(columns={
        'By (Senator)': 'senator_name',
        'Official Name': 'official_name',
        'State': 'state',
        'District': 'district',
        'Images': 'image_url'
    })
    if 'image_url' not in df.columns:
        df['image_url'] = ''
    df['image_url'] = df['image_url'].fillna('').astype(str)
    df['senator_key'] = df['senator_name'].apply(normalize_person_name)
    df['official_key'] = df['official_name'].apply(normalize_person_name)
    return df


@st.cache_data
def load_senate_bills_data():
    path = Path('cleaned_hreps_bills_final.xlsx')
    df = pd.read_excel(path, sheet_name='in')
    df.columns = df.columns.str.strip()
    for col in [
        'bill_id',
        'title',
        'date_first_reading',
        'date_second_reading',
        'primary_sponsor_name',
        'sponsors_names',
        'sponsors_full_details',
        'committee'
    ]:
        if col not in df.columns:
            df[col] = ''
        df[col] = df[col].fillna('').astype(str)
    df['first_reading_date'] = parse_bill_date(df['date_first_reading'])
    df['second_reading_date'] = parse_bill_date(df['date_second_reading'])
    df['third_reading_status'] = df['timeline_history'].apply(extract_third_reading_status)
    df['passed_third_reading'] = df['third_reading_status'].apply(has_passed_third_reading)
    df['sponsor_key'] = df['primary_sponsor_name'].apply(normalize_senate_sponsor_name)
    sponsor_table = load_bill_sponsors_data('Senate')
    if not sponsor_table.empty:
        sponsor_keys_by_bill = sponsor_table.groupby('bill_id')['sponsor_key'].apply(list).to_dict()
        cosponsor_keys_by_bill = (
            sponsor_table[~sponsor_table['is_primary_bool']]
            .groupby('bill_id')['sponsor_key']
            .apply(list)
            .to_dict()
        )
        cosponsor_details_by_bill = (
            sponsor_table[~sponsor_table['is_primary_bool']]
            .groupby('bill_id')['sponsor_display']
            .apply(lambda values: '; '.join(values))
            .to_dict()
        )
        df['sponsor_keys'] = df['bill_id'].map(sponsor_keys_by_bill).apply(lambda value: value if isinstance(value, list) else [])
        df['cosponsor_keys'] = df['bill_id'].map(cosponsor_keys_by_bill).apply(lambda value: value if isinstance(value, list) else [])
        df['cosponsor_details'] = df['bill_id'].map(cosponsor_details_by_bill).fillna('')
    else:
        df['sponsor_keys'] = df['sponsors_names'].apply(senate_sponsor_keys_from_names)
        df['cosponsor_keys'] = df['sponsor_keys'].apply(lambda keys: keys[1:] if len(keys) > 1 else [])
        df['cosponsor_details'] = ''
    return df


@st.cache_data
def load_bill_sponsors_data(chamber_type):
    path = Path('plac_10th_assembly_bills_sponsors.csv')
    if not path.exists():
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
    df['sponsor_display'] = df.apply(format_sponsor_table_row, axis=1)
    return df


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


def normalize_house_sponsor_name(name):
    key = normalize_person_name(name)
    return HOUSE_SPONSOR_NAME_MAP.get(key, key)


def house_sponsor_keys_from_names(names):
    keys = []
    for name in str(names).split(';'):
        key = normalize_house_sponsor_name(name)
        if key:
            keys.append(key)
    return keys


SENATE_SPONSOR_NAME_MAP = {
    'ndubueze patrick chiwuba': 'ndubueze patrick chinwuba',
    'yar adua abdulaziz musa': 'abdulaziz yar adua',
    'konbowel benson friday': 'konbowei benson friday',
    'mohammed dandutse muntari': 'dandutse muntari mohammed',
    'dafinone ede omueya': 'omueya dafinone edeh',
    'nwokocha darlington': 'darlington nwokocha',
}


def normalize_senate_sponsor_name(name):
    key = normalize_person_name(name)
    return SENATE_SPONSOR_NAME_MAP.get(key, key)


def senate_sponsor_keys_from_names(names):
    keys = []
    for name in str(names).split(';'):
        key = normalize_senate_sponsor_name(name)
        if key:
            keys.append(key)
    return keys


def paginate_dataframe(df, key_prefix, label):
    page_size = st.selectbox(
        f'{label} per page',
        [10, 25, 50, 100],
        index=1,
        key=f'{key_prefix}_page_size'
    )
    total_pages = max(1, (len(df) + page_size - 1) // page_size)

    if f'{key_prefix}_page' not in st.session_state:
        st.session_state[f'{key_prefix}_page'] = 1
    if st.session_state[f'{key_prefix}_page'] > total_pages:
        st.session_state[f'{key_prefix}_page'] = total_pages

    prev_col, page_col, next_col = st.columns([1, 2, 1])
    with prev_col:
        if st.button('Previous', key=f'{key_prefix}_previous', disabled=st.session_state[f'{key_prefix}_page'] <= 1):
            st.session_state[f'{key_prefix}_page'] -= 1
    with page_col:
        st.write(f"Page {st.session_state[f'{key_prefix}_page']} of {total_pages}")
    with next_col:
        if st.button('Next', key=f'{key_prefix}_next', disabled=st.session_state[f'{key_prefix}_page'] >= total_pages):
            st.session_state[f'{key_prefix}_page'] += 1

    start = (st.session_state[f'{key_prefix}_page'] - 1) * page_size
    end = start + page_size
    return df.iloc[start:end], start, min(end, len(df))


def senator_bills_for_row(row, bills_df):
    keys = {row.get('senator_key', ''), row.get('official_key', '')}
    keys = {key for key in keys if key}
    if not keys:
        return bills_df.iloc[0:0]
    return bills_df[bills_df['sponsor_key'].isin(keys)].copy()


def senator_cosponsored_bills_for_row(row, bills_df):
    keys = {row.get('senator_key', ''), row.get('official_key', '')}
    keys = {key for key in keys if key}
    if not keys or 'cosponsor_keys' not in bills_df.columns:
        return bills_df.iloc[0:0]
    mask = bills_df['cosponsor_keys'].apply(lambda sponsor_keys: bool(keys.intersection(set(sponsor_keys))))
    return bills_df[mask].copy()


def extract_third_reading_status(timeline_history):
    match = re.search(r'Third Reading/Concurrence \(([^)]*)\)', str(timeline_history))
    if not match:
        return ''
    return match.group(1).strip()


def has_passed_third_reading(third_reading_status):
    status = str(third_reading_status).strip()
    return bool(status) and status.lower() != 'not started'


def senator_conversion_stats(row, bills_df):
    sponsored_bills = senator_bills_for_row(row, bills_df)
    total = len(sponsored_bills)
    if not total or 'passed_third_reading' not in sponsored_bills.columns:
        return {'total': total, 'passed': 0, 'rate': 0}
    passed = int(sponsored_bills['passed_third_reading'].sum())
    return {'total': total, 'passed': passed, 'rate': round((passed / total) * 100)}


def house_bills_for_row(row, bills_df):
    keys = {row.get('rep_key', ''), row.get('official_key', '')}
    keys = {key for key in keys if key}
    if not keys:
        return bills_df.iloc[0:0]
    return bills_df[bills_df['sponsor_key'].isin(keys)].copy()


def house_cosponsored_bills_for_row(row, bills_df):
    keys = {row.get('rep_key', ''), row.get('official_key', '')}
    keys = {key for key in keys if key}
    if not keys or 'cosponsor_keys' not in bills_df.columns:
        return bills_df.iloc[0:0]
    mask = bills_df['cosponsor_keys'].apply(lambda sponsor_keys: bool(keys.intersection(set(sponsor_keys))))
    return bills_df[mask].copy()


def house_conversion_stats(row, bills_df):
    sponsored_bills = house_bills_for_row(row, bills_df)
    total = len(sponsored_bills)
    if not total or 'passed_third_reading' not in sponsored_bills.columns:
        return {'total': total, 'passed': 0, 'rate': 0}
    passed = int(sponsored_bills['passed_third_reading'].sum())
    return {'total': total, 'passed': passed, 'rate': round((passed / total) * 100)}


def format_date(value):
    if pd.isna(value):
        return 'Not available'
    return value.strftime('%d %b %Y')


def safe_text(value):
    return html.escape(str(value)) if pd.notna(value) else ''


def format_sponsor_table_row(row):
    details = []
    for col in ['sponsor_party', 'sponsor_state', 'sponsor_constituency']:
        value = str(row.get(col, '')).strip()
        if value:
            details.append(value)
    if details:
        return f"{row.get('sponsor_name', '')} ({', '.join(details)})"
    return str(row.get('sponsor_name', ''))


def inject_senate_styles():
    st.markdown(
        """
        <style>
            .senate-card-header {
                position: relative;
                overflow: hidden;
                margin: 0 0 1rem 0;
                padding: 1rem 1.2rem;
                border-radius: 10px;
                background:
                    radial-gradient(circle at 92% 18%, rgba(255,255,255,.35) 0 36px, transparent 37px),
                    radial-gradient(circle at 82% 88%, rgba(255,255,255,.18) 0 58px, transparent 59px),
                    linear-gradient(135deg, #9f1239 0%, #dc2626 50%, #f97316 100%);
                color: white;
                box-shadow: 0 12px 28px rgba(159, 18, 57, .16);
            }
            .senate-summary-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: .9rem;
                margin: 1rem 0 1.2rem 0;
            }
            .senate-summary-tile {
                position: relative;
                overflow: hidden;
                border-radius: 14px;
                padding: 1.05rem 1.15rem;
                min-height: 112px;
                background:
                    radial-gradient(circle at 88% 24%, rgba(255,255,255,.25) 0 34px, transparent 35px),
                    linear-gradient(135deg, #7f1d1d 0%, #b91c1c 48%, #ef4444 100%);
                color: white;
                box-shadow: 0 12px 26px rgba(185, 28, 28, .20);
            }
            .senate-summary-tile:after {
                content: "";
                position: absolute;
                right: -22px;
                bottom: -32px;
                width: 96px;
                height: 96px;
                border: 1px solid rgba(255,255,255,.22);
                border-radius: 24px;
                transform: rotate(18deg);
            }
            .senate-summary-label {
                position: relative;
                display: block;
                color: rgba(255,255,255,.84);
                font-size: .86rem;
                font-weight: 750;
                text-transform: uppercase;
            }
            .senate-summary-value {
                position: relative;
                display: block;
                margin-top: .42rem;
                color: #fff;
                font-size: 2.35rem;
                font-weight: 900;
                line-height: 1;
            }
            .senate-card-header:before {
                content: "";
                position: absolute;
                right: 72px;
                top: -26px;
                width: 92px;
                height: 92px;
                border: 1px solid rgba(255,255,255,.38);
                border-radius: 999px;
            }
            .senate-card-name {
                position: relative;
                margin: 0;
                font-size: 1.45rem;
                font-weight: 800;
                line-height: 1.2;
            }
            .senate-card-subtitle {
                position: relative;
                margin-top: .35rem;
                color: rgba(255,255,255,.88);
                font-size: .92rem;
            }
            .senate-badge-row {
                position: relative;
                display: flex;
                flex-wrap: wrap;
                gap: .45rem;
                margin-top: .85rem;
            }
            .senate-badge {
                border: 1px solid rgba(255,255,255,.36);
                border-radius: 999px;
                padding: .25rem .62rem;
                background: rgba(255,255,255,.14);
                color: white;
                font-size: .82rem;
                font-weight: 650;
            }
            .bill-metric-row {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: .65rem;
                margin: .8rem 0 .5rem 0;
            }
            .bill-metric {
                border: 1px solid #fee2e2;
                border-radius: 10px;
                padding: .75rem .85rem;
                background: linear-gradient(180deg, #fff7f7 0%, #ffffff 100%);
            }
            .bill-metric span {
                display: block;
                color: #7f1d1d;
                font-size: .74rem;
                font-weight: 700;
                text-transform: uppercase;
            }
            .bill-metric strong {
                display: block;
                margin-top: .25rem;
                color: #111827;
                font-size: 1.02rem;
            }
            .conversion-gauge-card {
                display: flex;
                align-items: center;
                gap: 1rem;
                border: 1px solid #fee2e2;
                border-radius: 10px;
                padding: .9rem 1rem;
                margin: .8rem 0 .5rem 0;
                background: #fffafa;
            }
            .conversion-gauge {
                position: relative;
                width: 112px;
                height: 112px;
                flex: 0 0 112px;
                border-radius: 50%;
                background: conic-gradient(#dc2626 0 var(--conversion), #fee2e2 var(--conversion) 360deg);
            }
            .conversion-gauge-inner {
                position: absolute;
                inset: 12px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                background: white;
                box-shadow: inset 0 0 0 1px #fee2e2;
            }
            .conversion-gauge-inner strong {
                color: #991b1b;
                font-size: 1.35rem;
                line-height: 1;
            }
            .conversion-gauge-inner span {
                color: #7f1d1d;
                font-size: .74rem;
                font-weight: 800;
                margin-top: .25rem;
            }
            .conversion-gauge-copy strong {
                display: block;
                color: #111827;
                font-size: 1rem;
            }
            .conversion-gauge-copy span {
                display: block;
                color: #7f1d1d;
                font-size: .82rem;
                margin-top: .2rem;
            }
            .performance-grid {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 1rem;
                margin-top: .8rem;
            }
            .top-senator-list {
                display: grid;
                gap: .72rem;
            }
            .top-senator-item {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                border-radius: 999px 28px 28px 999px;
                padding: .78rem .95rem .78rem 1.15rem;
                background: linear-gradient(90deg, #991b1b 0%, #dc2626 58%, #fee2e2 100%);
                box-shadow: 0 8px 18px rgba(185, 28, 28, .13);
            }
            .top-senator-name {
                color: white;
                font-weight: 800;
                font-size: 1rem;
            }
            .top-senator-count {
                min-width: 4.8rem;
                border-radius: 999px;
                padding: .36rem .7rem;
                background: white;
                color: #991b1b;
                text-align: center;
                font-weight: 900;
            }
            @media (max-width: 700px) {
                .senate-summary-grid,
                .performance-grid,
                .bill-metric-row {
                    grid-template-columns: 1fr;
                }
                .conversion-gauge-card {
                    align-items: flex-start;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def inject_house_styles():
    st.markdown(
        """
        <style>
            .house-card-header {
                position: relative;
                overflow: hidden;
                margin: 0 0 1rem 0;
                padding: 1rem 1.2rem;
                border-radius: 10px;
                background:
                    radial-gradient(circle at 92% 18%, rgba(255,255,255,.35) 0 36px, transparent 37px),
                    radial-gradient(circle at 82% 88%, rgba(255,255,255,.18) 0 58px, transparent 59px),
                    linear-gradient(135deg, #065f46 0%, #16a34a 52%, #84cc16 100%);
                color: white;
                box-shadow: 0 12px 28px rgba(22, 163, 74, .16);
            }
            .house-card-header:before {
                content: "";
                position: absolute;
                right: 72px;
                top: -26px;
                width: 92px;
                height: 92px;
                border: 1px solid rgba(255,255,255,.38);
                border-radius: 999px;
            }
            .house-card-name {
                position: relative;
                margin: 0;
                font-size: 1.45rem;
                font-weight: 800;
                line-height: 1.2;
            }
            .house-card-subtitle {
                position: relative;
                margin-top: .35rem;
                color: rgba(255,255,255,.88);
                font-size: .92rem;
            }
            .house-badge-row {
                position: relative;
                display: flex;
                flex-wrap: wrap;
                gap: .45rem;
                margin-top: .85rem;
            }
            .house-badge {
                border: 1px solid rgba(255,255,255,.36);
                border-radius: 999px;
                padding: .25rem .62rem;
                background: rgba(255,255,255,.14);
                color: white;
                font-size: .82rem;
                font-weight: 650;
            }
            .house-detail-panel {
                border: 1px solid #dcfce7;
                border-radius: 10px;
                padding: .85rem 1rem;
                background: linear-gradient(180deg, #f0fdf4 0%, #ffffff 100%);
            }
            .house-summary-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: .9rem;
                margin: 1rem 0 1.2rem 0;
            }
            .house-summary-tile {
                position: relative;
                overflow: hidden;
                border-radius: 14px;
                padding: 1.05rem 1.15rem;
                min-height: 112px;
                background:
                    radial-gradient(circle at 88% 24%, rgba(255,255,255,.25) 0 34px, transparent 35px),
                    linear-gradient(135deg, #064e3b 0%, #15803d 48%, #22c55e 100%);
                color: white;
                box-shadow: 0 12px 26px rgba(21, 128, 61, .18);
            }
            .house-summary-tile:after {
                content: "";
                position: absolute;
                right: -22px;
                bottom: -32px;
                width: 96px;
                height: 96px;
                border: 1px solid rgba(255,255,255,.22);
                border-radius: 24px;
                transform: rotate(18deg);
            }
            .house-summary-label {
                position: relative;
                display: block;
                color: rgba(255,255,255,.84);
                font-size: .86rem;
                font-weight: 750;
                text-transform: uppercase;
            }
            .house-summary-value {
                position: relative;
                display: block;
                margin-top: .42rem;
                color: #fff;
                font-size: 2.35rem;
                font-weight: 900;
                line-height: 1;
            }
            .house-bill-metric-row {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: .65rem;
                margin: .8rem 0 .5rem 0;
            }
            .house-bill-metric {
                border: 1px solid #bbf7d0;
                border-radius: 10px;
                padding: .75rem .85rem;
                background: linear-gradient(180deg, #f0fdf4 0%, #ffffff 100%);
            }
            .house-bill-metric span {
                display: block;
                color: #14532d;
                font-size: .74rem;
                font-weight: 700;
                text-transform: uppercase;
            }
            .house-bill-metric strong {
                display: block;
                margin-top: .25rem;
                color: #111827;
                font-size: 1.02rem;
            }
            .house-conversion-gauge-card {
                display: flex;
                align-items: center;
                gap: 1rem;
                border: 1px solid #bbf7d0;
                border-radius: 10px;
                padding: .9rem 1rem;
                margin: .8rem 0 .5rem 0;
                background: #f8fffb;
            }
            .house-conversion-gauge {
                position: relative;
                width: 112px;
                height: 112px;
                flex: 0 0 112px;
                border-radius: 50%;
                background: conic-gradient(#16a34a 0 var(--conversion), #dcfce7 var(--conversion) 360deg);
            }
            .house-conversion-gauge-inner {
                position: absolute;
                inset: 12px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                background: white;
                box-shadow: inset 0 0 0 1px #bbf7d0;
            }
            .house-conversion-gauge-inner strong {
                color: #065f46;
                font-size: 1.35rem;
                line-height: 1;
            }
            .house-conversion-gauge-inner span {
                color: #14532d;
                font-size: .74rem;
                font-weight: 800;
                margin-top: .25rem;
            }
            .house-conversion-gauge-copy strong {
                display: block;
                color: #111827;
                font-size: 1rem;
            }
            .house-conversion-gauge-copy span {
                display: block;
                color: #14532d;
                font-size: .82rem;
                margin-top: .2rem;
            }
            .top-house-list {
                display: grid;
                gap: .72rem;
            }
            .top-house-item {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 1rem;
                border-radius: 999px 28px 28px 999px;
                padding: .78rem .95rem .78rem 1.15rem;
                background: linear-gradient(90deg, #065f46 0%, #16a34a 58%, #dcfce7 100%);
                box-shadow: 0 8px 18px rgba(21, 128, 61, .13);
            }
            .top-house-name {
                color: white;
                font-weight: 800;
                font-size: 1rem;
            }
            .top-house-count {
                min-width: 4.8rem;
                border-radius: 999px;
                padding: .36rem .7rem;
                background: white;
                color: #065f46;
                text-align: center;
                font-weight: 900;
            }
            @media (max-width: 700px) {
                .house-summary-grid,
                .house-bill-metric-row,
                .performance-grid {
                    grid-template-columns: 1fr;
                }
                .house-conversion-gauge-card {
                    align-items: flex-start;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_senate_card_header(row, bill_count):
    st.markdown(
        f"""
        <div class="senate-card-header">
            <div class="senate-card-name">{safe_text(row.get('senator_name', row.get('official_name', 'Unknown')))}</div>
            <div class="senate-card-subtitle">{safe_text(row.get('official_name', ''))}</div>
            <div class="senate-badge-row">
                <span class="senate-badge">{safe_text(row.get('state', ''))}</span>
                <span class="senate-badge">{safe_text(row.get('district', ''))}</span>
                <span class="senate-badge">{bill_count} linked bills</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_senate_conversion_gauge(stats):
    rate = int(stats.get('rate', 0))
    passed = int(stats.get('passed', 0))
    total = int(stats.get('total', 0))
    degrees = max(0, min(rate, 100)) * 3.6
    st.markdown(
        f"""
        <div class="conversion-gauge-card">
            <div class="conversion-gauge" style="--conversion: {degrees:.1f}deg;" aria-label="Third reading conversion rate {rate}%">
                <div class="conversion-gauge-inner">
                    <strong>{rate}%</strong>
                    <span>{passed}/{total}</span>
                </div>
            </div>
            <div class="conversion-gauge-copy">
                <strong>Third reading conversion</strong>
                <span>Sponsored bills that reached Third Reading/Concurrence.</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_house_card_header(row, bill_count):
    st.markdown(
        f"""
        <div class="house-card-header">
            <div class="house-card-name">{safe_text(row.get('rep_name', row.get('official_name', 'Unknown')))}</div>
            <div class="house-card-subtitle">{safe_text(row.get('official_name', ''))}</div>
            <div class="house-badge-row">
                <span class="house-badge">{safe_text(row.get('state', ''))}</span>
                <span class="house-badge">{safe_text(row.get('constituency', ''))}</span>
                <span class="house-badge">Rep ID {safe_text(row.get('RepID', ''))}</span>
                <span class="house-badge">{bill_count} linked bills</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_house_summary_tiles(members_shown, linked_bills, members_with_bills):
    st.markdown(
        f"""
        <div class="house-summary-grid">
            <div class="house-summary-tile">
                <span class="house-summary-label">Members shown</span>
                <span class="house-summary-value">{members_shown}</span>
            </div>
            <div class="house-summary-tile">
                <span class="house-summary-label">Linked bills</span>
                <span class="house-summary-value">{linked_bills}</span>
            </div>
            <div class="house-summary-tile">
                <span class="house-summary-label">Members with bills</span>
                <span class="house-summary-value">{members_with_bills}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_house_conversion_gauge(stats):
    rate = int(stats.get('rate', 0))
    passed = int(stats.get('passed', 0))
    total = int(stats.get('total', 0))
    degrees = max(0, min(rate, 100)) * 3.6
    st.markdown(
        f"""
        <div class="house-conversion-gauge-card">
            <div class="house-conversion-gauge" style="--conversion: {degrees:.1f}deg;" aria-label="Third reading conversion rate {rate}%">
                <div class="house-conversion-gauge-inner">
                    <strong>{rate}%</strong>
                    <span>{passed}/{total}</span>
                </div>
            </div>
            <div class="house-conversion-gauge-copy">
                <strong>Third reading conversion</strong>
                <span>Sponsored bills that reached Third Reading/Concurrence.</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_senate_summary_tiles(senators_shown, linked_bills, senators_with_bills):
    st.markdown(
        f"""
        <div class="senate-summary-grid">
            <div class="senate-summary-tile">
                <span class="senate-summary-label">Senators shown</span>
                <span class="senate-summary-value">{senators_shown}</span>
            </div>
            <div class="senate-summary-tile">
                <span class="senate-summary-label">Linked bills</span>
                <span class="senate-summary-value">{linked_bills}</span>
            </div>
            <div class="senate-summary-tile">
                <span class="senate-summary-label">Senators with bills</span>
                <span class="senate-summary-value">{senators_with_bills}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_senator_bill_details(row, bills_df):
    senator_bills = senator_bills_for_row(row, bills_df)
    cosponsored_bills = senator_cosponsored_bills_for_row(row, bills_df)
    bill_count = len(senator_bills)
    cosponsored_count = len(cosponsored_bills)
    linked_count = bill_count + cosponsored_count

    all_linked_bills = pd.concat([senator_bills, cosponsored_bills], ignore_index=True)
    if linked_count:
        first_bill_date = format_date(all_linked_bills['first_reading_date'].min())
        latest_bill_date = format_date(all_linked_bills['first_reading_date'].max())
    else:
        first_bill_date = 'None'
        latest_bill_date = 'None'

    st.markdown(
        f"""
        <div class="bill-metric-row">
            <div class="bill-metric"><span>Bills sponsored</span><strong>{bill_count}</strong></div>
            <div class="bill-metric"><span>Co-sponsored bills</span><strong>{cosponsored_count}</strong></div>
            <div class="bill-metric"><span>First bill date</span><strong>{first_bill_date}</strong></div>
            <div class="bill-metric"><span>Latest bill date</span><strong>{latest_bill_date}</strong></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    render_senate_conversion_gauge(senator_conversion_stats(row, bills_df))

    if not linked_count:
        st.info('No linked Senate bills found for this senator yet.')
        return

    if bill_count:
        display_bills = senator_bills.sort_values('first_reading_date', ascending=False)
        with st.expander(f'View {bill_count} sponsored bill details'):
            for _, bill in display_bills.iterrows():
                st.markdown(f"**{bill.get('title', '')}**")
                bill_cols = st.columns(4)
                bill_cols[0].caption(f"Bill ID: {bill.get('bill_id', '')}")
                bill_cols[1].caption(f"First Reading: {format_date(bill.get('first_reading_date'))}")
                bill_cols[2].caption(f"Second Reading: {format_date(bill.get('second_reading_date'))}")
                bill_cols[3].caption(f"Committee: {bill.get('committee', '') or 'Not Yet Referred'}")
                st.caption(f"Third Reading/Concurrence: {bill.get('third_reading_status', '') or 'Not Started'}")
                st.caption(f"Primary sponsor: {bill.get('primary_sponsor_name', '')}")
                cosponsor_details = bill.get('cosponsor_details', '') or bill.get('sponsors_full_details', '')
                if cosponsor_details:
                    st.caption(f"Co-sponsor details: {cosponsor_details}")
                st.markdown('---')

    if cosponsored_count:
        display_bills = cosponsored_bills.sort_values('first_reading_date', ascending=False)
        with st.expander(f'View {cosponsored_count} co-sponsored bill details'):
            for _, bill in display_bills.iterrows():
                st.markdown(f"**{bill.get('title', '')}**")
                bill_cols = st.columns(4)
                bill_cols[0].caption(f"Bill ID: {bill.get('bill_id', '')}")
                bill_cols[1].caption(f"First Reading: {format_date(bill.get('first_reading_date'))}")
                bill_cols[2].caption(f"Second Reading: {format_date(bill.get('second_reading_date'))}")
                bill_cols[3].caption(f"Committee: {bill.get('committee', '') or 'Not Yet Referred'}")
                st.caption(f"Third Reading/Concurrence: {bill.get('third_reading_status', '') or 'Not Started'}")
                st.caption(f"Primary sponsor: {bill.get('primary_sponsor_name', '')}")
                cosponsor_details = bill.get('cosponsor_details', '') or bill.get('sponsors_full_details', '')
                if cosponsor_details:
                    st.caption(f"Co-sponsor details: {cosponsor_details}")
                st.markdown('---')


def show_house_bill_details(row, bills_df):
    house_bills = house_bills_for_row(row, bills_df)
    cosponsored_bills = house_cosponsored_bills_for_row(row, bills_df)
    bill_count = len(house_bills)
    cosponsored_count = len(cosponsored_bills)
    linked_count = bill_count + cosponsored_count

    all_linked_bills = pd.concat([house_bills, cosponsored_bills], ignore_index=True)
    if linked_count:
        first_bill_date = format_date(all_linked_bills['first_reading_date'].min())
        latest_bill_date = format_date(all_linked_bills['first_reading_date'].max())
    else:
        first_bill_date = 'None'
        latest_bill_date = 'None'

    st.markdown(
        f"""
        <div class="house-bill-metric-row">
            <div class="house-bill-metric"><span>Bills sponsored</span><strong>{bill_count}</strong></div>
            <div class="house-bill-metric"><span>Co-sponsored bills</span><strong>{cosponsored_count}</strong></div>
            <div class="house-bill-metric"><span>First bill date</span><strong>{first_bill_date}</strong></div>
            <div class="house-bill-metric"><span>Latest bill date</span><strong>{latest_bill_date}</strong></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    render_house_conversion_gauge(house_conversion_stats(row, bills_df))

    if not linked_count:
        st.info('No linked House bills found for this member yet.')
        return

    if bill_count:
        display_bills = house_bills.sort_values('first_reading_date', ascending=False)
        with st.expander(f'View {bill_count} sponsored bill details'):
            for _, bill in display_bills.iterrows():
                st.markdown(f"**{bill.get('title', '')}**")
                bill_cols = st.columns(4)
                bill_cols[0].caption(f"Bill ID: {bill.get('bill_id', '')}")
                bill_cols[1].caption(f"First Reading: {format_date(bill.get('first_reading_date'))}")
                bill_cols[2].caption(f"Second Reading: {format_date(bill.get('second_reading_date'))}")
                bill_cols[3].caption(f"Committee: {bill.get('committee', '') or 'Not Yet Referred'}")
                st.caption(f"Third Reading/Concurrence: {bill.get('third_reading_status', '') or 'Not Started'}")
                st.caption(f"Primary sponsor: {bill.get('primary_sponsor_name', '')}")
                cosponsor_details = bill.get('cosponsor_details', '') or bill.get('sponsors_full_details', '')
                if cosponsor_details:
                    st.caption(f"Co-sponsor details: {cosponsor_details}")
                st.markdown('---')

    if cosponsored_count:
        display_bills = cosponsored_bills.sort_values('first_reading_date', ascending=False)
        with st.expander(f'View {cosponsored_count} co-sponsored bill details'):
            for _, bill in display_bills.iterrows():
                st.markdown(f"**{bill.get('title', '')}**")
                bill_cols = st.columns(4)
                bill_cols[0].caption(f"Bill ID: {bill.get('bill_id', '')}")
                bill_cols[1].caption(f"First Reading: {format_date(bill.get('first_reading_date'))}")
                bill_cols[2].caption(f"Second Reading: {format_date(bill.get('second_reading_date'))}")
                bill_cols[3].caption(f"Committee: {bill.get('committee', '') or 'Not Yet Referred'}")
                st.caption(f"Third Reading/Concurrence: {bill.get('third_reading_status', '') or 'Not Started'}")
                st.caption(f"Primary sponsor: {bill.get('primary_sponsor_name', '')}")
                cosponsor_details = bill.get('cosponsor_details', '') or bill.get('sponsors_full_details', '')
                if cosponsor_details:
                    st.caption(f"Co-sponsor details: {cosponsor_details}")
                st.markdown('---')


def senator_bill_count(row, bills_df):
    return len(senator_bills_for_row(row, bills_df))


def senator_linked_bill_count(row, bills_df):
    return len(senator_bills_for_row(row, bills_df)) + len(senator_cosponsored_bills_for_row(row, bills_df))


def house_linked_bill_count(row, bills_df):
    return len(house_bills_for_row(row, bills_df)) + len(house_cosponsored_bills_for_row(row, bills_df))


def show_top_house_summary(house_df, bills_df):
    if house_df.empty:
        return

    summary_rows = []
    for _, row in house_df.iterrows():
        bill_count = house_linked_bill_count(row, bills_df)
        if bill_count:
            summary_rows.append({
                'rep_name': row.get('rep_name', row.get('official_name', 'Unknown')),
                'Bills': bill_count
            })

    if not summary_rows:
        st.markdown('### House Performance Summary by Linked Bills')
        st.info('No linked bill counts available for the House summary.')
        return

    summary_df = (
        pd.DataFrame(summary_rows)
        .groupby('rep_name', as_index=False)['Bills']
        .sum()
    )

    top_df = summary_df.sort_values('Bills', ascending=False).head(20)
    least_df = summary_df.sort_values('Bills', ascending=True).head(20)

    st.markdown('### House Performance Summary by Linked Bills')
    st.caption('This summary uses all House bill records and includes sponsored plus co-sponsored bill links.')

    top_col, least_col = st.columns(2)
    with top_col:
        st.markdown('#### Top 20')
        st.markdown('<div class="top-house-list">', unsafe_allow_html=True)
        for _, row in top_df.iterrows():
            st.markdown(
                f"""
                <div class="top-house-item">
                    <span class="top-house-name">{safe_text(row['rep_name'])}</span>
                    <span class="top-house-count">{int(row['Bills'])} bills</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with least_col:
        st.markdown('#### Least 20')
        st.markdown('<div class="top-house-list">', unsafe_allow_html=True)
        for _, row in least_df.iterrows():
            st.markdown(
                f"""
                <div class="top-house-item">
                    <span class="top-house-name">{safe_text(row['rep_name'])}</span>
                    <span class="top-house-count">{int(row['Bills'])} bills</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)


def show_top_senators_summary(senate_df, bills_df):
    if senate_df.empty:
        return

    key_to_name = {}
    for _, row in senate_df.iterrows():
        display_name = row.get('senator_name', row.get('official_name', 'Unknown'))
        for key in [row.get('senator_key', ''), row.get('official_key', '')]:
            if key:
                key_to_name[key] = display_name

    counts = bills_df['sponsor_key'].value_counts()
    summary_rows = []
    for sponsor_key, count in counts.items():
        if sponsor_key in key_to_name:
            summary_rows.append({
                'senator_name': key_to_name[sponsor_key],
                'Bills': count
            })

    if not summary_rows:
        st.markdown('### Top 15 Performing Senators by Bills Sponsored')
        st.info('No linked bill counts available for the Senate summary.')
        return

    summary_df = (
        pd.DataFrame(summary_rows)
        .groupby('senator_name', as_index=False)['Bills']
        .sum()
    )

    top_df = summary_df.sort_values('Bills', ascending=False).head(20)
    least_df = summary_df.sort_values('Bills', ascending=True).head(20)

    st.markdown('### Senate Performance Summary by Bills Sponsored')
    st.caption('This summary uses all Senate bill records and does not change when sidebar filters are selected.')

    top_col, least_col = st.columns(2)
    with top_col:
        st.markdown('#### Top 20')
        st.markdown('<div class="top-senator-list">', unsafe_allow_html=True)
        for _, row in top_df.iterrows():
            st.markdown(
                f"""
                <div class="top-senator-item">
                    <span class="top-senator-name">{safe_text(row['senator_name'])}</span>
                    <span class="top-senator-count">{int(row['Bills'])} bills</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

    with least_col:
        st.markdown('#### Least 20')
        st.markdown('<div class="top-senator-list">', unsafe_allow_html=True)
        for _, row in least_df.iterrows():
            st.markdown(
                f"""
                <div class="top-senator-item">
                    <span class="top-senator-name">{safe_text(row['senator_name'])}</span>
                    <span class="top-senator-count">{int(row['Bills'])} bills</span>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)


st.set_page_config(page_title='National Assembly Dashboard', layout='wide')

chamber = st.sidebar.radio('Select chamber', ['House of Reps', 'Senate'])
st.sidebar.markdown('---')

if chamber == 'House of Reps':
    inject_house_styles()
    st.title('House of Representatives Members Dashboard')
    st.write('Browse House of Representatives members with their details and images from the master House dataset.')

    house_data_path = Path('data/house_of_reps_master_final.xlsx')
    house_df = load_house_data(house_data_path.stat().st_mtime)
    house_bills_df = load_house_bills_data()

    states = ['All'] + sorted(house_df['state'].dropna().astype(str).unique().tolist())
    constituencies = ['All'] + sorted(house_df['constituency'].dropna().astype(str).unique().tolist())
    rep_names = ['All'] + sorted(house_df['rep_name'].dropna().astype(str).unique().tolist())

    selected_state = st.sidebar.selectbox('Filter by state', states, key='house_state_filter')
    selected_constituency = st.sidebar.selectbox('Filter by constituency', constituencies, key='house_constituency_filter')
    selected_rep = st.sidebar.selectbox('Filter by House member', rep_names, key='house_member_filter')
    st.sidebar.markdown('---')
    st.sidebar.write('Use the filters above to narrow the member list.')

    filtered = house_df.copy()
    if selected_state != 'All':
        filtered = filtered[filtered['state'] == selected_state]
    if selected_constituency != 'All':
        filtered = filtered[filtered['constituency'] == selected_constituency]
    if selected_rep != 'All':
        filtered = filtered[filtered['rep_name'] == selected_rep]

    if filtered.empty:
        st.warning('No members found for the selected filters.')
    else:
        linked_bill_count = 0
        linked_member_count = 0
        for _, summary_row in filtered.iterrows():
            member_linked_count = house_linked_bill_count(summary_row, house_bills_df)
            linked_bill_count += member_linked_count
            if member_linked_count:
                linked_member_count += 1

        render_house_summary_tiles(len(filtered), linked_bill_count, linked_member_count)

        page_df, start, end = paginate_dataframe(filtered, 'house', 'Members')
        st.write(f'**Showing members {start + 1}-{end} of {len(filtered)}**')
        for _, row in page_df.iterrows():
            member_bill_count = house_linked_bill_count(row, house_bills_df)
            with st.container(border=True):
                render_house_card_header(row, member_bill_count)
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(
                        f"""
                        <div class="house-detail-panel">
                            <p><strong>Official Name:</strong> {safe_text(row.get('official_name', ''))}</p>
                            <p><strong>Constituency:</strong> {safe_text(row.get('constituency', ''))}</p>
                            <p><strong>State:</strong> {safe_text(row.get('state', ''))}</p>
                            <p><strong>Rep ID:</strong> {safe_text(row.get('RepID', ''))}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    show_house_bill_details(row, house_bills_df)
                with col2:
                    image_url = row.get('image_url', '')
                    if image_url and str(image_url).strip():
                        img_str = str(image_url).strip()
                        try:
                            if img_str.startswith('data:') and 'base64,' in img_str:
                                # data URI: data:[<mediatype>][;base64],<data>
                                b64 = img_str.split('base64,', 1)[1]
                                img_bytes = base64.b64decode(b64)
                                st.image(img_bytes, caption=row.get('rep_name', ''), width='stretch')
                            elif img_str.startswith('http'):
                                st.image(img_str, caption=row.get('rep_name', ''), width='stretch')
                            else:
                                # fallback: try to decode if it looks like raw base64
                                if all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\n\r' for c in img_str[:50]):
                                    try:
                                        img_bytes = base64.b64decode(img_str)
                                        st.image(img_bytes, caption=row.get('rep_name', ''), width='stretch')
                                    except Exception:
                                        st.write('Image not available')
                                else:
                                    st.write('No valid image URL provided')
                        except Exception:
                            st.write('Image not available')
                    else:
                        st.write('No image URL provided')

    show_top_house_summary(house_df, house_bills_df)

else:
    inject_senate_styles()
    st.title('Senate Members Dashboard')
    st.write('Browse Senate members with their details, images, and linked bill sponsorship records.')

    senate_df = load_senate_data()
    senate_bills_df = load_senate_bills_data()

    states = ['All'] + sorted(senate_df['state'].dropna().astype(str).unique().tolist())
    districts = ['All'] + sorted(senate_df['district'].dropna().astype(str).unique().tolist())
    senator_names = ['All'] + sorted(senate_df['senator_name'].dropna().astype(str).unique().tolist())

    selected_state = st.sidebar.selectbox('Filter by state', states, key='senate_state_filter')
    selected_district = st.sidebar.selectbox('Filter by district', districts, key='senate_district_filter')
    selected_senator = st.sidebar.selectbox('Filter by senator', senator_names, key='senate_member_filter')
    if st.sidebar.button('Clear Senate filters'):
        st.session_state['senate_state_filter'] = 'All'
        st.session_state['senate_district_filter'] = 'All'
        st.session_state['senate_member_filter'] = 'All'
        st.rerun()
    st.sidebar.markdown('---')
    st.sidebar.write('Use the filters above to narrow the senator list.')

    filtered_senate = senate_df.copy()
    if selected_state != 'All':
        filtered_senate = filtered_senate[filtered_senate['state'] == selected_state]
    if selected_district != 'All':
        filtered_senate = filtered_senate[filtered_senate['district'] == selected_district]
    if selected_senator != 'All':
        filtered_senate = filtered_senate[filtered_senate['senator_name'] == selected_senator]

    if filtered_senate.empty:
        st.warning('No senators found for the selected filters.')
    else:
        linked_bill_count = 0
        linked_senator_count = 0
        for _, summary_row in filtered_senate.iterrows():
            senator_linked_count = senator_linked_bill_count(summary_row, senate_bills_df)
            linked_bill_count += senator_linked_count
            if senator_linked_count:
                linked_senator_count += 1

        render_senate_summary_tiles(len(filtered_senate), linked_bill_count, linked_senator_count)

        page_df, start, end = paginate_dataframe(filtered_senate, 'senate', 'Senators')
        st.write(f'**Showing senators {start + 1}-{end} of {len(filtered_senate)}**')
        for _, row in page_df.iterrows():
            senator_bill_count = senator_linked_bill_count(row, senate_bills_df)
            with st.container(border=True):
                render_senate_card_header(row, senator_bill_count)
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**Senator ID:** {row.get('SenatorID', '')}")
                    show_senator_bill_details(row, senate_bills_df)
                with col2:
                    image_url = row.get('image_url', '')
                    if image_url and str(image_url).strip():
                        img_str = str(image_url).strip()
                        try:
                            if img_str.startswith('data:') and 'base64,' in img_str:
                                # data URI: data:[<mediatype>][;base64],<data>
                                b64 = img_str.split('base64,', 1)[1]
                                img_bytes = base64.b64decode(b64)
                                st.image(img_bytes, caption=row.get('senator_name', ''), width='stretch')
                            elif img_str.startswith('http'):
                                st.image(img_str, caption=row.get('senator_name', ''), width='stretch')
                            else:
                                # fallback: try to decode if it looks like raw base64
                                if all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\n\r' for c in img_str[:50]):
                                    try:
                                        img_bytes = base64.b64decode(img_str)
                                        st.image(img_bytes, caption=row.get('senator_name', ''), width='stretch')
                                    except Exception:
                                        st.write('Image not available')
                                else:
                                    st.write('No valid image URL provided')
                        except Exception:
                            st.write('Image not available')
                    else:
                        st.write('No image URL provided')

    show_top_senators_summary(senate_df, senate_bills_df)
