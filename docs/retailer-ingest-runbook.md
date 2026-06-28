# Retailer Ingest Readiness Runbook

This runbook is for controlled raw-product ingest only. It does not approve broad scraping by default. Use the smallest run that answers the current question, record the run scope, and stop whenever retailer behavior, data quality, or approval status is unclear.

## Current Retailer Status

| Retailer | Country | Status | Operator notes |
| --- | --- | --- | --- |
| BILLA | AT | Cleanup before next baseline ingest | Stored raw ingest is available through `scripts/billa_full_ingest.py`, but the broad run exposed category overlap and duplicate source IDs. Finish T042 before using BILLA counts as the baseline for non-BILLA sequencing. |
| MPREIS | AT | Policy-approved for capped raw validation | `no_market_selected` rows are approved only for one raw stored validation run: one page, three products, no normalization or matching. App-only labels are promotion metadata only. Implementation may still block `--store` until the follow-up task narrows the guard. |
| REWE | DE | Discovery-only; storage blocked | No runtime scraper is ready. Complete public-price, market/location, robots/terms, and account-flow discovery before any dry-run scraper work. |
| Kaufland Slovakia | SK | Discovery-only; storage blocked | No runtime scraper is ready. Complete discovery to distinguish public grocery prices from marketplace, leaflet, store, and Kaufland Card/app-only prices. |
| Tesco Slovakia | SK | Discovery-only; storage blocked | No runtime scraper is ready. Complete discovery for public prices, location/session requirements, Clubcard labels, and dynamic page behavior before any dry-run scraper work. |

## All-Retailer Raw Ingest Execution Plan

The raw-data priority is to make each retailer safe and repeatable before storing any non-BILLA rows. BILLA remains the only approved stored source today. Non-BILLA storage is blocked until retailer-specific discovery notes and policy prerequisites are explicit.

### Global Order

1. Finish BILLA dedupe cleanup in T042. Do not treat run 2's duplicate-heavy counts as a clean baseline.
2. Run a clean BILLA baseline ingest/report task after T042. Record raw count, distinct source IDs, duplicate count, normalization count, and cleanup decision.
3. Complete documentation-only discovery for REWE, Kaufland Slovakia, and Tesco Slovakia.
4. Implement the MPREIS capped raw stored validation now that policy allows only `no_market_selected`, one page, three products, and app-only labels as promotion metadata.
5. Implement low-volume dry-run scrapers only after discovery and policy notes are explicit. Dry runs should use one or two categories/pages, at most three products, no storage, and at least a two-second delay.
6. Create retailer-specific controlled stored-ingest tasks only after dry-run outputs are reviewed. Each stored task must start with one category/page and no more than three products, produce a sanity report, and stop before broad volume.
7. Normalize and report each approved stored run before adding matching or comparison work. MPREIS is excluded from this step until its capped stored validation is reviewed and downstream use is separately approved.

### Retailer Sequence

| Order | Retailer | Next safe step | Storage gate |
| --- | --- | --- | --- |
| 1 | BILLA AT | Complete T042, then run a clean stored baseline and report. | Already approved for controlled BILLA only; broader runs still require explicit human approval and token. |
| 2 | MPREIS AT | Implement and run the capped `no_market_selected` raw stored validation from GRO-29 / T054. | Approved only for one page and three products; no market context, app/account flow, normalization, matching, comparison use, or broader volume is approved. |
| 3 | REWE DE | Document public price visibility and delivery/pickup market requirements. | Blocked if login, postal code, market, delivery area, pickup branch, or delivery slot is required without an approved default context. |
| 4 | Kaufland SK | Document whether data is online grocery, marketplace, leaflet, or store-specific. | Blocked if prices are leaflet-only, region-specific, Kaufland Card/app-only, or not grocery product prices without policy approval. |
| 5 | Tesco SK | Document dynamic page behavior, location/session requirements, and Clubcard labeling. | Blocked if prices need account, delivery slot, address, or postal-code context without an approved default context. |

### Non-BILLA Stop Conditions

Stop before implementation, storage, or volume increase when any non-BILLA retailer requires account login, account-specific API calls, postal code, store, delivery area, pickup branch, delivery slot, app-only access, CAPTCHA, bot challenge, legal/terms review, or unclear separation between regular and loyalty/app/member prices.

If a stop condition appears during discovery, keep the retailer in discovery-only status and update the scraper note with the exact blocker. Do not create a stored-ingest task until the blocker has an explicit Linear policy issue.

## Required Approval

Before any stored BILLA run, confirm and record:

- The approving human and timestamp.
- The retailer, country, run purpose, and maximum intended scope.
- Whether the run is dry-run, capped stored validation, or broader stored ingest.
- The maximum category count, maximum product count, `--max-products-per-category`, and delay.
- Where the resulting `scrape_run_id`, sanity report, and cleanup decision will be recorded.

Additional approval is required before any BILLA run that uses more than one category, uses `--all-categories`, or sets `--max-products 0`. The operator must pass the exact token `--confirm-broad-run BILLA_FULL_INGEST`; the token is a guardrail, not approval by itself.

MPREIS approval is limited to one raw stored validation using public `no_market_selected` rows from `https://www.mpreis.at/schneller-erster-einkauf`: one page, three products, no account flows, no store or market selection, no app/API flows, no manual workarounds, no normalization, no matching, and no comparison UI use. The current CLI may still reject `--store` until a follow-up implementation task narrows that guard.

## Rate Limits And Scope

Use these limits unless a narrower task says otherwise:

- Default dry run: one category, up to 10 products, no storage.
- Low-volume stored validation: one category and no more than 3 products when using `scripts/scrape_once.py --store`.
- Capped BILLA validation: at most two categories, at most 50 total products, default `--max-products-per-category 30`, and at least `--delay-seconds 2`.
- Capped MPREIS validation: exactly one public category-equivalent page, no more than 3 products, `raw_payload_json.location_context` of `no_market_selected`, and no downstream processing before sanity review.
- Broad BILLA ingest: only after explicit approval; keep `--delay-seconds` at 2 or higher and avoid `--max-products 0` unless the approval explicitly names an uncapped run.
- Discovery-only retailers: at most one or two categories/pages and three products, with at least 2 seconds between automated page loads.

Do not run concurrent scraper processes against the same retailer.

## Stop Conditions

Stop immediately and ask for direction when any of these happen:

- The retailer requires login, registration, app-only access, account-specific API calls, store selection, postal code, delivery area, pickup branch, or delivery slot and no approved policy exists.
- A bot challenge, CAPTCHA, unexpected block page, repeated timeout, or HTTP rate-limit response appears.
- Robots, terms, legal pages, or site copy raise new uncertainty.
- Prices, availability, loyalty/app-only promotions, or market-specific values cannot be separated clearly.
- A category fails repeatedly, returns unexpected non-product content, or starts producing duplicate/blank source IDs.
- The sanity report shows zero rows, unexpectedly high missing `raw_name`, `raw_price`, or `source_url` counts, suspicious prices, or unexplained duplicate source product IDs.
- An operator cannot identify the run, approval, scope, or cleanup plan.

## Commands

Run commands from the repository root. For stored runs, ensure Postgres is running and migrations are applied:

```bash
docker compose up -d postgres
cd backend
alembic upgrade head
cd ..
```

### BILLA Dry Run

Use this first. It prints JSON and does not write to Postgres:

```bash
python scripts/billa_full_ingest.py
```

For a slightly larger dry-run sample, keep the cap explicit:

```bash
python scripts/billa_full_ingest.py \
  --limit-categories 1 \
  --max-products 10 \
  --delay-seconds 2
```

### BILLA Low-Volume Stored Validation

Use this only after approval for storage:

```bash
python scripts/scrape_once.py --retailer billa --limit-categories 1 --max-products 3 --store
```

Record the printed `scrape_run_id`, then inspect it:

```bash
python scripts/stored_data_sanity_report.py --scrape-run-id <scrape_run_id>
```

### BILLA Capped Multi-Category Validation

Use this only after explicit approval for a broader BILLA run:

```bash
python scripts/billa_full_ingest.py \
  --store \
  --limit-categories 2 \
  --max-products 50 \
  --max-products-per-category 30 \
  --delay-seconds 2 \
  --confirm-broad-run BILLA_FULL_INGEST
```

Stored `billa_full_ingest.py` runs embed the sanity report in the JSON output. Save the `scrape_run_id` from `storage.scrape_run_id`.

### BILLA Broad Run

Broad runs are exceptional. Use them only when the approving human has explicitly approved all categories and the product cap:

```bash
python scripts/billa_full_ingest.py \
  --store \
  --all-categories \
  --max-products 0 \
  --max-products-per-category 30 \
  --delay-seconds 2 \
  --confirm-broad-run BILLA_FULL_INGEST
```

If a broad run stops partway through, resume with exactly one of:

```bash
python scripts/billa_full_ingest.py --start-category-index <index> ...
python scripts/billa_full_ingest.py --resume-after-source-id <source_id> ...
python scripts/billa_full_ingest.py --resume-after-name "<category name>" ...
```

Keep the same approval scope, caps, storage mode, and delay when resuming.

### MPREIS Discovery Dry Run

Use this when validating parser behavior without storage:

```bash
python scripts/scrape_once.py --retailer mpreis --limit-categories 1 --max-products 3
```

### MPREIS Capped Raw Stored Validation

GRO-29 / T054 unblocks only this validation shape after the implementation guard is narrowed:

```bash
python scripts/scrape_once.py --retailer mpreis --limit-categories 1 --max-products 3 --store
```

The current script may still exit with `MPREIS discovery is dry-run only; omit --store.` until the follow-up implementation task lands. When storage succeeds, record the `scrape_run_id`, run the sanity report, and keep the run quarantined from normalization and matching:

```bash
python scripts/stored_data_sanity_report.py --scrape-run-id <scrape_run_id>
```

## Sanity Report Expectations

For every stored BILLA run, keep the JSON run summary and the sanity report with the operator notes. A usable run should have:

- `scrape_run.status` of `succeeded`.
- `counts.raw_products` greater than zero and consistent with the approved cap.
- Low or explained `missing_fields` for `source_product_id`, `source_url`, `raw_name`, and `raw_price`.
- `quality_issues` reviewed, with bad rows inspected when present.
- Duplicate source product IDs explained by known site behavior before normalization or matching proceeds.

If a stored run is questionable, do not normalize or use it for matching. Clean it up or leave it quarantined with a note.

For MPREIS, a usable capped validation also requires `raw_payload_json.location_context` to remain `no_market_selected`, app-only labels to appear only as promotion metadata, and no evidence that the public price was app/account/market-only.

## Rollback And Cleanup

Stored raw data is attached to one `scrape_runs.id`. Prefer deleting a whole bad run instead of hand-editing individual raw rows.

Inspect the run first:

```bash
python scripts/stored_data_sanity_report.py --scrape-run-id <scrape_run_id>
```

If no downstream normalized rows or matches have been created from that run, delete the raw rows and run record:

```bash
docker compose exec postgres psql -U grocery_saver -d grocery_saver -c \
  "BEGIN; DELETE FROM raw_products WHERE scrape_run_id = <scrape_run_id>; DELETE FROM scrape_runs WHERE id = <scrape_run_id>; COMMIT;"
```

If normalization has already created `retailer_products`, or matching has created `product_matches`, stop and plan a cleanup task before deleting anything. Those tables depend on the raw rows and need an ordered cleanup decision.

MPREIS capped validation runs must not be normalized or matched before a separate downstream approval. If an MPREIS validation run is bad, delete the whole run and its raw rows before creating any downstream records.

After cleanup, rerun the sanity report without `--scrape-run-id` only if another valid BILLA run should remain as the latest run:

```bash
python scripts/stored_data_sanity_report.py
```

## Operator Log Template

Use this short template in the task, PR, or run notes:

```text
Retailer/country:
Approval:
Command:
Scope caps:
Started/finished:
scrape_run_id:
Sanity report summary:
Stop conditions observed:
Cleanup decision:
Next action:
```
