# REWE Scraper Notes

## Status

REWE has an approved no-storage low-volume dry-run implementation path for Germany location context `65510 Idstein-Wörsdorf`. Do not store rows, authenticate, use account/session-specific flows, enter cart/checkout, or treat REWE output as comparable app data until a dry-run PR is reviewed and a separate storage/downstream-use approval is recorded.

T051 low-volume public discovery was completed on 2026-06-28 22:54-23:07 UTC+2 using read-only page/search fetches only. No REWE account was used, no postal code or market was selected, no cart/checkout/session-specific flow was entered, no storage was performed, and product examples were capped at three.

T074 approved-location policy was completed on 2026-06-29. Its original decision kept `GRO-31` / T056 blocked until a human named the exact postal code, market or service mode, and run purpose. A later Linear decision superseded the blocked status for dry-run implementation only by approving `65510 Idstein-Wörsdorf` as the Germany location context.

User decision recorded in Linear on 2026-06-29: use `65510 Idstein-Wörsdorf` as the Germany supermarket location context; approve a no-storage REWE dry run using Idstein; if it works, proceed to a separately approved controlled stored run; target exploratory scope is 2-3 categories and up to 100 products only after the first low-volume behavior remains healthy. `GRO-31` / T056 implements the first capped scraper path with one category-equivalent sample and up to three products.

## T056 Low-Volume Dry-Run Implementation

### Approved Context

- Location context: `65510 Idstein-Wörsdorf`.
- Mode: no-storage dry run only.
- First implementation cap: one category-equivalent product sample and at most three public `/shop/p/...` product pages.
- Output: JSON only through `python scripts/scrape_once.py --retailer rewe --limit-categories 1 --max-products 3`.

### Implementation Notes

The first scraper path uses known public product URLs from T051 as a constrained category-equivalent sample. It records `raw_payload.location_context` as `65510 Idstein-Wörsdorf`, preserves the no-location placeholder when numeric prices remain unavailable, strips tracking/query parameters from source URLs, and keeps `location_selection_attempted` false unless a later reviewed task explicitly implements a location-selection flow.

The shared `scripts/scrape_once.py` CLI rejects `--retailer rewe --store` so this task cannot accidentally create stored REWE rows before dry-run review and storage approval.

### T056 Stop Conditions

Stop before continuing the dry run if REWE presents login, registration, PAYBACK/account linking, coupon activation, cart or checkout prompts, current-location detection, market selection, delivery-area checks, pickup-branch selection, delivery-slot selection, CAPTCHA, bot challenge, unexpected block page, disallowed robots path, or unclear separation between regular prices and loyalty/app/account-specific labels.

### 2026-06-29 Live Dry-Run Result

Command:

```bash
python scripts/scrape_once.py --retailer rewe --limit-categories 1 --max-products 3
```

Result: stopped before returning product data because REWE served a verification/bot-protection page containing `Zeig uns, dass du ein Mensch bist`, `WAF Challenge`, and `Enable JavaScript and cookies to continue`. The scraper now raises a clear stop-condition error instead of emitting the challenge page as a product.

Next safe action: keep REWE storage and comparable app use blocked. A future REWE follow-up should either propose a narrower manually reviewed dry-run approach that does not bypass the challenge, or ask the user whether REWE should remain excluded from near-term real-data work.

## T074 Approved-Location Dry-Run Policy

### Superseded Decision

At the time of T074, no approved REWE location, market, delivery service, pickup service, or postal-code context was available for automated use. That is now superseded for the no-storage dry-run implementation by the later `65510 Idstein-Wörsdorf` Linear decision.

Storage, matching, comparison API/UI use, account flows, cart/checkout flows, and broader product volume remain blocked. Any run that still returns `Konkreter Preis abhängig vom Standort` must clearly preserve missing numeric prices.

### Required Approval Before Location-Priced Dry Run

Before any task may select a REWE location or fetch location-priced product/listing pages, Linear must record:

- Approving human and timestamp.
- Exact postal code, market, and service mode: delivery, pickup, or explicitly no-location.
- Whether the selected context is intended only for dry-run observation or may later inform storage policy.
- Allowed URL set, maximum page count, maximum product count, delay/jitter, and whether browser automation is allowed.
- Expected output fields, including how location context, deposit, weighted-item caveats, service fees, loyalty labels, and missing fields will be represented.

### Allowed No-Location Metadata Scope

Without a location approval, REWE work may only:

- Fetch public `/shop/p/...` product pages that are not disallowed by `robots.txt`.
- Capture at most three sample products in a dry-run-only report.
- Record product names, brands, article numbers, canonical URLs, package-size text, public labels such as `Tiefpreis`, and the exact no-location price placeholder.
- Use at least a two-second delay plus jitter for scripted page loads.
- Avoid storage, normalization, matching, comparison UI use, cart flows, checkout flows, account APIs, `/restservices/`, `/shop/mc/`, disallowed query parameters, session IDs, and any attempt to bypass location prompts.

### Stop Conditions

Stop immediately on login, registration, PAYBACK/account linking, coupon activation, cart or checkout prompts, current-location detection, postal-code selection, market selection, delivery-area checks, pickup-branch selection, delivery-slot selection, CAPTCHA, bot challenge, unexpected block page, disallowed robots path, or unclear separation between regular prices and loyalty/app/account-specific labels.

## T051 Public Price And Location Discovery

### URLs Checked

- Start URL: `https://www.rewe.de/shop/`
  - Public fetch timed out once during discovery, so findings below use direct public product pages and REWE service/terms pages rather than category crawling.
- Robots: `https://www.rewe.de/robots.txt`
  - General disallows include `/restservices/`.
  - Shop-specific disallows include `/shop/mc/`, `/shop/checkout/`, `/*;jsessionid`, `/shop/doiretry`, and shop query parameters for search, merchant type, merchant, objects-per-page, and sorting. Plain `/shop/p/...` product pages were not listed as disallowed.
  - Public offer category paths under `/angebote/nationale-angebote/...` are explicitly allowed, but they are separate from the online-shop product/price surface and were not used for data capture.
- Online shopping guidance: `https://www.rewe.de/service/online-einkaufen/`
  - Describes the online shop as delivery or pickup depending on location; not all services are available everywhere.
- Pickup guidance: `https://www.rewe.de/service/abholservice/`
  - The documented flow starts with entering a postal code, choosing a REWE market, building the basket online or in the app, selecting a pickup appointment, then collecting the order.
- Delivery AGB: `https://www.rewe.de/service/agb/lieferservice/`
  - Delivery depends on postal code/service availability. To place an order, the customer must be registered and logged in.
- Pickup AGB: `https://www.rewe.de/service/agb/abholservice/`
  - Pickup depends on entering a postal code and selecting a market. To submit the item selection, the customer must be registered and logged in. Online pickup prices can differ from in-market prices, and loose goods use actual weighed quantities.
- Customer account terms: `https://www.rewe.de/service/nutzungsbedingungen-kundenkonto/`
  - Customer-account terms govern REWE account functionality and state that checkout/service use ties into pickup/delivery terms.

### Price Visibility Without Login Or Location

No-go for price capture without location. Public product pages were accessible without login, but the numeric price was not visible before selecting a location. Instead, observed product pages displayed `Konkreter Preis abhängig vom Standort` and a `Standort wählen` action.

This means public no-location product pages are useful for product metadata discovery only, not for price comparison rows. A scraper that captures numeric prices would need an explicit location/market/service context; that is outside T051 and remains blocked until approved.

### Location, Delivery, And Pickup Stop Conditions

- Stop at any prompt requiring postal code, current-location detection, market selection, delivery area, pickup branch, delivery or pickup appointment, account login, cart submission, checkout, payment, CAPTCHA, or bot challenge.
- Do not use `/shop/mc/`, `/shop/checkout/`, session IDs, disallowed search/filter query parameters, `/restservices/`, account APIs, cart APIs, or checkout payloads.
- Do not infer prices from third-party snippets, search snippets, offer pages, market flyers, account coupons, or app-only labels as regular online-shop shelf prices.
- For any future dry-run task, keep it no-storage and stop if a human-approved test postal-code/market context is not documented before fetching location-priced pages.

### Sample Products

Observed without location. No numeric price, unit price, old price, or online availability was visible for these samples.

| Field | Sample 1 | Sample 2 | Sample 3 |
| --- | --- | --- | --- |
| `retailer` | `rewe` | `rewe` | `rewe` |
| `country` | `DE` | `DE` | `DE` |
| `source_product_id` | `8846520` | `2632428` | `455217` |
| `source_url` | `https://www.rewe.de/shop/p/rewe-bio-frische-vollmilch-3-8-1l/8846520` | `https://www.rewe.de/shop/p/rewe-beste-wahl-spaghetti-n-3-500g/2632428` | `https://www.rewe.de/shop/p/ja-banane-ca-200g/455217` |
| `category` | Product detail page only; no category crawl | Product detail page only; no category crawl | Product detail page only; no category crawl |
| `raw_name` | `REWE Bio Frische Vollmilch 3,8% 1l` | `REWE Beste Wahl Spaghetti N°3 500g` | `ja! Banane ca. 200g` |
| `raw_brand` | `REWE Bio` | `REWE Beste Wahl` | `ja!` |
| `raw_price` | Not visible; `Konkreter Preis abhängig vom Standort` | Not visible; `Konkreter Preis abhängig vom Standort` | Not visible; `Konkreter Preis abhängig vom Standort` |
| `raw_old_price` | Not visible | Not visible | Not visible |
| `raw_unit_price` | Not visible | Not visible | Not visible |
| `raw_package_size` | `1l` | `500g` | `ca. 200g`; variable/weighted item warning shown |
| `raw_currency` | Not visible | Not visible | Not visible |
| `raw_availability` | Not visible without location | Not visible without location | Not visible without location |
| `raw_promotion_text` | `Tiefpreis` label visible | None observed | None observed |
| `location_context` | No location selected | No location selected | No location selected |
| `observed_at` | 2026-06-28 22:54-23:07 UTC+2 | 2026-06-28 22:54-23:07 UTC+2 | 2026-06-28 22:54-23:07 UTC+2 |
| `raw_payload_notes` | Public page exposes title, brand, article number, nutrition/details, no price. | Public search result exposed article number and no-location price placeholder; direct page fetch timed out once. | Public page exposes title, brand, article number, origin/details, variable-weight warning, no price. |

### Stable Source ID Candidates

- Primary candidate: numeric article number shown on product detail pages and mirrored as the final URL segment, for example `8846520`, `2632428`, and `455217`.
- Secondary candidate: canonical `/shop/p/<slug>/<article_number>` URL, with tracking/query parameters stripped.
- Do not treat offer IDs, cart line IDs, merchant IDs, delivery-slot IDs, or selected-market payload IDs as stable product IDs unless a future approved dry run proves they are market-independent.

### Promotion Labels

- `Tiefpreis` was visible on public no-location product pages and should be captured as a promotion/label, not as a numeric discount.
- `REWE Bonus` and Bonus coupons are documented for the Abholservice. Bonus-coupon activation happens in the REWE app before ordering; regular bonus actions may apply automatically. These are loyalty/app/account-adjacent and must be recorded separately from regular prices.
- Pickup/delivery service fees and first-order fee waivers are service terms, not product promotions.
- No PAYBACK label was confirmed in this pass. If it appears later, capture it as a loyalty label and stop before treating it as a regular shelf price.

### Go/No-Go For Dry-Run Scraper Implementation

No-go for a price-capturing REWE dry-run scraper using no-location public pages: numeric prices and availability were not visible without location.

Conditional go only for a future metadata-only no-location probe or a separately approved location-priced dry run if all of these are true:

- The task remains dry-run only with no storage.
- A human explicitly approves the exact test location/market/service context before fetching any location-priced pages; otherwise the run stays metadata-only and preserves missing numeric prices.
- The implementation avoids disallowed robots paths and query parameters, account/login/cart/checkout APIs, bot challenges, and invasive flows.
- The run is capped at one product page or one small category/listing view with at most three products and at least a 2-second delay plus jitter for any scripted page loads.
- Output clearly separates regular price, location context, weighted-item caveats, service fees, loyalty/app/account labels, and missing fields.

## Required Discovery Before Implementation

Start URL: `https://www.rewe.de/shop/`

Use `docs/retailer-discovery-checklist.md` with these REWE-specific questions:

- Price availability: confirm whether numeric prices appear before selecting a delivery or pickup market.
- Location dependence: record whether a postal code, delivery area, pickup market, or delivery slot is required and whether price, availability, source URL, deposit, or unit price changes after selection.
- Account and loyalty behavior: stop if login, PAYBACK, coupon, member, or app-only flows are needed to see prices; record labels separately when they are merely visible.
- Source IDs: prefer stable product IDs from URLs or embedded public payloads; record whether offer IDs change by selected market.
- Robots and terms notes: check `robots.txt`, terms/help pages, and online-shop guidance before scripted dry runs.

## Low-Volume Discovery Limits

- Categories/pages: at most 1 or 2.
- Products captured: at most 3.
- Location context: no location unless a human explicitly approves a documented test context.
- Delay for any later scripted page loads: at least 2 seconds plus jitter.

## Stop Conditions

Stop before price-capturing dry-run implementation or any storage if REWE requires login, account-specific API calls, postal code, market selection, delivery area, pickup branch, delivery slot, CAPTCHA, bot challenge, legal review, or unclear separation between regular and loyalty/member/app prices. Metadata-only no-location work must stop before satisfying any location prompt.

## Planned Task Sequence

1. Complete documentation-only discovery and update this note with sample products and policy blockers.
2. If public no-location prices are usable, implement a low-volume dry-run scraper with no storage.
3. If dry-run output is reviewed and location/legal policy is explicit, plan a one-category, three-product stored validation.
4. Normalize and report only the approved stored run, including location context, missing fields, duplicate source IDs, suspicious prices, and promotion caveats.
