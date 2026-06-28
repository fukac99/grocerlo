# Grocery Price Comparison App Plan

## Goal

Build a lightweight app to compare supermarket prices between Germany, Austria, and Slovakia.

The app should:

1. Scrape product data from online supermarket shops.
2. Store raw scraped data in a database.
3. Normalize and reconcile products that are likely the same across retailers.
4. Provide a searchable, filterable comparison table.

Initial scope should focus on one-off scraping. Recurring scrapes can be added later once the data model and scraping pipeline are stable.

## Target Retailers

Germany:

- REWE: https://www.rewe.de/shop/

Austria:

- BILLA: https://shop.billa.at/kategorie
- MPREIS: https://www.mpreis.at/

Slovakia:

- Kaufland: https://www.kaufland.sk/
- Tesco: https://potravinydomov.itesco.sk/shop/en-SK/landing/groceries

## Recommended Tech Stack

For a small but serious first version:

- Backend: Python
- Scraping: Playwright for dynamic sites, with BeautifulSoup or lxml where static HTML is enough
- Database: PostgreSQL
- ORM and migrations: SQLAlchemy plus Alembic
- API: FastAPI
- Frontend: Next.js
- Search: PostgreSQL full-text search, with optional `pg_trgm` fuzzy search later
- Local environment: Docker Compose

This stack keeps the scraping and data processing simple while still leaving room for a proper web app and recurring scraping later.

## Suggested Repository Structure

```text
grocery-saver/
  backend/
    app/
      api/
      db/
      models/
      scrapers/
      normalization/
      matching/
    alembic/
  frontend/
  scripts/
    scrape_once.py
    reconcile_once.py
  docker-compose.yml
  README.md
```

Core responsibilities:

- `scrapers`: source-specific scraping logic
- `db`: database models, sessions, and migrations
- `normalization`: currency, unit, size, packaging, and text cleanup
- `matching`: product reconciliation logic
- `api`: serves product and comparison data
- `frontend`: search, filters, and comparison table

## Data Model

The app should store both raw scraped data and normalized product data. Raw data makes scraper bugs debuggable and allows reprocessing without scraping again.

### Scrape Runs

```text
scrape_runs
  id
  retailer
  country
  started_at
  finished_at
  status
  scraper_version
  source_url
  error_message
```

### Raw Products

```text
raw_products
  id
  scrape_run_id
  retailer
  country
  source_product_id
  source_url
  raw_name
  raw_brand
  raw_category
  raw_price
  raw_old_price
  raw_unit_price
  raw_package_size
  raw_currency
  raw_availability
  raw_promotion_text
  raw_payload_json
  scraped_at
```

`raw_payload_json` should preserve source-specific details that do not fit cleanly into shared columns.

### Retailer Products

```text
retailer_products
  id
  raw_product_id
  retailer
  country
  source_product_id
  product_url
  name
  brand
  category
  price_amount
  currency
  unit_price_amount
  unit_price_unit
  package_quantity
  package_unit
  normalized_quantity_base
  normalized_unit_base
  price_per_base_unit
  is_promotion
  promotion_type
  availability
  observed_at
```

Examples:

- `500 g` becomes `0.5 kg`
- `1.5 liter` becomes `1.5 l`
- `100 g 1,25 EUR` becomes `12.50 EUR/kg`
- `1 Liter 1,89 EUR` becomes `1.89 EUR/l`

### Canonical Products

```text
canonical_products
  id
  canonical_name
  canonical_brand
  category
  created_at
```

### Product Matches

```text
product_matches
  id
  canonical_product_id
  retailer_product_id
  match_confidence
  match_method
  reviewed_status
  created_at
```

Suggested `reviewed_status` values:

- `unreviewed`
- `accepted`
- `rejected`
- `manual`

## Scraping Strategy

Each retailer should have its own scraper adapter behind a shared interface.

```python
class RetailerScraper:
    retailer: str
    country: str

    async def scrape_categories(self) -> list[Category]:
        ...

    async def scrape_products(self, category: Category) -> list[RawProduct]:
        ...
```

Scrapers should extract data, not fully interpret it. Normalization should happen in a separate step.

The shared scraper output should look roughly like this:

```python
RawProduct(
    retailer="billa",
    country="AT",
    source_url="...",
    source_product_id="...",
    name="Ja! Natürlich Bananen",
    brand="Ja! Natürlich",
    category="Obst & Gemüse",
    price="2,39 EUR",
    unit_price="per 1 kg",
    package_size="Ab 0,5 kg",
    promotion_text=None,
    raw_payload={...},
)
```

## Retailer Notes

### BILLA Austria

BILLA is a good first target because the category listing exposes product names, prices, unit prices, promotions, tags, and pagination.

Initial BILLA tasks:

- Discover category URLs.
- Scrape product cards from category pages.
- Follow pagination.
- Extract product name, brand if available, package size, price, unit price, promotion, category, and source URL.
- Store raw data first.
- Normalize prices and units after storage.

### MPREIS Austria

MPREIS exposes product and promotion information on the website, but many offers appear to be app-only or store-dependent.

Important fields:

- Regular price
- Promotional price
- App-only indicator
- Store availability text
- Unit price
- Category

The scraper should distinguish normal prices from promotion-only prices.

### REWE Germany

REWE may require a selected delivery or pickup market. Prices can be location-dependent.

Important considerations:

- Record selected store or region context if required.
- Store location-specific metadata in `raw_payload_json`.
- Avoid mixing prices from different locations without recording the context.

### Kaufland Slovakia

Kaufland needs discovery work to determine whether product prices are online-shop prices, leaflet prices, or store-dependent prices.

Important considerations:

- Identify category and product listing pages.
- Check whether prices are location-specific.
- Store promotion and leaflet metadata separately when present.

### Tesco Slovakia

Tesco online groceries are likely dynamic and may require Playwright.

Important considerations:

- Determine whether location/session setup is required.
- Scrape category listings first.
- Preserve Tesco-specific fields in `raw_payload_json`.

## One-Off Scrape Pipeline

Start with CLI commands:

```bash
python scripts/scrape_once.py --retailer billa
python scripts/scrape_once.py --retailer mpreis
python scripts/scrape_once.py --all
```

Pipeline:

1. Create a `scrape_runs` row.
2. Visit category pages.
3. Paginate through product listings.
4. Extract product cards.
5. Save rows to `raw_products`.
6. Normalize raw rows into `retailer_products`.
7. Mark the scrape run as successful or failed.

Each run should create new observations instead of overwriting prior runs. This makes historical price tracking possible later.

## Normalization Plan

Normalization should happen after raw scraping and before matching.

Main tasks:

- Parse currencies such as `EUR` and `€`.
- Parse decimal commas such as `2,39` into `2.39`.
- Parse package units such as `g`, `kg`, `ml`, `l`, `stk`, `piece`, and `Packung`.
- Convert package sizes to base units.
- Convert unit prices to comparable units like `EUR/kg`, `EUR/l`, or `EUR/piece`.
- Extract brand when available.
- Normalize text for matching while preserving original display names.
- Detect promotions such as `in Aktion`, `2+1`, `1+1 gratis`, `ab 2 billiger`, and app-only offers.

Avoid currency conversion initially because Germany, Austria, and Slovakia all use EUR.

## Product Reconciliation Plan

Product matching should be incremental and explainable.

### Version 1: Rule-Based Matching

Start with deterministic scoring using:

- Product name similarity
- Brand equality
- Package size equality
- Category similarity
- Unit compatibility
- Price sanity checks

Example score:

```text
brand exact match: +30
name token similarity high: +40
same package quantity/unit: +20
same category family: +10
conflicting package size: -30
conflicting brand: -40
```

Suggested thresholds:

```text
>= 85: auto-match
60-84: candidate match, needs review
< 60: no match
```

Examples that may match:

```text
Coca Cola Zero 1,5 liter Flasche
Coca-Cola Zero Sugar 1.5L
Coca Cola Zero 1,5 l
```

Examples that should probably not match:

```text
Clever Vollmilch 3.5% 1 liter
Ja! Natürlich Vollmilch 3.5% 1 liter
BILLA Bio Vollmilch 3.5% 1 liter
```

Examples that need careful handling:

```text
Bananas per kg
Organic bananas per kg
Loose bananas from Austria
```

### Version 2: Embedding-Assisted Matching

After enough product data exists, add semantic matching:

- Use multilingual embeddings for product names.
- Generate candidates with vector similarity.
- Keep final scoring grounded in brand, package size, and category.
- Store the match method as `rules`, `embedding`, or `manual`.

## API Plan

Expose a small API for the frontend.

Useful endpoints:

```text
GET /retailers
GET /countries
GET /categories
GET /products/search?q=milk
GET /comparison?query=milk&countries=AT,DE,SK&retailers=billa,rewe
GET /canonical-products/{id}
```

Example comparison response:

```json
{
  "canonicalProduct": {
    "id": "123",
    "name": "Coca Cola Zero 1.5L",
    "brand": "Coca Cola",
    "category": "Drinks"
  },
  "offers": [
    {
      "retailer": "BILLA",
      "country": "AT",
      "price": 2.49,
      "currency": "EUR",
      "unitPrice": 1.66,
      "unit": "l",
      "promotion": null,
      "observedAt": "2026-06-27"
    }
  ]
}
```

## UI Plan

The first UI should be a searchable comparison table.

Core features:

- Search box
- Retailer filter
- Country filter
- Category filter
- Promotion-only toggle
- Sort by product name
- Sort by cheapest unit price
- Sort by country
- Sort by retailer
- Sort by scrape date

Suggested table columns:

- Product
- Brand
- Package size
- Country
- Retailer
- Price
- Unit price
- Promotion
- Last seen
- Source link

Later additions:

- Matched-products-only toggle
- Unmatched-products view
- Manual match review screen
- Price history chart
- Basket comparison

## Recurring Scrapes Later

Do not build scheduling first, but design for it from the start.

Later scheduling options:

- cron
- GitHub Actions
- Celery Beat
- Prefect
- scheduled container

Useful future table:

```text
price_observations
  id
  retailer_product_key
  price_amount
  unit_price_amount
  promotion_text
  observed_at
  scrape_run_id
```

This would enable price history without duplicating product metadata too much.

## Legal And Operational Considerations

Scraping supermarket websites has operational and legal risks.

The scraper should:

- Check `robots.txt` and site terms before scraping.
- Keep request rates conservative.
- Avoid authenticated scraping unless explicitly needed.
- Avoid bypassing anti-bot systems.
- Cache pages during development.
- Record source URLs and scrape timestamps.
- Track whether prices are location-dependent.

For the first version, use low-volume one-off scrapes.

## Milestones

### Milestone 1: Foundation

- Set up repo structure.
- Add Docker Compose with PostgreSQL.
- Create initial database schema and migrations.
- Add scraper interface.
- Add CLI command framework.

### Milestone 2: First Retailer, BILLA

- Scrape BILLA categories and product listings.
- Store raw products.
- Normalize prices, package sizes, and unit prices.
- Add basic search endpoint.

### Milestone 3: UI V1

- Build simple comparison table.
- Add search and filters.
- Show source links.
- Show raw and normalized price fields where useful.

### Milestone 4: Add More Retailers

- Add MPREIS.
- Add REWE.
- Add Kaufland Slovakia.
- Add Tesco Slovakia.
- Track scraper limitations per retailer.

### Milestone 5: Matching V1

- Add rule-based product matching.
- Create canonical product groups.
- Store confidence scores.
- Expose comparison API grouped by canonical product.

### Milestone 6: Review And Improve

- Add manual match correction.
- Improve normalization.
- Add embedding-assisted matching if useful.
- Add price history.
- Add recurring scrape scheduler.

## Recommended First Build Order

1. Create the database schema.
2. Implement the scraper interface.
3. Build the BILLA scraper first.
4. Store raw BILLA product data.
5. Normalize BILLA prices and units.
6. Build a minimal table UI against BILLA only.
7. Add MPREIS.
8. Add matching between BILLA and MPREIS.
9. Expand to Germany and Slovakia.

This order produces a useful working app early while still moving toward the full cross-country comparison system.
