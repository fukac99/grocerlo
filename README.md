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

The frontend is a Next.js visual inspection shell that currently uses static
mock data only. It is not connected to live scraper output or backend APIs yet.

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
