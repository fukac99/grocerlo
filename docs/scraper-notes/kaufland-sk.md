# Kaufland Slovakia Scraper Notes

## Status

Kaufland Slovakia is discovery-only. Do not implement runtime scraping, store rows, select a store/region, authenticate, or use app/account flows until discovery proves which public grocery price surface is safe to use.

T052 low-volume public discovery was completed on 2026-06-28 23:34-23:54 UTC+2 using read-only browser/search fetches only. No Kaufland account was used, no store was manually selected or changed, no app/account/loyalty flow was entered, no bot protection was bypassed, no storage was performed, and product examples were capped at three public offer rows.

## T080 Source-Policy Recommendation

Recommendation: keep Kaufland Slovakia blocked for regular grocery product-price scraping, storage, matching, and comparison UI use. The only potentially safe future automation target is a no-storage, low-volume `predajne.kaufland.sk` leaflet/store-offer dry run, and that should be modeled as store-contextual promotional offer data rather than national shelf-price grocery data.

Source modeling decision:

- Do not model `www.kaufland.sk` marketplace listings as grocery retailer prices. The host returned verification/bot-protection pages during discovery, appears marketplace-oriented, and mixes non-grocery product semantics that do not match the app's supermarket price-comparison goal.
- Do not model Kaufland Card, app coupons, personalized coupons, shopping lists, digital receipts, account flows, or loyalty prices as ordinary public grocery offers. Keep these as explicit stop conditions unless a later human-approved policy creates a separate loyalty/app data model.
- If a future task is approved, model `predajne.kaufland.sk` only as `source_surface=leaflet_store_offer` with required validity dates, selected-store/default-store context, old price, offer price, unit price, missing source-ID caveat, and promotion labels preserved in raw payload metadata.

Minimum human decision before any safe dry-run implementation:

- Decide whether the project may inspect the public default-store leaflet context exactly as rendered, or whether a named test store must be explicitly approved first.
- Decide whether leaflet/store-offer prices are useful for Grocerlo as promotional regional offers, knowing they are not regular national shelf prices and may not have stable product IDs.
- Approve the exact dry-run cap and allowed URL path before implementation. Recommended maximum: one public offer page or one category group, at most three products, no storage, no matching, no comparison API/UI exposure, and at least a 2-second delay plus jitter.

Until those decisions are recorded in Linear, keep `GRO-32` / T057 and `GRO-36` / T061 blocked. This recommendation does not approve scraping, storage, bot-challenge handling, store selection, account/app flows, loyalty-price capture, normalization, matching, or UI exposure.

## T052 Public Price-Surface Discovery

### URLs Checked

- Start URL: `https://www.kaufland.sk/`
  - Public fetch returned a verification/bot-protection page requiring JavaScript/cookies and confirmation that the visitor is not a robot. This is a stop condition for `www.kaufland.sk` discovery.
- Main robots: `https://www.kaufland.sk/robots.txt`
  - Returned the same verification/bot-protection page, so no robots rules could be safely confirmed for the marketplace host.
- Store/leaflet robots: `https://predajne.kaufland.sk/robots.txt`
  - Allows the store/leaflet site generally, with `Disallow: /etc.clientlibs/`, `Allow: /etc.clientlibs/kaufland`, and sitemap `https://predajne.kaufland.sk/.sitemap.xml`.
- Store offers overview: `https://predajne.kaufland.sk/aktualna-ponuka.html`
  - Public page describing weekly offers, digital leaflet, Kaufland App, newsletter, and Kaufland Card.
- Store offers listing: `https://predajne.kaufland.sk/aktualna-ponuka/prehlad.html`
  - Public overview text exposed offer products, prices, old prices, unit prices, categories, and Kaufland Card labels. One direct fetch timed out, so captured fields come from a search-result page snapshot rather than a scripted crawl.
- Digital leaflet: `https://predajne.kaufland.sk/aktualna-ponuka/letak.html`
  - Public page loaded with default store context `Kaufland Poprad-Moyzesova`, current leaflet dates `25.06.2026 - 01.07.2026`, `Zmenit predajnu` controls, and "while supplies last/customary quantities/errors reserved" caveats.
- App surface: `https://predajne.kaufland.sk/servis/app.html`
  - Search/result text describes leaflet browsing, favorite-store assortment sorting, shopping lists, offer alarms, recipes, and store search. Some features require a user account.
- Kaufland Card surface: `https://predajne.kaufland.sk/kaufland-card.html`
  - Public page text describes card benefits, coupons, loyalty points, and online marketplace integration. Coupon activation and personalized coupons are loyalty/account-specific and not a regular public shelf-price surface.
- Store FAQ/location guidance: `https://predajne.kaufland.sk/servis/caste-otazky.html`
  - Search/result text says selected store can be stored with cookies and changed through `Zmenit predajnu`.
- Privacy/customer data pages checked:
  - `https://predajne.kaufland.sk/ochrana-osobnych-udajov.html`
  - `https://spolocnost.kaufland.sk/ochrana-osobnych-udajov-zakaznici.html`
  - These describe customer accounts, shopping lists, K-App, online marketplace linkage, and data handling.
- Imprint/legal pages found:
  - `https://spolocnost.kaufland.sk/tiraz.html`
  - `https://spolocnost.kaufland.sk/ochrana-osobnych-udajov.html`
  - Search/result text identifies Kaufland Slovenska republika v.o.s. for Slovak store/company pages and separates marketplace matters from the Slovak store operator.
- Marketplace customer terms URL found from public Kaufland Card text: `https://www.kaufland.sk/i/legal/tc-customers/~26LEVy9TssxpgS0maITojQ`
  - Direct fetch returned the same verification/bot-protection page as `www.kaufland.sk`, so the URL was recorded but not used.

### Surface Classification

- Grocery shelf-price surface: no-go found. No public no-location grocery ecommerce surface with regular shelf prices was confirmed on `www.kaufland.sk`; the host was behind verification during discovery.
- Store offer/leaflet surface: public and low-volume readable on `predajne.kaufland.sk`. It exposes promotional/store-offer prices, old prices, unit prices, and category groupings, but it is a leaflet/offer surface, not a full grocery catalog.
- Marketplace surface: distinct from grocery/store offers. `www.kaufland.sk` is described as the online marketplace and search snippets showed non-grocery examples such as garden chairs, brush cutters, trampolines, bicycles, dining tables, pans, and tires. It is not suitable as a grocery price source for this task, and direct access hit bot-protection verification.
- Store surface: public store pages and leaflet pages include a selected-store context. Discovery observed default context `Kaufland Poprad-Moyzesova`; FAQ/search text says the selected store is persisted with cookies and can be changed through `Zmenit predajnu`.
- Loyalty/app surface: public pages document Kaufland Card, coupons, personalized offers, offer alarms, shopping lists, digital receipts, and app features. These are loyalty/account/app-adjacent and must be kept separate from public regular prices.

### Location And Store Dependence

The safe public store/leaflet surface is store-contextual. The leaflet page rendered a default selected store (`Kaufland Poprad-Moyzesova`) and `Zmenit predajnu` controls. FAQ/search text says users can change the store and that the chosen store can be retained by cookies.

Stop before selecting or changing a store, using browser geolocation, writing a cookie-backed location policy, entering postal/location search, or treating default-store offers as national shelf prices. If a future task wants store-specific discovery, it needs an explicit human-approved store context and must continue to label every output with that store.

### Sample Public Offer Rows

Observed from the public `prehlad.html` overview snapshot with no manual store selection. The snapshot text included `Ponuka platna 02.05.`; because the separately fetched leaflet page showed a different current leaflet date and selected store, treat these as surface/field examples only, not current-price assertions.

| Field | Sample 1 | Sample 2 | Sample 3 |
| --- | --- | --- | --- |
| `retailer` | `kaufland_sk` | `kaufland_sk` | `kaufland_sk` |
| `country` | `SK` | `SK` | `SK` |
| `source_product_id` | Not visible in rendered text | Not visible in rendered text | Not visible in rendered text |
| `source_url` | `https://predajne.kaufland.sk/aktualna-ponuka/prehlad.html` | `https://predajne.kaufland.sk/aktualna-ponuka/prehlad.html` | `https://predajne.kaufland.sk/aktualna-ponuka/prehlad.html` |
| `category` | `Aktualna ponuka - top produkty` | `Aktualna ponuka - top produkty` | `Aktualna ponuka - top produkty` |
| `raw_name` | `Mliekarna Kunin Termix Tvarohovy dezert` | `Uhorka salatova` | `Zemiaky "C"` |
| `raw_brand` | `Mliekarna Kunin Termix` | Not displayed separately | `Z lasky k tradicii` |
| `raw_price` | `0,29` | `0,36` | `0,95` |
| `raw_old_price` | `0,75` | `0,89` | `2,19` |
| `raw_unit_price` | `(=1 kg 3,22)` | Not visible | `(=1 kg 0,48)` |
| `raw_package_size` | `90 g` | `1 kus` | `2 kg balenie` |
| `raw_currency` | EUR implied by Slovak Kaufland offer page; currency symbol not present in fetched text | EUR implied by Slovak Kaufland offer page; currency symbol not present in fetched text | EUR implied by Slovak Kaufland offer page; currency symbol not present in fetched text |
| `raw_availability` | Offer caveat only: products available while supplies last/customary quantities | Offer caveat only: products available while supplies last/customary quantities | Offer caveat only: products available while supplies last/customary quantities |
| `raw_promotion_text` | `-61%` | `-59%` | `-56%` |
| `location_context` | No manual store selected; public leaflet/store context present | No manual store selected; public leaflet/store context present | No manual store selected; public leaflet/store context present |
| `observed_at` | 2026-06-28 23:34-23:54 UTC+2 | 2026-06-28 23:34-23:54 UTC+2 | 2026-06-28 23:34-23:54 UTC+2 |
| `raw_payload_notes` | Rendered public text only; no stable product ID visible | Rendered public text only; no stable product ID visible | Rendered public text only; no stable product ID visible |

### Stable Source ID Candidates

- No stable product-level IDs were visible in the rendered public offer overview text.
- Current fallback candidate for a future dry run: canonical leaflet/overview URL plus category, product display name, package size, promotion validity text, and selected-store context. This is offer-specific and weaker than a product ID.
- Do not use marketplace product IDs, Kaufland Card coupon IDs, digital receipt IDs, app shopping-list IDs, cookie/store-selection IDs, or account-specific identifiers as `source_product_id` for grocery prices.

### Stop Conditions

- Stop on `www.kaufland.sk` verification, CAPTCHA, JavaScript/cookie challenge, marketplace terms access behind verification, or any bot-protection page.
- Stop before account registration, login, Kaufland Card activation, coupon activation, personalized coupons, digital receipts, app-only offer alarms, shopping-list APIs, newsletter/WhatsApp enrollment, cart/checkout, payment, or customer-specific marketplace flows.
- Stop before selecting/changing a store, using current-location detection, relying on persisted store cookies, or comparing regions without explicit human approval.
- Stop before treating leaflet/store-offer prices, Kaufland Card prices, app/coupon prices, marketplace prices, or press-release price claims as ordinary national grocery shelf prices.
- Stop before storage. This task is documentation-only discovery.

### Go/No-Go For Dry-Run Scraper Implementation

No-go for a grocery shelf-price dry-run scraper against `www.kaufland.sk`: the host and marketplace terms returned verification/bot-protection pages, and no public no-location grocery price surface was confirmed.

No-go for stored scraping or broad scraping from any Kaufland Slovakia surface.

Conditional go only for a future no-storage leaflet/offer dry run on `predajne.kaufland.sk` if all of these are true:

- The task is explicitly scoped to leaflet/store-offer prices, not regular national grocery shelf prices.
- A human approves the exact store/location policy before the run, or the run is explicitly labeled as default-store/public-context observation only.
- The scraper avoids `www.kaufland.sk`, account/app/loyalty-specific flows, bot-protected pages, disallowed asset paths, store-changing flows, and any personal/session-specific endpoints.
- The run is capped to one offer page or one category group with at most three products, no storage, and at least a 2-second delay plus jitter for any scripted page loads.
- Output keeps regular offer price, old price, unit price, package size, category, store/location context, Kaufland Card labels, missing IDs, and uncertainty separate.

## Required Discovery Before Implementation

Start URL: `https://www.kaufland.sk/`

Use `docs/retailer-discovery-checklist.md` with these Kaufland Slovakia-specific questions:

- Price availability: confirm whether the Slovak site exposes online grocery product prices, leaflet/offer prices, marketplace prices, or only store information.
- Product scope: separate grocery products from non-grocery marketplace listings if search or category pages mix them.
- Location dependence: record whether prices depend on selected store, region, local leaflet, postal code, or app context.
- Promotion flags: capture public promotions separately from Kaufland Card, app-only, leaflet-only, or region-specific prices.
- Source IDs: prefer stable product IDs from URLs or public payloads; record when only offer/flyer IDs are available.
- Robots and terms notes: check `robots.txt`, terms/help pages, and online-shop or leaflet guidance before scripted dry runs.

## Low-Volume Discovery Limits

- Categories/pages: at most 1 or 2.
- Products captured: at most 3.
- Location context: no store or region unless a human explicitly approves a documented test context.
- Delay for any later scripted page loads: at least 2 seconds plus jitter.

## Stop Conditions

Stop before dry-run implementation or storage if Kaufland Slovakia requires login, account-specific API calls, store/region selection, app access, CAPTCHA, bot challenge, legal review, or cannot clearly distinguish grocery prices from marketplace, leaflet, loyalty, or region-specific prices.

## Planned Task Sequence

1. Complete documentation-only discovery and update this note with sample products and product-surface classification.
2. If a public grocery price surface is usable, implement a low-volume dry-run scraper with no storage.
3. If dry-run output is reviewed and store/legal policy is explicit, plan a one-category or one-page, three-product stored validation.
4. Normalize and report only the approved stored run, including price-surface type, location context, missing fields, duplicate source IDs, suspicious prices, and promotion caveats.
