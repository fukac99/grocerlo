# Grocery Saver Frontend

Next.js visual inspection shell for comparing grocery offers. By default, the app
loads normalized BILLA products from the local backend through a same-origin
frontend API route.

## Local Run

Install dependencies from the `frontend` directory:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open http://localhost:3000 to inspect the comparison table.

The frontend expects the FastAPI backend at `http://127.0.0.1:8000` unless
`GROCERY_API_BASE_URL` is set. It loads BILLA products with the search query
`billa` by default; set `NEXT_PUBLIC_GROCERY_BILLA_QUERY` to use another product,
brand, or category term for the local data set.

To view clearly labelled mock offers instead of backend data, run with:

```bash
NEXT_PUBLIC_GROCERY_DATA_SOURCE=sample npm run dev
```

## Checks

```bash
npm run lint
npm run build
npm run typecheck
```
