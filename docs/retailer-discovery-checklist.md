# Retailer Expansion Discovery Checklist

Use this checklist before adding or extending a scraper for MPREIS, REWE, Kaufland, or Tesco. The goal is to understand the retailer's public product surface with a small, repeatable manual or dry-run discovery pass before writing runtime scraping code.

Do not run a broad scrape during discovery. Stop when prices require an account, a location decision, an app-only flow, a bot challenge, or legal/terms review.

## Low-Volume Discovery Procedure

1. Open the retailer's target start URL from `PRICE_COMPARISON_APP_PLAN.md`.
2. Check `robots.txt`, linked terms, and any site guidance that applies to automated access. Record URLs checked and any uncertainty.
3. Browse one or two grocery categories manually and capture at most three product examples.
4. Open one product detail page for each sample when available.
5. Repeat the same product/category view with no location selected and, if the site prompts for it, with one documented test location selected.
6. Record whether prices, availability, promotions, and product URLs changed after location selection.
7. Inspect page HTML or network payloads only enough to identify stable source IDs and field locations.
8. Do not authenticate, bypass challenges, accept invasive tracking prompts, or increase volume without explicit approval.

Recommended first-pass limits:

- Maximum categories: 1 or 2.
- Maximum products: 3 per retailer.
- Maximum page loads: enough to confirm list page, product page, and location behavior.
- Delay between automated page loads, if any script is used later: at least 2 seconds plus jitter.
- User agent and headers: keep defaults unless a human approves a documented reason.

## Required Discovery Notes

Create or update the retailer's scraper note before implementation with these findings. Current note files are `docs/scraper-notes/mpreis.md`, `docs/scraper-notes/rewe.md`, `docs/scraper-notes/kaufland-sk.md`, and `docs/scraper-notes/tesco-sk.md`.

- Price availability: whether list pages and product pages show numeric prices before login and before location selection.
- Location dependence: whether prices or availability require country, postal code, store, pickup branch, delivery area, or delivery slot.
- Promotions and app-only flags: whether discounts are public, loyalty/member-only, coupon-based, Clubcard/PAYBACK/app-only, or shown only after account selection.
- Source IDs: the most stable product identifier found in URLs, embedded JSON, HTML attributes, or network payloads.
- Robots and terms notes: `robots.txt` URL checked, terms/help pages checked, and any unresolved concern.
- Low-volume limits: the exact categories, product count, and request/page-load limits used during discovery.
- Fields captured: the sample product fields listed below, including raw text when a value cannot be parsed confidently.
- Stop conditions: any login wall, location wall, bot challenge, unclear terms, or account-specific pricing behavior.

## Fields To Capture

For each sample product, capture these fields where visible:

| Field | Notes |
| --- | --- |
| `retailer` | Stable lowercase retailer key, for example `mpreis`, `rewe`, `kaufland_sk`, or `tesco_sk`. |
| `country` | ISO-like project value such as `AT`, `DE`, or `SK`. |
| `source_product_id` | Prefer stable product IDs from URLs or payloads over display names. |
| `source_url` | Final canonical product URL, without tracking parameters when possible. |
| `category` | Category name and URL or breadcrumb. |
| `raw_name` | Product title exactly as shown. |
| `raw_brand` | Brand when displayed separately; otherwise leave empty and preserve full title. |
| `raw_price` | Displayed current price text, including decimal separator and currency. |
| `raw_old_price` | Strikethrough or previous price, if shown. |
| `raw_unit_price` | Price per kg, liter, piece, or package as displayed. |
| `raw_package_size` | Package size, variable-weight wording, multipack count, or deposit text. |
| `raw_currency` | Currency symbol or code. |
| `raw_availability` | In stock, unavailable, delivery-only, pickup-only, or store-specific text. |
| `raw_promotion_text` | Badge, campaign, loyalty price, coupon, or app-only wording. |
| `location_context` | No location, postal code, store, delivery area, pickup branch, or selected slot used for observation. |
| `observed_at` | Timestamp and timezone of discovery. |
| `raw_payload_notes` | Short note describing useful HTML, embedded JSON, or network payload structure. |

## Retailer-Specific Checklist

### MPREIS

Start URL: `https://www.mpreis.at/`

- Confirm whether MPREIS exposes grocery product listings with prices on the public website, or whether product and offer data is separated from online shopping.
- Check whether prices change or disappear by store, postal code, pickup location, delivery area, or regional flyer.
- Look for source IDs in product URLs, offer URLs, embedded data, or image/file names; record if only offer IDs are available.
- Capture whether promotions are normal shelf discounts, weekly offers, loyalty/app-only offers, or region-specific flyer prices.
- Note whether discovery should target product pages, category pages, search results, or offer/flyer pages for the next task.

### REWE

Start URL: `https://www.rewe.de/shop/`

- Confirm whether product prices are visible before selecting a delivery or pickup market.
- If prompted, document the exact location context needed: postal code, market, pickup, delivery, or delivery slot.
- Compare one product before and after location selection and record changes to price, availability, deposit, unit price, and source URL.
- Capture PAYBACK, coupon, member, or app-only labels separately from normal promotions.
- Prefer product IDs from URLs or embedded payloads; record whether the same product has different offer IDs under different markets.

### Kaufland Slovakia

Start URL: `https://www.kaufland.sk/`

- Confirm whether the Slovak site exposes online grocery product prices, flyer/offer prices, marketplace products, or only store information.
- Separate grocery products from non-grocery marketplace listings if both appear in search or category pages.
- Check whether prices depend on selecting a store, region, or local leaflet.
- Capture source IDs from product URLs or offer/flyer payloads and note if IDs are offer-specific rather than product-specific.
- Record whether promotions are public, Kaufland Card/app-only, leaflet-only, or region-specific.

### Tesco Slovakia

Start URL: `https://potravinydomov.itesco.sk/shop/en-SK/landing/groceries`

- Confirm whether prices are visible before selecting a delivery address, postal code, store, or delivery slot.
- Record the selected language and country context because Tesco URLs and labels may vary by locale.
- Capture Clubcard prices, multibuy promotions, coupons, and app-only labels separately from regular prices.
- Compare list page and product detail page fields for the same item, including unit price, package size, and availability.
- Prefer product IDs from Tesco URLs or embedded payloads; record if availability or price IDs change after location selection.

## Go/No-Go Before Implementation

Proceed to scraper implementation only when discovery notes answer these questions:

- Can public product and price data be viewed without login?
- Is there a documented default location strategy, or is the task explicitly scoped to no-location data?
- Are promotions and loyalty/app-only prices distinguishable from regular prices?
- Is there a stable `source_product_id` or documented fallback?
- Are robots/terms concerns recorded and acceptable for a low-volume dry run?
- Are low-volume limits and stop conditions written down for the implementation task?

If any answer is unknown, keep the retailer task in discovery instead of adding runtime scraper code.
