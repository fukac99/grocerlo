import { GrocerloDataLoader } from "../components/grocerlo-data-loader";

export default function Home() {
  return (
    <main className="page-shell">
      <section className="hero" aria-labelledby="page-title">
        <p className="eyebrow">Grocerlo</p>
        <div className="hero-grid">
          <div>
            <h1 id="page-title">Compare grocery prices clearly.</h1>
            <p className="hero-copy">
              Grocerlo keeps the comparison calm: start with products, packages,
              retailer prices, and savings, then open the source details only
              when you need them.
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
