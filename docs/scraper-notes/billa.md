# BILLA Scraper Notes

## 2026-06-28 Dry Scrape Validation

Command:

```bash
python scripts/scrape_once.py --retailer billa --limit-categories 1 --max-products 3
```

Result: the low-volume dry run returned one category, `Neu im Online Shop`, and three product payloads without using `--store`.

Sample products:

- Kinder Bueno Cone Classic: `3,99 €`, `1 Liter 10,84 €`, `368 ml Packung`, source `https://shop.billa.at/produkte/kinder-bueno-cone-classic-00571232?from=plp`.
- Clever Schlögel Steaks mariniert: `9,99 €`, no extracted unit price, `Ab 0,6 kg Packung`, source `https://shop.billa.at/produkte/clever-schloegel-steaks-mariniert-00720106?from=plp`.
- Clever Spareribs: `9,99 €`, no extracted unit price, `Ab 0,6 kg Packung`, source `https://shop.billa.at/produkte/clever-spareribs-00724508?from=plp`.

Plausibility notes:

- Category name, category URL, product names, EUR prices, package sizes, product URLs, and source product IDs were present.
- Raw payloads were compact and useful for audit/debugging: each product included `category_url` and `card_text`.
- Unit price extraction worked for the packaged ice cream sample. The two variable-weight meat samples had raw text ending in `per 1 kg`, but no numeric unit price was present in the sample text, so `unit_price` remained empty.
- No large scrape output was stored in the repository.
