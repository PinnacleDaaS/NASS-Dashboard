# NASS Dashboard

Interactive dashboard of Nigeria's 10th National Assembly: members, photos, parties, and tracked bills (sourced from PLAC). Live view, search, filtering by chamber/party, bill details, and an embed mode for iframes.

## Structure

```
frontend/   Vite + React 19 + TypeScript + Tailwind 4 app
pipeline/   Python data pipeline (PLAC scrape -> clean -> export -> validate)
data/       Pipeline inputs/outputs (CSVs, xlsx, scraper cache)
.github/    Weekly auto-update workflow (Tue 03:00 UTC)
```

## Frontend

```bash
cd frontend
npm install
npm run dev      # local dev server
npm run build    # typecheck + production build (tsc && vite build)
npm run lint     # ESLint (zero warnings)
npm run preview  # preview the production build
```

The app reads static JSON from `frontend/public/data/`:

- `house.json` — 375 House of Representatives members
- `senate.json` — 119 Senators
- `legislator_images/` — member photos named by slug (`sen_*.jpg`, `rep_*.jpg`)

Append `?embed=1` to the URL for a clean iframe-friendly embed (used by the NASSTrack toolbar).

## Data pipeline

```bash
py -m pip install -r pipeline/requirements.txt
py pipeline/run_pipeline.py     # runs all four steps below
```

Steps (in order):

1. `scrape_plac_bills.py` — fetch PLAC bills API (resumable cache at `data/temp_bills_cache.json`)
2. `clean_plac_bills.py` — normalize bill records into CSVs
3. `export_data.py` — build `house.json` / `senate.json` with member photos and parties
4. `validate_pipeline.py` — integrity checks on counts, images, and party coverage

### Member data

- Members come from PLAC's master spreadsheets plus the PLAC members API fallback.
- Photos are resolved slug-first from `legislator_images/`; the slug derives from the member's normalized name (`member_image_slug` in `export_data.py`).
- Parties come from the PLAC API with a manual override layer — `PARTY_OVERRIDES` in `export_data.py` — for members who changed parties during the 10th Assembly (2025-2026 defections are researched and pinned there, including corrections of stale PLAC data, e.g. El-Rasheed Abdullahi and David Fuoh).

### Known roster caveats

- "Vacant" is a placeholder seat and will never have a party or photo.
- The PLAC members API caps around 470 records; members missing from it are backfilled via the party lookup and overrides.
- A few members listed on PLAC are no longer serving (e.g. deceased or defected members) — their rows are preserved as-is.

## Deployment

- Vercel auto-deploys the `frontend/` directory on push to `main`.
- `.github/workflows/pipeline.yml` runs the pipeline weekly (Tuesdays 03:00 UTC) and commits updated data back to `main`, triggering a redeploy. It can also be triggered manually via the Actions tab.
