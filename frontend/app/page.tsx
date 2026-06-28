import { GrocerloDataLoader } from "../components/grocerlo-data-loader";

export default function Home() {
  return (
    <main className="page-shell">
      <section className="hero" aria-labelledby="page-title">
        <p className="eyebrow">Grocery Saver</p>
        <div className="hero-grid">
          <div>
            <h1 id="page-title">Grocerlo price comparison</h1>
            <p className="hero-copy">
              Explore normalized BILLA products from the local backend, with
              explicit source labels when the app is using live API data or
              opt-in mock samples.
            </p>
          </div>
          <div className="mock-banner live-banner" role="status">
            <strong>Real data first</strong>
            <span>
              Start the FastAPI backend locally to load scrape_run_id=2 BILLA
              rows. Mock offers appear only when sample mode is explicitly
              enabled.
            </span>
          </div>
        </div>
      </section>

      <GrocerloDataLoader />
    </main>
  );
}
