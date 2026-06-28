# Grocery Saver Loop State

This file is the persistent memory for loop-style work on the grocery price comparison app. Future agent runs should read this file together with `PRICE_COMPARISON_APP_PLAN.md` before choosing the next task.

## Current Focus

BILLA Austria scraper MVP.

## Project Mode

Automatic builder loop every 10 minutes. Do not run recurring scrapes yet.

Loop coordination uses `LOOP_TASKS.md` as the task ledger and lightweight lock file. Tasks must be moved to `In Progress` before local work or subagent launch.

Each implementation task should use its own branch and open a GitHub pull request against `https://github.com/fukac99/grocerlo`. The repository connection task should run before other ready tasks that need pull requests.

Every loop run should check existing task pull requests and update `pr_status` plus `pr_last_checked` in `LOOP_TASKS.md`. Downstream tasks should treat prior PR-backed dependencies as complete only after their pull requests are merged.

## Retailer Status

| Retailer | Country | Status | Notes |
| --- | --- | --- | --- |
| BILLA | AT | Next | Best first target. Category listing exposes product cards, prices, unit prices, promotions, and pagination. |
| MPREIS | AT | Not started | Needs distinction between regular prices, app-only promotions, and store availability. |
| REWE | DE | Not started | May require selected delivery or pickup market. Store or region context must be recorded. |
| Kaufland | SK | Not started | Needs discovery to determine product listing and price availability. |
| Tesco | SK | Not started | Likely dynamic. May require Playwright and location/session setup. |

## Last Run

2026-06-28 automatic builder loop, coordinator pass:

- Armed the automatic 30-minute loop.
- Added `LOOP_TASKS.md` as the coordination ledger and task lock file.
- Claimed T001 for environment setup and T004 for normalization utilities.
- T004 completed: added Decimal-based EUR price, package size, and unit price normalization utilities with pytest coverage.
- T001 completed: local backend environment, dependencies, and Playwright Chromium are installed; required imports passed.
- A low-volume BILLA dry scrape ran successfully with 1 category and 3 products.

2026-06-27 manual builder loop, iteration 2:

- Added BILLA scraper implementation with category discovery and low-volume product extraction.
- Added `scripts/scrape_once.py` one-off scraper CLI.
- CLI defaults to JSON dry-run output and only writes to Postgres when `--store` is passed.
- Added lazy DB imports so dry-run mode does not require database dependencies or a running database.
- Added `README.md` with local setup, migration, dry-run, and store commands.
- Ran `python3 -m compileall -q backend/app scripts`.
- Checked editor diagnostics for touched scraper and CLI files; no linter errors found.
- Tried `python3 scripts/scrape_once.py --retailer billa --limit-categories 1 --max-products 3`; runtime is currently blocked because local scraper dependencies are not installed (`beautifulsoup4` provides `bs4`).

Previous run:

- Added backend and database skeleton.
- Added PostgreSQL Docker Compose service.
- Added FastAPI health endpoint.
- Added SQLAlchemy models for `scrape_runs`, `raw_products`, `retailer_products`, `canonical_products`, and `product_matches`.
- Added Alembic configuration and initial schema migration.
- Added shared scraper interface with `Category`, `RawProductPayload`, and `RetailerScraper`.
- Ran `python3 -m compileall -q backend/app backend/alembic`.
- Checked editor diagnostics for touched files; no linter errors found.

## Current Assumptions

- One-off scraping comes before recurring scheduling.
- Raw scraped data should be stored before normalization.
- Scrapers should extract source data, not fully interpret it.
- Product reconciliation should start with explainable rule-based matching.
- Low-volume scraping is preferred while site behavior and terms are being evaluated.

## Open Questions

- Do any target retailers require a selected market before prices are available?
- Which retailers expose stable source product IDs?
- Which fields are visible without login or account-specific context?
- How should app-only promotions be represented in comparisons?
- Should the first UI compare unmatched retailer products, matched canonical products, or both?

## Next Actions

1. Use `LOOP_TASKS.md` to claim eligible `Ready` tasks.
2. Connect this local project to `https://github.com/fukac99/grocerlo` and establish the branch/PR workflow.
3. Inspect the BILLA dry-scrape sample output for product plausibility.
4. If the dry run returns plausible products, start Postgres, run migrations, and test `--store`.
5. Add a simple data quality check for missing names, missing prices, duplicate source IDs, and suspicious unit prices.

## Loop Log

### 2026-06-27

- Created `PRICE_COMPARISON_APP_PLAN.md`.
- Created this loop state file.
- Ran the first manual builder loop.
- Added the backend/database skeleton, initial schema migration, shared scraper interface, and local PostgreSQL Compose service.
- Verified Python syntax with `python3 -m compileall -q backend/app backend/alembic`.
- Checked editor diagnostics for touched files; no linter errors found.
- Current recommended next step is BILLA category discovery and low-volume raw product extraction.
- Ran the second manual builder loop.
- Added BILLA scraper discovery/extraction code and the `scripts/scrape_once.py` CLI.
- Added `README.md` with environment setup and scraper commands.
- Verified Python syntax with `python3 -m compileall -q backend/app scripts`.
- Checked editor diagnostics for touched scraper and CLI files; no linter errors found.
- BILLA dry-run execution is blocked until backend dependencies and Playwright Chromium are installed.
- Added `LOOP_TASKS.md` as the task ledger and lightweight lock file for automated loop coordination.
- Updated loop instructions to support a 30-minute automated builder loop and parallel subagents for independent claimed tasks.

### 2026-06-28

- Armed the automatic 30-minute builder loop.
- Added and started using `LOOP_TASKS.md` as the task ledger and lock file.
- T004 completed with price, package size, and unit price normalization utilities plus tests.
- T001 completed with backend dependencies installed, Playwright Chromium installed, required imports verified, and a successful low-volume BILLA dry scrape.
- Added T006 to connect the project to `https://github.com/fukac99/grocerlo`.
- Updated loop rules so future tasks use dedicated branches and GitHub pull requests.
- Added PR status tracking so each loop tick records whether previous task pull requests are open, merged, closed, blocked, or unknown.
