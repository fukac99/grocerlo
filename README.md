# Grocery Saver

Lightweight supermarket price comparison app for Germany, Austria, and Slovakia.

See `PRICE_COMPARISON_APP_PLAN.md` for the product plan and `LOOP_STATE.md` for current loop progress.

## Local Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install backend dependencies:

```bash
python -m pip install -e "backend[dev]"
python -m playwright install chromium
```

Start Postgres:

```bash
docker compose up -d postgres
```

Docker Desktop or another Docker daemon must be running before starting the service. The
compose database uses the default local app URL:
`postgresql+asyncpg://grocery_saver:grocery_saver@localhost:5432/grocery_saver`.

Run migrations:

```bash
cd backend
alembic upgrade head
```

## Frontend Visual Shell

The frontend is a Next.js visual inspection shell that loads normalized BILLA
products from the local backend by default. Explicit sample mode is still
available for UI-only checks.

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 to view the searchable comparison table.

## Scraper Dry Run

Dry runs print JSON and do not write to the database:

```bash
python scripts/scrape_once.py --retailer billa --limit-categories 1 --max-products 3
```

REWE is approved only for a no-storage low-volume dry run using the recorded
`65510 Idstein-Wörsdorf` context:

```bash
python scripts/scrape_once.py --retailer rewe --limit-categories 1 --max-products 3
```

Store raw products in Postgres:

```bash
python scripts/scrape_once.py --retailer billa --limit-categories 1 --max-products 3 --store
```

For a low-volume validation run, keep the store command to one category and no more than
three products. A successful stored run prints the created `scrape_run_id` and the raw
product count.

Summarize the latest stored BILLA run:

```bash
python scripts/stored_data_sanity_report.py
```

Inspect a specific stored run:

```bash
python scripts/stored_data_sanity_report.py --scrape-run-id 1
```

The sanity report prints counts for raw rows, missing fields, duplicate source product IDs,
suspicious prices/unit prices, and row identifiers for inspecting bad records. If the
database is unavailable, start Postgres and rerun migrations before running the report.

## Controlled BILLA Full Ingest

Read `docs/retailer-ingest-runbook.md` before any stored or broad retailer
ingest. It records current retailer readiness, required approvals, conservative
limits, stop conditions, cleanup steps, and MPREIS report-only validation status.

Use `scripts/billa_full_ingest.py` when an operator intentionally wants a broader BILLA
raw ingest. The command is safe by default: it runs as a dry run, scrapes one category,
caps output at 10 products, waits between category requests, and prints a run summary
with quality checks.

```bash
python scripts/billa_full_ingest.py
```

Any multi-category or unlimited run requires the explicit confirmation token
`BILLA_FULL_INGEST`. Store a capped two-category validation run:

```bash
python scripts/billa_full_ingest.py \
  --store \
  --limit-categories 2 \
  --max-products 50 \
  --delay-seconds 2 \
  --confirm-broad-run BILLA_FULL_INGEST
```

Run the full stored workflow only after confirming that broad BILLA scraping is approved:

```bash
python scripts/billa_full_ingest.py \
  --store \
  --all-categories \
  --max-products 0 \
  --delay-seconds 2 \
  --confirm-broad-run BILLA_FULL_INGEST
```

Resume with one of `--start-category-index`, `--resume-after-source-id`, or
`--resume-after-name`. Stored runs print a `scrape_run_id` and embed the same sanity
report output produced by `scripts/stored_data_sanity_report.py`; dry runs include a
small product sample plus quality issue counts without writing to Postgres.
