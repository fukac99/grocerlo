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
