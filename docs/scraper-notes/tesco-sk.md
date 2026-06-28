# Tesco Slovakia Scraper Notes

## Status

Tesco Slovakia is discovery-only. Do not implement runtime scraping, store rows, select a delivery address/slot, authenticate, or use account/session-specific flows until discovery proves which public grocery price surface is safe to use.

## Required Discovery Before Implementation

Start URL: `https://potravinydomov.itesco.sk/shop/en-SK/landing/groceries`

Use `docs/retailer-discovery-checklist.md` with these Tesco Slovakia-specific questions:

- Price availability: confirm whether numeric prices appear before delivery address, postal code, store, or delivery slot selection.
- Location/session dependence: record selected language, country, and whether price, availability, source URL, or product IDs change after any approved location context.
- Dynamic behavior: document whether category/listing data is available in static HTML, embedded public JSON, or public network payloads and whether Playwright is required.
- Promotion flags: capture Clubcard, multibuy, coupon, and app-only labels separately from regular prices.
- Source IDs: prefer stable Tesco product IDs from URLs or public payloads; record if price or availability IDs change by selected context.
- Robots and terms notes: check `robots.txt`, terms/help pages, and online grocery guidance before scripted dry runs.

## Low-Volume Discovery Limits

- Categories/pages: at most 1 or 2.
- Products captured: at most 3.
- Location context: no address, postal code, store, or delivery slot unless a human explicitly approves a documented test context.
- Delay for any later scripted page loads: at least 2 seconds plus jitter.

## Stop Conditions

Stop before dry-run implementation or storage if Tesco Slovakia requires login, account-specific API calls, delivery address, postal code, store, delivery slot, CAPTCHA, bot challenge, legal review, or unclear separation between regular and Clubcard/member/app prices.

## Planned Task Sequence

1. Complete documentation-only discovery and update this note with sample products, dynamic-loading notes, and policy blockers.
2. If public no-location prices are usable, implement a low-volume dry-run scraper with no storage.
3. If dry-run output is reviewed and location/legal policy is explicit, plan a one-category, three-product stored validation.
4. Normalize and report only the approved stored run, including language/location context, missing fields, duplicate source IDs, suspicious prices, and promotion caveats.
