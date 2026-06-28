# Tesco Slovakia Scraper Notes

## Status

Tesco Slovakia remains discovery-only after the 2026-06-28 public discovery pass. Do not implement runtime scraping, store rows, select a delivery address/slot, authenticate, or use account/session-specific flows.

Dry-run scraper decision: **No-Go**. Tesco's public online shopping terms say current goods prices are listed after a registered customer logs in, and the public shopping guide says users register/sign in and book a slot before shopping for the most accurate availability and offers. Direct low-volume product-page checks returned a protection/privacy interstitial instead of product data, so a dry-run scraper would either need browser automation against a protected dynamic surface or account/location context that is outside this task.

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

Discovery performed 2026-06-28 23:34-23:55 UTC+2:

- Checked `robots.txt`, one grocery landing page, one online-shopping guide page, the online shopping terms page, one Clubcard coupon help page, the product sitemap index URL, and three product URL candidates.
- Did not log in, register, enter a postal code/address, choose a store, book a delivery or Click+Collect slot, accept invasive tracking prompts, or bypass protection.
- No application storage or scraper code was added.

## Robots, Terms, And Help URLs Checked

- `https://potravinydomov.itesco.sk/robots.txt`
  - Lists grocery product and promotion sitemap URLs.
  - Disallows login/register paths, queued/tokenized URLs, modal/tab parameter variants, offset pagination variants, and several parameterized grocery paths.
  - Does not by itself make product scraping acceptable; product pages still returned a protection interstitial during direct checks.
- `https://potravinydomov.itesco.sk/shop/en-SK/landing/groceries`
  - Public landing/search-visible page. Copy emphasizes signing in to start shopping, Clubcard prices, app use, Tesco Online Club, and delivery/Click+Collect.
- `https://potravinydomov.itesco.sk/shop/en-SK/zone/ako-nakupovat-online`
  - Public guide says online shopping starts with registration/sign-in, then booking a delivery slot, then adding products. It also says to book a slot first to see the most accurate availability and offers.
- `https://www.tesco.sk/help/en-SK/pages/documents/terms-and-conditions/terms-and-conditions-of-tesco-online-shopping`
  - Terms say the service presents goods on the Website and lets the customer create a shopping list after registration and login.
  - Terms say creating a shopping list and ordering delivery require registration with exact delivery address, phone, email, and password.
  - Terms say the current price of goods is listed on the Website after the registered customer logs in to their account.
  - Terms say product availability depends on the serving store on the day of delivery.
- `https://www.tesco.sk/help/en-SK/pages/online-shopping/clubcard/how-to-use-clubcard-vouchers-and-coupons-online`
  - Clubcard coupons are account/wallet and checkout dependent. Vouchers can be applied in the online shopping basket or online shopping app.
- `https://potravinydomov.itesco.sk/sitemaps/sk-SK/groceries/products-index.xml`
  - Advertised in `robots.txt`, but a low-volume direct request returned `403 Forbidden`; WebFetch also timed out.
- `https://potravinydomov.itesco.sk/sitemaps/sk-SK/groceries/promotions-index.xml`
  - Advertised in `robots.txt`, but WebFetch returned `403 Forbidden`.

## Price, Location, And Session Findings

- Prices: **Do not rely on no-location public prices.** Search snippets exposed a few product prices or promotion fragments, but Tesco's terms state current prices are available after registered login. Direct product-page fetches did not return price data.
- Address/postal code/store/slot: **Required or materially relevant for shopping data.** Registration requires an exact delivery address, and the shopping guide says users book a delivery slot before adding products to get the most accurate availability and offers. Terms also tie availability to the serving store on the delivery day.
- Login: **Required for current prices and shopping-list/order flow** per the terms.
- Availability: **Store/slot dependent.** Public snippets can expose product information, but terms say availability may differ by the serving store and delivery day.
- Safe public sample data: only search-indexed snippets and landing/help text were observed. No verified direct product payload with current price, availability, or add-to-basket state was safely accessible without protection/login/location context.

## Dynamic Payload And Playwright Notes

- Static/direct HTTP checks are insufficient for scraper implementation:
  - Grocery and help pages are dynamic; WebFetch could render help/landing text, while plain direct requests returned `403 Forbidden` for grocery-domain pages.
  - Direct product-page WebFetch requests returned only `Powered and protected by` / `Privacy`, indicating a protection interstitial rather than usable public product payload.
  - The online shopping terms list JavaScript, cookies, pop-up support, and an active email address as technical requirements for service use.
- Playwright may be required to manually inspect the rendered product surface, but using it for an automated dry run would still face the same blockers: login, address/slot context, cookies, and bot/protection handling. Do not add Playwright scraper code until legal/product policy explicitly approves a test context and access method.

## Public Sample Product Candidates

These are capped at three and are recorded only as public search-indexed candidates. They were not accepted as scraper-ready samples because direct product-page fetches returned a protection interstitial.

| Field | Sample 1 | Sample 2 | Sample 3 |
| --- | --- | --- | --- |
| `retailer` | `tesco_sk` | `tesco_sk` | `tesco_sk` |
| `country` | `SK` | `SK` | `SK` |
| `source_product_id` | `2002017071699` | `2002121558377` | `2002121250654` |
| `source_url` | `https://potravinydomov.itesco.sk/shop/en-SK/products/2002017071699` | `https://potravinydomov.itesco.sk/shop/en-SK/products/2002121558377` | `https://potravinydomov.itesco.sk/groceries/en-SK/products/2002121250654` |
| `category` | Unknown from safe public snippet | Unknown from safe public snippet | Unknown from safe public snippet |
| `raw_name` | `Tuc Mini Crackers with Smoky Bacon Flavour 100 g` | `Guinness Draught Stout 4.2 % 440 ml` | `Tesco Light Bread 450 g` |
| `raw_brand` | Not separately displayed in snippet | Guinness | Tesco |
| `raw_price` | `0,99 € Clubcard Price` from search snippet only | `1,91 € Clubcard Price` from search snippet only | Not exposed in safe snippet |
| `raw_old_price` | Not observed | Not observed | Not observed |
| `raw_unit_price` | `9,90 €/kg` from search snippet only | `4,34 €/litre + Deposit` from search snippet only | Not exposed in safe snippet |
| `raw_package_size` | `100 g` | `440 ml` | `450 g`; search snippet also showed `Pack size: 0.45kg` |
| `raw_currency` | `€` | `€` | Not observed |
| `raw_availability` | Not observed | Not observed | Not observed |
| `raw_promotion_text` | `Clubcard Price`; `Promotion valid until 12/05/2026` from search snippet only | `Clubcard Price`; `Promotion valid until 19/05/2026` from search snippet only | Not observed |
| `location_context` | No location selected | No location selected | No location selected |
| `observed_at` | 2026-06-28 23:34-23:55 UTC+2 | 2026-06-28 23:34-23:55 UTC+2 | 2026-06-28 23:34-23:55 UTC+2 |
| `raw_payload_notes` | Search-indexed snippet only; direct page returned protection interstitial | Search-indexed snippet only; direct page returned protection interstitial | Search-indexed snippet only; direct page returned protection interstitial |

## Source ID Candidates

- Primary candidate: numeric product ID at the end of Tesco product URLs, for example `2002017071699`, `2002121558377`, or `2002121250654`.
- Candidate URL shapes:
  - `https://potravinydomov.itesco.sk/shop/en-SK/products/{source_product_id}`
  - `https://potravinydomov.itesco.sk/groceries/en-SK/products/{source_product_id}`
- Do not assume these IDs are sufficient for price or availability identity. Terms indicate availability depends on the serving store/day, and the page surface may use separate session, basket, promotion, offer, or fulfillment identifiers after login/location selection.

## Clubcard, App, And Promotion Labels

- Clubcard labels observed in public copy/snippets: `Clubcard prices`, `Clubcard Price`, Clubcard coupons, Clubcard vouchers, and Clubcard-linked account registration.
- App labels observed in public copy: Online Shopping mobile app and Clubcard app; voucher codes may be copied from the Clubcard app into the online shopping app.
- Tesco Online Club is separate from Clubcard and is described as a membership for delivery-fee and other benefits.
- Treat Clubcard prices, coupons, vouchers, Online Club benefits, multibuy/discount labels, app-only copy, and regular shelf/current prices as separate fields in any future approved discovery.

## Go/No-Go For Dry-Run Scraper

No-Go for implementation now.

- Current prices require registered login according to Tesco's own terms.
- Accurate availability/offers require delivery slot context according to the public shopping guide, and availability is serving-store/day dependent according to the terms.
- Direct public product-page and sitemap checks were blocked or protected at low volume.
- Search snippets are useful for human discovery only; they are not a stable, authorized, or complete product/price payload for scraper implementation.
- Next step, if the project still wants Tesco Slovakia, is a policy/legal review and an explicitly approved manual test context before any Playwright or API inspection. Keep any future task dry-run-only with no storage until that context is approved.

## Stop Conditions

Stop before dry-run implementation or storage if Tesco Slovakia requires login, account-specific API calls, delivery address, postal code, store, delivery slot, CAPTCHA, bot challenge, legal review, or unclear separation between regular and Clubcard/member/app prices.

## Planned Task Sequence

1. Complete documentation-only discovery and update this note with sample products, dynamic-loading notes, and policy blockers.
2. If public no-location prices are usable, implement a low-volume dry-run scraper with no storage.
3. If dry-run output is reviewed and location/legal policy is explicit, plan a one-category, three-product stored validation.
4. Normalize and report only the approved stored run, including language/location context, missing fields, duplicate source IDs, suspicious prices, and promotion caveats.
