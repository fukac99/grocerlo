# REWE Scraper Notes

## Status

REWE is discovery-only. Do not implement runtime scraping, store rows, select a market, authenticate, or use account/session-specific flows until the discovery checklist is completed and the location policy is explicit.

T051 low-volume public discovery was completed on 2026-06-28 22:54-23:07 UTC+2 using read-only page/search fetches only. No REWE account was used, no postal code or market was selected, no cart/checkout/session-specific flow was entered, no storage was performed, and product examples were capped at three.

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

Conditional go only for a future metadata-only or approved-location dry run if all of these are true:

- The task remains dry-run only with no storage.
- A human explicitly approves the exact test location/market/service context before fetching location-priced pages.
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

Stop before dry-run implementation or storage if REWE requires login, account-specific API calls, postal code, market selection, delivery area, pickup branch, delivery slot, CAPTCHA, bot challenge, legal review, or unclear separation between regular and loyalty/member/app prices.

## Planned Task Sequence

1. Complete documentation-only discovery and update this note with sample products and policy blockers.
2. If public no-location prices are usable, implement a low-volume dry-run scraper with no storage.
3. If dry-run output is reviewed and location/legal policy is explicit, plan a one-category, three-product stored validation.
4. Normalize and report only the approved stored run, including location context, missing fields, duplicate source IDs, suspicious prices, and promotion caveats.
