# Retailer Ingest Readiness Runbook

This runbook is for controlled raw-product ingest only. It does not approve broad scraping by default. Use the smallest run that answers the current question, record the run scope, and stop whenever retailer behavior, data quality, or approval status is unclear.

## Current Retailer Status

| Retailer | Country | Status | Operator notes |
| --- | --- | --- | --- |
| BILLA | AT | Clean baseline complete | Post-dedupe stored baseline `scrape_run_id=3` produced 3 raw rows, 3 normalized rows, 3 distinct source IDs, and no duplicate-source-ID issues. Broader BILLA runs still require explicit human approval and token. |
| MPREIS | AT | Report-only normalization approved; broader downstream blocked | `scrape_run_id=4` stored 3 `no_market_selected` raw rows with no sanity-report quality issues. A report-only normalization pass may validate parsing for these rows, but matching, comparison UI use, broader volume, and market-selected scraping remain blocked. |
| REWE | DE | Discovery-only; storage blocked | Public no-location pages expose metadata but not numeric prices. Any price-capturing dry run needs an exact human-approved postal code, market, service mode, run purpose, cap, and stop rule. |
| Kaufland Slovakia | SK | Excluded from first version; storage blocked | `GRO-51` excludes Kaufland Slovakia from the first multi-retailer version. Do not reopen scraper, storage, matching, API, or UI work until a later revisit after BILLA/MPREIS/REWE gates are settled. |
| Tesco Slovakia | SK | Excluded from first version; storage blocked | `GRO-52` excludes Tesco Slovakia from the first multi-retailer version. Do not reopen scraper, storage, normalization, matching, API, UI, account/session, or location work until a later revisit after BILLA/MPREIS/REWE gates are settled. |

## 2026-06-29 All-Retailer Readiness Summary

This summary closes `GRO-38` / T063 by recording the current raw-ingest gates across every known retailer. It is a planning report only; it does not approve a new scrape, storage run, location context, account flow, matching path, comparison UI path, or volume increase.

| Retailer | Raw rows | Normalized rows | Current safe next step | Stop conditions and blockers | Capped multi-category readiness |
| --- | ---: | ---: | --- | --- | --- |
| BILLA AT | 3 in clean baseline `scrape_run_id=3` | 3 | Use the clean baseline as the reusable local reference; plan another BILLA run only with explicit approval and caps. | Stop on duplicate-heavy category overlap, unexpected missing key fields, suspicious prices, or missing approval scope. Broader BILLA runs still require a human-approved purpose, cap, delay, and broad-run token. | Conditionally ready for a capped BILLA-only validation, not an automatic all-category run. |
| MPREIS AT | 3 quarantined `no_market_selected` rows in `scrape_run_id=4` | 0 reusable app rows; report-only normalization pending | Run `GRO-48` / T079 to validate parsing and data quality for report-only output from the existing raw rows. | Matching, comparison API/UI use, market-selected scraping, broader volume, app/account flows, and any reusable baseline remain blocked until a human approves exact market/location context and downstream policy. | Not ready. |
| REWE DE | 0 stored | 0 | Keep price capture blocked; only metadata-only no-location documentation can proceed without a human-approved postal code, market, service mode, and run purpose. | Numeric prices are not visible without location. Stop before location selection, account, cart, checkout, PAYBACK/coupon flows, `/restservices/`, disallowed paths, CAPTCHA, or bot challenges. | Not ready. |
| Kaufland SK | 0 stored | 0 | If prioritized, scope a no-storage leaflet/offer dry-run or policy decision that explicitly names default-store versus approved-store semantics. | `www.kaufland.sk` hit verification/bot protection, public store offers are leaflet/store-contextual, stable product IDs were not visible, and Kaufland Card/app/account prices must stay separate. | Not ready. |
| Tesco SK | 0 stored | 0 | Keep implementation blocked unless a policy/legal review approves an account/location/session test context. | Tesco terms say current prices appear after registered login; accurate availability/offers depend on delivery slot/store context; product pages and sitemaps returned protection or `403`. | Not ready. |
| Tegut on Amazon DE | 0 stored | 0 | Keep as discovery-only unless a policy issue approves Amazon-hosted grocery source semantics plus postcode/account context. | Grocery availability is postcode-dependent, ordering requires Amazon account context, source category returned `404`, and Amazon robots disallow account/cart/availability/offer/promotion paths. | Not ready. |

Cleanup and downstream-use decisions:

- Keep BILLA `scrape_run_id=3` as the clean controlled baseline because its raw and normalized counts match the approved cap and it has no duplicate-source-ID issues.
- Keep MPREIS `scrape_run_id=4` quarantined. Report-only normalization may inspect parser behavior, but any misleading parser result, changed `location_context`, app-only price ambiguity, missing key field, or suspicious value should keep the run out of app surfaces and trigger cleanup or parser-fix planning.
- Do not create stored-ingest issues for REWE, Kaufland Slovakia, Tesco Slovakia, or Tegut on Amazon until the relevant policy blocker is explicitly resolved in Linear.
- Do not use any non-BILLA retailer rows for matching or comparison UI until that retailer has a reviewed stored validation report and a downstream-use policy that allows comparable product data.

## 2026-06-29 BILLA/MPREIS/REWE First-Version Scope

`GRO-62` narrows the first multi-retailer path after the Kaufland Slovakia and Tesco Slovakia decisions. The first version should now be planned around BILLA plus only the still-allowed MPREIS and REWE paths. This is a scoping record, not approval for new scraping, storage, matching, API wiring, UI exposure, location selection, account flows, or broader volume.

| Retailer | First-version role | Current blocker | Next safe Linear action |
| --- | --- | --- | --- |
| BILLA AT | Reusable baseline source | None for the existing `scrape_run_id=3` baseline; broader BILLA volume still needs explicit run approval and caps. | Keep the clean baseline available for local development and comparison-shape testing. Create a new BILLA run task only when a human approves the exact purpose, cap, delay, and cleanup plan. |
| MPREIS AT | Candidate second source only after policy approval | Existing `scrape_run_id=4` rows are `no_market_selected` and approved only for report-only validation. Comparable downstream use, market-selected scraping, matching, API use, and UI use remain blocked. | Prepare a human decision packet for the exact market/location/downstream-use policy before moving `GRO-34` / T059 or any MPREIS comparison task out of `Blocked`. |
| REWE DE | Candidate third source only after policy approval | No approved price-visible location or service context exists. Public no-location pages do not expose numeric prices. | Prepare a human decision packet for postal code, market/service mode, allowed URLs, caps, and stop conditions before moving `GRO-31` / T056 or `GRO-35` / T060 out of `Blocked`. |
| Kaufland Slovakia | Excluded | First-version exclusion is recorded in `GRO-51`. | Keep `GRO-32` / T057 and `GRO-36` / T061 blocked/canceled unless a later revisit explicitly approves a new context. |
| Tesco Slovakia | Excluded | First-version exclusion is recorded in `GRO-52`. | Keep `GRO-33` / T058 and `GRO-37` / T062 blocked/canceled unless a later revisit explicitly approves a new context. |

No existing MPREIS or REWE implementation issue is dependency-complete today. The useful next retailer action is a policy/scoping issue that drafts the two human approval packets together, because the same first-version comparison decision has to define whether BILLA-only development continues while MPREIS/REWE wait for approved contexts.

## All-Retailer Raw Ingest Execution Plan

The raw-data priority is to make each retailer safe and repeatable before storing any non-BILLA rows. BILLA remains the only approved stored source for reusable baselines today. MPREIS has a one-time capped raw validation approval; all other non-BILLA storage is blocked until retailer-specific discovery notes and policy prerequisites are explicit.

### Global Order

1. Keep the clean BILLA baseline as the reusable stored-data reference until another explicitly approved BILLA run is needed.
2. Run report-only normalization for the quarantined MPREIS capped raw validation before considering any broader policy. Matching, comparison UI use, market-selected scraping, and broader volume remain blocked.
3. Draft the MPREIS and REWE human approval packets needed for first-version use. MPREIS needs an exact market/location and downstream-use policy; REWE needs an exact postal code, market/service mode, allowed URL surface, cap, and stop rule.
4. Keep Kaufland Slovakia and Tesco Slovakia excluded from first-version runtime work until a later revisit after the BILLA/MPREIS/REWE gates are settled.
5. Implement low-volume dry-run scrapers only after discovery and policy notes are explicit. Dry runs should use one or two categories/pages, at most three products, no storage, and at least a two-second delay.
6. Create retailer-specific controlled stored-ingest tasks only after dry-run outputs are reviewed. Each stored task must start with one category/page and no more than three products, produce a sanity report, and stop before broad volume.
7. Normalize and report each approved stored run before adding matching or comparison work. MPREIS is excluded from this step until its capped stored validation is reviewed and downstream use is separately approved.

### Retailer Sequence

| Order | Retailer | Next safe step | Storage gate |
| --- | --- | --- | --- |
| 1 | BILLA AT | Use `scrape_run_id=3` as the clean controlled baseline while planning the next approved BILLA run. | Already approved for controlled BILLA only; broader runs still require explicit human approval and token. |
| 2 | MPREIS AT | Normalize `scrape_run_id=4` for reporting only, then decide whether a human-approved market/location policy task is appropriate. | Only the capped raw validation and report-only normalization are approved; no market context, app/account flow, matching, comparison use, broader storage, or broader volume is approved. |
| 3 | REWE DE | Draft the exact human approval packet for a location/service-scoped no-storage dry run before implementation. | Blocked until the user approves postal code, market/service mode, allowed URLs, caps, delay/jitter, and stop conditions. |
| 4 | Kaufland SK | Excluded from first-version implementation. | Blocked until a later revisit explicitly approves a new scope after BILLA/MPREIS/REWE gates are settled. |
| 5 | Tesco SK | Excluded from first-version implementation. | Blocked until a later revisit explicitly approves a new scope after BILLA/MPREIS/REWE gates are settled. |

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

MPREIS approval is limited to one raw stored validation using public `no_market_selected` rows from `https://www.mpreis.at/schneller-erster-einkauf`: one page, three products, no account flows, no store or market selection, no app/API flows, no manual workarounds, no matching, and no comparison UI use. A follow-up may normalize only the existing `scrape_run_id=4` rows for a report-only parser and data-quality validation; the output must be labeled non-comparable and must not feed matching, API, or UI comparison surfaces.

## Rate Limits And Scope

Use these limits unless a narrower task says otherwise:

- Default dry run: one category, up to 10 products, no storage.
- Low-volume stored validation: one category and no more than 3 products when using `scripts/scrape_once.py --store`.
- Capped BILLA validation: at most two categories, at most 50 total products, default `--max-products-per-category 30`, and at least `--delay-seconds 2`.
- Capped MPREIS validation: exactly one public category-equivalent page, no more than 3 products, `raw_payload_json.location_context` of `no_market_selected`, and no downstream processing except the approved report-only normalization of `scrape_run_id=4`.
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

The CLI allows stored MPREIS only inside this cap. When storage succeeds, record the `scrape_run_id`, run the sanity report, and keep the run quarantined from normalization and matching:

```bash
python scripts/stored_data_sanity_report.py --retailer mpreis --scrape-run-id <scrape_run_id>
```

### MPREIS Report-Only Normalization

GRO-48 / T079 allows parser and data-quality validation for the existing quarantined
`scrape_run_id=4` rows only. This command does not scrape, does not create
`retailer_products`, and labels MPREIS output as non-comparable validation data:

```bash
python scripts/normalize_once.py 4 --retailer mpreis --report-only
```

Use the report to inspect normalized package quantity/unit, unit-price parse results,
missing key fields, skipped rows, suspicious values, location context, and app-only label
separation. Do not use MPREIS rows for matching, comparison APIs, frontend comparison UI,
or reusable price baselines until a separate human-approved market/location downstream-use
policy allows that.

## Sanity Report Expectations

For every stored BILLA run, keep the JSON run summary and the sanity report with the operator notes. A usable run should have:

- `scrape_run.status` of `succeeded`.
- `counts.raw_products` greater than zero and consistent with the approved cap.
- Low or explained `missing_fields` for `source_product_id`, `source_url`, `raw_name`, and `raw_price`.
- `quality_issues` reviewed, with bad rows inspected when present.
- Duplicate source product IDs explained by known site behavior before normalization or matching proceeds.

If a stored run is questionable, do not normalize or use it for matching. Clean it up or leave it quarantined with a note.

For MPREIS, a usable capped validation also requires `raw_payload_json.location_context` to remain `no_market_selected`, app-only labels to appear only as promotion metadata, and no evidence that the public price was app/account/market-only. Report-only normalization must flag parser failures, suspicious values, or unclear app-only price separation instead of producing comparable rows.

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

MPREIS capped validation rows may be normalized only for the approved report-only validation scope. They must not be matched or used by comparison APIs/UI before a separate human-approved market/location and downstream-use policy. If an MPREIS validation run is bad, delete the whole run and its raw rows before creating any reusable downstream records.

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
