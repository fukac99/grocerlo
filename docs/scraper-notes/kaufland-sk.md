# Kaufland Slovakia Scraper Notes

## Status

Kaufland Slovakia is discovery-only. Do not implement runtime scraping, store rows, select a store/region, authenticate, or use app/account flows until discovery proves which public grocery price surface is safe to use.

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
