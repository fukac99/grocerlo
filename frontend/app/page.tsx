import { ComparisonTable } from "../components/comparison-table";
import { sampleOffers } from "../data/sample-offers";

export default function Home() {
  return (
    <main className="page-shell">
      <section className="hero" aria-labelledby="page-title">
        <p className="eyebrow">Grocery Saver</p>
        <div className="hero-grid">
          <div>
            <h1 id="page-title">Visual inspection shell</h1>
            <p className="hero-copy">
              Explore the intended comparison workflow with static grocery offer
              examples while backend search and matching APIs are still being
              built.
            </p>
          </div>
          <div className="mock-banner" role="status">
            <strong>Mock data only</strong>
            <span>
              This view is not connected to live scrapes, product search, or
              comparison APIs yet.
            </span>
          </div>
        </div>
      </section>

      <ComparisonTable offers={sampleOffers} />
    </main>
  );
}
