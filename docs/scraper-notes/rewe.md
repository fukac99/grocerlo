# REWE Scraper Notes

## Status

REWE is discovery-only. Do not implement runtime scraping, store rows, select a market, authenticate, or use account/session-specific flows until the discovery checklist is completed and the location policy is explicit.

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
