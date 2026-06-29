# MPREIS Scraper Notes

## 2026-06-28 Low-Volume Discovery Dry Run

Command:

```bash
python3 scripts/scrape_once.py --retailer mpreis --limit-categories 1 --max-products 3
```

Result: the dry run returned one documented category-equivalent page, `Schneller erster Einkauf`, and three product payloads without using `--store`.

Low-volume limits used:

- Categories/pages: 1 (`https://www.mpreis.at/schneller-erster-einkauf`).
- Products captured: 3.
- Automated page loads: one scraper page load for the category-equivalent page, with a 2 second post-load delay.
- Location context: no market selected; no account, postal code, store, pickup branch, delivery area, or delivery slot was used.

Sample products:

- BIO vom BERG Bio Eier M/L 6er-Packung: `3,59 €`, `0,60 € /Stk`, `6STK`, source ID `500167`, source `https://www.mpreis.at/shop/p/bio-vom-berg-bio-eier-ml-6er-packung-500167`.
- Erlebnissennerei Zillertal Berg Heumilch 3,6%: `1,85 €`, `1,85 € /l`, `1l`, source ID `812735`, source `https://www.mpreis.at/shop/p/erlebnissennerei-zillertal-berg-heumilch-36-812735`.
- Jeden Tag Mozzarella gerieben: `1,99 €`, `7,96 € /kg`, `250g`, source ID `241728`, source `https://www.mpreis.at/shop/p/jeden-tag-mozzarella-gerieben-241728`.

## Discovery Findings

Price availability: public list/product-card surfaces show numeric EUR prices before login and before selecting a market. Product cards also show package size and unit price when available.

Location dependence: availability is explicitly location-dependent. Each captured product showed `Verfügbarkeit in deinem Markt prüfen`, `Noch kein Markt gewählt`, and `Verfügbarkeit in allen Märkten prüfen`. No location was selected during this task, so market-specific price or availability changes are unresolved.

Promotions and app-only flags: captured products showed `NUR MIT APP`. MPREIS FAQ/app pages describe app coupons, Rabattsticker, and customer-card behavior; these must be kept separate from normal shelf prices in any later broader implementation.

Source IDs: product URLs and card classes expose numeric source IDs. The scraper prefers `c3-item-<id>` from the product card and falls back to the trailing numeric ID in `/shop/p/<slug>-<id>` URLs.

Fields captured: retailer, country, source URL, source product ID, category, name, brand, price, unit price, package size, currency, availability text, promotion text, no-market location context, and compact raw card text.

Raw payload notes: the public HTML contains product cards as `a.c3-product[href]` elements with producer/name, weight, price, unit, app-discount, availability, and `c3-item-<id>` class data.

Robots and terms notes: checked `https://www.mpreis.at/robots.txt`; it allows `User-agent: *` while disallowing `/search/`, `*?filter*`, `/newsletter/`, and `*?index=*`. Checked MPREIS legal/help pages surfaced during discovery: `https://www.mpreis.at/nutzungsbedingungen`, `https://www.mpreis.at/agb`, `https://www.mpreis.at/sp/impressum`, `https://www.mpreis.at/sp/datenschutz`, `https://www.mpreis.at/haeufige-fragen`, and `https://www.mpreis.at/app/faq-support`. Keep future scraping away from disallowed search/filter/index paths and do not use app/account flows without explicit legal review.

Stop conditions: stop before selecting a market, logging in, registering, using the app/API account flow, bypassing a challenge, scraping disallowed paths, or increasing beyond the documented low-volume discovery limits without explicit approval.

## 2026-06-28 Storage Policy Decision (GRO-29 / T054)

Policy decision: `no_market_selected` MPREIS rows may be stored for one capped raw validation run only. No specific market, postal code, pickup branch, delivery area, delivery slot, app session, or account context is approved for MPREIS yet. Stored rows must keep `raw_payload_json.location_context` as `no_market_selected` and operator notes must state that availability remains market-dependent.

Downstream use: the approved validation run is raw-storage only. Do not normalize MPREIS rows, match them, show them in comparison UI, or use them as a reusable baseline until a later task reviews the stored sanity report and explicitly approves downstream use.

App-only promotion handling: public regular card prices may be stored in `raw_price` when visible without app/account access. `NUR MIT APP`, app coupons, Rabattsticker, customer-card copy, and similar labels are promotion metadata only and must be stored in `raw_promotion_text` or `raw_payload_json`, not as `raw_price`, `raw_old_price`, or a separate comparable price type. If a future card exposes only an app-only numeric price without a public regular price, exclude that price from regular price fields and stop for policy review before storing broader data.

Legal and robots boundary: the approved validation may use only the public category page `https://www.mpreis.at/schneller-erster-einkauf` and public `https://www.mpreis.at/shop/p/...` product URLs observed from that page. Do not scrape `/search/`, URLs containing filter parameters, `/newsletter/`, URLs containing `index=`, account/login/register flows, app/API-only flows, carts, checkout, market-selection flows, or any CAPTCHA, challenge, or blocked response. Re-check robots/legal notes before any later scope expansion.

Low-volume stored cap: at most one stored MPREIS validation run, one category-equivalent page, three raw products total, and the existing two-second page-load delay. Do not run concurrent MPREIS scrapers and do not increase volume in the same task.

Cleanup plan: record the `scrape_run_id`, run the stored-data sanity report, and keep the run quarantined from normalization and matching. If the run has zero rows, missing source IDs/URLs/names/prices, unexpected duplicate source IDs, suspicious prices, unclear app-only price separation, changed location prompts, or any legal/robots uncertainty, delete the entire MPREIS `scrape_runs` record and its `raw_products` rows before any downstream processing. Prefer whole-run deletion over row edits.

Unblock decision: T028 / GRO-8 can be unblocked only for implementing and running the capped `no_market_selected` raw stored validation described here. Broad MPREIS scraping, approved-market scraping, app/account flows, normalization, matching, and comparison use remain blocked.

## Storage Gate

MPREIS storage policy is resolved for a single capped raw validation run under `no_market_selected`. `scripts/scrape_once.py --retailer mpreis --store` is allowed only when the run stays within one category-equivalent page and no more than three products; broader stored MPREIS runs still exit before scraping.

## 2026-06-29 Capped Raw Stored Validation

Command:

```bash
python3 scripts/scrape_once.py --retailer mpreis --limit-categories 1 --max-products 3 --store
```

Result: stored `scrape_run_id=4` with three raw rows from `https://www.mpreis.at/schneller-erster-einkauf`.

Sanity report:

```bash
python3 scripts/stored_data_sanity_report.py --retailer mpreis --scrape-run-id 4
```

The sanity report found 3 raw rows, 0 quality issues, 0 missing source IDs, 0 missing source URLs, 0 missing names, 0 missing prices, 0 missing unit prices, 0 missing package sizes, and 0 bad rows.

Validation notes:

- All 3 rows kept `raw_payload_json.location_context` as `no_market_selected`.
- All 3 rows stored `NUR MIT APP` only as `raw_promotion_text`.
- No market, postal code, pickup branch, delivery area, delivery slot, app session, account, normalization, matching, or comparison UI use was performed.
- Cleanup decision: keep the run quarantined as the approved capped raw validation sample.

Before any broader stored MPREIS task, another policy task must document:

- Whether an approved market/location context is needed beyond `no_market_selected`.
- Whether app-only prices can ever become a separate non-comparable price type.
- Which additional source URLs and paths are allowed under updated robots and terms notes.
- The exact expanded cap, cleanup plan, and sanity-report expectations.

## 2026-06-29 Downstream-Use Policy Decision (GRO-45 / T075)

Policy decision: the quarantined `scrape_run_id=4` rows may be normalized only for a report-only parser and data-quality validation. This approval is limited to the already stored three `no_market_selected` raw rows and must not create comparable product data for the app. The report may calculate normalized package quantities, unit-price parsing results, missing-field counts, app-label separation, and parser failures, but it must label all output as non-comparable MPREIS validation data.

Approved market context: an explicit human-approved market, postal code, pickup branch, delivery area, or delivery slot is required before any MPREIS row can be matched to other retailers, shown in the comparison UI, used as a price baseline, or expanded beyond the existing capped validation page. `no_market_selected` rows are useful for parser validation only because availability and potentially price semantics remain market-dependent.

App-only promotion handling: `NUR MIT APP`, app coupons, Rabattsticker, customer-card copy, and app-only numeric prices remain promotion metadata. They must not become regular comparable prices. If a future parser sees an app-only numeric price without a visible public regular price, the run must stop for policy review before normalization or storage beyond a quarantined raw sample.

Expanded cap and cleanup plan: no expanded MPREIS cap is approved yet. The next safe implementation scope is a report-only normalization pass over `scrape_run_id=4`, with no scraping and no new raw rows. If the report finds missing source IDs, missing source URLs, missing names, missing prices, unclear app-only price separation, changed location-context values, suspicious prices, or parser failures that would produce misleading normalized values, keep the run quarantined and plan a cleanup or parser-fix task before any broader use.

Unblock decision: keep GRO-34 / T059 blocked for broader controlled stored ingest, matching, comparison UI use, and any market-selected MPREIS scraping. Create or use a narrower follow-up task for report-only normalization of `scrape_run_id=4`; that follow-up should not unblock matching or UI comparison work.

## Planned Task Sequence

1. Run a one-page, three-product stored validation through the narrowed CLI guard.
2. Produce and review the stored-data sanity report, including location context, app-only promotion caveats, missing fields, duplicate source IDs, suspicious prices, and package-size parse results.
3. Run report-only normalization with `python scripts/normalize_once.py 4 --retailer mpreis --report-only` for the quarantined `scrape_run_id=4` rows to validate parsing and data quality without treating MPREIS prices as comparable.
4. Keep matching, comparison UI use, market-selected scraping, and broader volume blocked until a human approves exact market/location context and expanded scope.
