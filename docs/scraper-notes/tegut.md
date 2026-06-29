# Tegut Amazon Scraper Notes

## Status

Tegut on Amazon is discovery-only. Do not implement runtime scraping, store rows, select a postcode, authenticate, use account/session-specific Amazon flows, add products to a basket, or inspect checkout/delivery-slot payloads until a separate policy task explicitly approves the access context.

T073 low-volume discovery was completed on 2026-06-29 using the Linear issue snapshot, one direct source-page fetch attempt, Amazon robots/help pages, Amazon public press context, and public search results. No Amazon account was used, no postcode or delivery address was entered, no cart/checkout/session-specific flow was entered, no broad scraping was performed, and no product data was stored.

## T073 Amazon Grocery Price-Surface Discovery

### URLs Checked

- Source category from Linear: `https://www.amazon.de/-/en/alm/category/tegut/Brot-Backwaren?almBrandId=dGVndXQuLi4&node=358557031&ref_=BakedGoods&pf_rd_r=X0FSENXTKQ476T9WRAG9&pf_rd_p=1582a9d1-ba5f-43a7-be5e-cd7af6ef8e04&pf_rd_m=A3JWKAKR8XB7XF&pf_rd_s=zone-3-slot-3_4&pf_rd_t=&pf_rd_i=128909`
  - Direct fetch returned `404 Not Found` during this pass, so do not treat the category URL as a stable public scrape endpoint.
- Amazon robots: `https://www.amazon.de/robots.txt`
  - General disallows include account/login, cart, offer listing, product availability, promotion, local Ajax, and many account/session-like paths.
  - `/-/en/` is allowed for general user agents, but `/-/` is otherwise disallowed and several AI/crawler user agents are disallowed entirely. A future scripted task needs explicit legal/policy review before any automated Amazon access.
- Amazon grocery help: `https://www.amazon.de/-/en/gp/help/customer/display.html?nodeId=GB4P4BZ9FYDGRV6X`
  - Amazon describes Tegut on Amazon and Knuspr on Amazon as grocery services available only in eligible postcode areas.
  - Grocery orders can be placed for same-day or next-two-day delivery depending on postcode, with two-hour delivery windows subject to availability.
  - Amazon directs users to `https://www.amazon.de/lebensmittelundmehr` to check delivery availability for a postcode.
- Amazon press context: `https://press.aboutamazon.com/de/amazon-prime/2025/2/amazon-de-oeffnet-lebensmittellieferungen-von-knuspr-und-tegut-fuer-alle-kunden-und-kundinnen`
  - Tegut on Amazon is available in selected German areas and uses same-day delivery windows.
  - Prime and non-Prime customers have different minimum order and delivery-fee terms.
- Tegut online-shop FAQ search result:
  - Tegut points users to `www.amazon.de/tegut`.
  - An Amazon customer account is required to order; Prime is not required but changes minimum order and delivery-fee conditions.
  - Tegut says a reduced set of leaflet offer prices is represented in the Amazon online shop.

### Uploaded Snapshot Context

The Linear issue records an uploaded `Brot-Backwaren-0.md` snapshot, but that file is not present in the repository or clean worktree. Treat the following as issue-provided discovery context rather than independently re-fetched page data:

- The snapshot showed a Tegut/Amazon category structure with aisles such as Bakery, Dairy, Fruits & vegetables, and Pantry.
- Bread/bakery category sections included Fresh Bakery Breads, Fresh Pastries, Whole Cakes, Crispbread, Packaged Pastries, and Desserts.
- Product cards exposed Amazon product/ASIN links, seller text `tegut..`, package-size text, ratings, promotion or unavailable markers, and category grouping.
- The snapshot did not clearly expose numeric prices, so it is not sufficient evidence for price capture.

### Price Visibility Without Login Or Location

No-go for price capture without an approved account/postcode context. The live source category fetch did not return usable product data, and Amazon's public grocery help makes delivery availability postcode-dependent. Public search/help context also indicates that an Amazon account is required to order and that product availability and delivery windows depend on postcode.

Do not infer current shelf prices from category snippets, ratings, unavailable markers, press copy, delivery-fee pages, or leaflet references. Numeric prices and unit prices should be considered unverified until an approved manual context confirms they are visible without login, without a customer-specific session, and without selecting a delivery area.

### Surface Classification

- Retailer: model as `tegut` only if the project explicitly accepts Amazon-hosted grocery data as a Tegut retailer source.
- Source platform: record `amazon_de` or `amazon_fresh`/`amazon_grocery` in raw payload metadata for any future approved output.
- Marketplace semantics: requires a policy decision before implementation. Amazon controls account, postcode eligibility, basket, delivery windows, checkout, and Prime/non-Prime delivery economics, while Tegut supplies the grocery assortment. Do not mix Tegut on Amazon rows with direct Tegut store, flyer, or physical-store prices without source-platform context.
- Promotion semantics: keep Tegut leaflet offers, Amazon grocery promotions, Prime/non-Prime benefits, delivery-fee promotions, unavailable markers, and regular product prices as separate fields.

### Category And Product Field Candidates

- Category URL shape observed in the issue: `/‑/en/alm/category/tegut/<category>?almBrandId=<brand>&node=<node_id>...`
- Storefront candidate from public search context: `https://www.amazon.de/alm/storefront?almBrandId=dGVndXQuLi4`
- Product URL/ID candidate: Amazon product links with ASINs from the snapshot. Use ASIN only as an Amazon platform product identifier, not as proof of stable Tegut price identity.
- Seller candidate: snapshot seller text `tegut..`.
- Product-card fields from the snapshot: display name, ASIN/product link, seller, package-size text, ratings, promotion labels, unavailable markers, category/aisle section, and possibly image/position metadata.
- Missing or unverified fields: numeric price, old price, unit price, currency, availability for a specific delivery postcode, delivery-window availability, deposit, substitutions, and account/Prime-specific promotions.

### Stop Conditions

- Stop before login, account creation, postcode/address entry, delivery-area lookup, delivery-window selection, cart/basket actions, checkout, payment, Prime sign-up prompts, account APIs, product-availability endpoints, local Ajax endpoints, offer-listing endpoints, or promotion endpoints.
- Stop on CAPTCHA, bot challenge, 404/soft-block pages, privacy/protection interstitials, request throttling, or unclear robots/terms interpretation.
- Stop before using ratings, unavailable labels, snippet text, leaflet offer references, delivery-fee terms, or Prime/non-Prime benefits as comparable product prices.
- Stop before storage. This task is documentation-only discovery.

### Go/No-Go For Dry-Run Scraper Implementation

No-go for a price-capturing dry-run scraper now.

- Numeric product prices were not confirmed in safe public no-location context.
- Grocery availability and delivery windows are postcode-dependent.
- Ordering requires an Amazon account, and Amazon controls customer/session, cart, delivery, and Prime/non-Prime economics.
- Amazon robots disallow sensitive account/cart/availability/offer/promotion paths and disallow many crawler/AI user agents.
- The source category was not a stable public fetch target during this pass.

Conditional go only for a future documentation or manual-inspection task if all of these are true:

- A human explicitly approves the exact postcode/account/legal policy context.
- The task remains no-storage and caps inspection to one category and at most three product cards.
- Output clearly labels source platform, seller, postcode/location context, login/account context, Prime/non-Prime context, delivery-window context, regular price, unit price, promotions, unavailable markers, and missing fields.
- The implementation avoids disallowed robots paths, account/cart/checkout/product-availability APIs, bot protection, and broad category crawling.

## Required Discovery Before Implementation

Start URL candidates:

- `https://www.amazon.de/alm/storefront?almBrandId=dGVndXQuLi4`
- `https://www.amazon.de/lebensmittelundmehr`
- The issue-provided bread/bakery category URL if a human can still open it manually.

Use `docs/retailer-discovery-checklist.md` with these Tegut-specific questions:

- Price availability: confirm whether numeric prices and unit prices appear without login, postcode, delivery address, delivery window, or Prime state.
- Location dependence: record postcode, delivery area, delivery window, availability, minimum order, delivery fees, and whether product prices change by context.
- Account and platform behavior: separate Amazon account, Prime, cart, checkout, and delivery data from Tegut product fields.
- Source IDs: prefer ASIN plus seller/source-platform metadata; record if offer, fulfillment, availability, or delivery identifiers vary by context.
- Promotions: separate regular price, Tegut leaflet offer, Amazon grocery promotion, Prime benefit, coupon, unavailable marker, and delivery-fee promotion.
- Robots and terms notes: review Amazon and Tegut policy context before any scripted dry run.

## Low-Volume Discovery Limits

- Categories/pages: at most 1.
- Products captured: at most 3 cards, manually inspected.
- Location context: no postcode/address unless a human explicitly approves a documented test context.
- Account context: no login or account-specific session unless a human explicitly approves a separate policy task.
- Delay for any later approved scripted page loads: at least 2 seconds plus jitter.

## Planned Task Sequence

1. Complete documentation-only discovery and keep Tegut storage blocked.
2. Create a policy issue if the project wants to evaluate an approved postcode/account context for Amazon-hosted grocery data.
3. If policy approves, run a manual no-storage inspection of one category and at most three products.
4. Only after reviewed manual output, consider a no-storage dry-run scraper that records source platform, postcode/account context, and missing fields explicitly.
