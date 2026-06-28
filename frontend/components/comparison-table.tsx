"use client";

import { useMemo, useState } from "react";
import type { RetailerOffer } from "../data/sample-offers";

type SortKey = "product" | "retailer" | "price" | "unitPrice" | "lastSeen";

type ComparisonTableProps = {
  offers: RetailerOffer[];
};

const allRetailers = "All retailers";
const allCategories = "All categories";

const currencyFormatter = new Intl.NumberFormat("en-AT", {
  style: "currency",
  currency: "EUR",
});

const dateFormatter = new Intl.DateTimeFormat("en-AT", {
  dateStyle: "medium",
});

export function ComparisonTable({ offers }: ComparisonTableProps) {
  const [query, setQuery] = useState("");
  const [retailer, setRetailer] = useState(allRetailers);
  const [category, setCategory] = useState(allCategories);
  const [sortKey, setSortKey] = useState<SortKey>("unitPrice");

  const retailers = useMemo(
    () => [allRetailers, ...Array.from(new Set(offers.map((offer) => offer.retailer))).sort()],
    [offers],
  );
  const categories = useMemo(
    () => [allCategories, ...Array.from(new Set(offers.map((offer) => offer.category))).sort()],
    [offers],
  );

  const filteredOffers = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    return offers
      .filter((offer) => {
        const matchesRetailer = retailer === allRetailers || offer.retailer === retailer;
        const matchesCategory = category === allCategories || offer.category === category;
        const searchableText = [
          offer.product,
          offer.brand,
          offer.retailer,
          offer.category,
          offer.packageSize,
          offer.promotion ?? "",
        ]
          .join(" ")
          .toLowerCase();

        return (
          matchesRetailer &&
          matchesCategory &&
          (normalizedQuery.length === 0 || searchableText.includes(normalizedQuery))
        );
      })
      .sort((firstOffer, secondOffer) => {
        if (sortKey === "price" || sortKey === "unitPrice") {
          return firstOffer[sortKey] - secondOffer[sortKey];
        }

        return String(firstOffer[sortKey]).localeCompare(String(secondOffer[sortKey]));
      });
  }, [category, offers, query, retailer, sortKey]);

  return (
    <section className="comparison-card" aria-labelledby="comparison-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Static sample data</p>
          <h2 id="comparison-title">Comparison table</h2>
        </div>
        <p className="result-count">
          Showing {filteredOffers.length} of {offers.length} offers
        </p>
      </div>

      <div className="filters" aria-label="Filter comparison offers">
        <label>
          Search products
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Try milk, BILLA, coffee..."
          />
        </label>

        <label>
          Retailer
          <select value={retailer} onChange={(event) => setRetailer(event.target.value)}>
            {retailers.map((retailerName) => (
              <option key={retailerName}>{retailerName}</option>
            ))}
          </select>
        </label>

        <label>
          Category
          <select value={category} onChange={(event) => setCategory(event.target.value)}>
            {categories.map((categoryName) => (
              <option key={categoryName}>{categoryName}</option>
            ))}
          </select>
        </label>

        <label>
          Sort by
          <select value={sortKey} onChange={(event) => setSortKey(event.target.value as SortKey)}>
            <option value="unitPrice">Unit price</option>
            <option value="price">Shelf price</option>
            <option value="product">Product</option>
            <option value="retailer">Retailer</option>
            <option value="lastSeen">Last seen</option>
          </select>
        </label>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th scope="col">Product</th>
              <th scope="col">Retailer</th>
              <th scope="col">Package</th>
              <th scope="col">Shelf price</th>
              <th scope="col">Unit price</th>
              <th scope="col">Promotion</th>
              <th scope="col">Last seen</th>
              <th scope="col">Source</th>
            </tr>
          </thead>
          <tbody>
            {filteredOffers.map((offer) => (
              <tr key={offer.id}>
                <td>
                  <strong>{offer.product}</strong>
                  <span>{offer.brand}</span>
                </td>
                <td>
                  <span className="retailer-pill">{offer.retailer}</span>
                  <span>{offer.category}</span>
                </td>
                <td>{offer.packageSize}</td>
                <td>{currencyFormatter.format(offer.price)}</td>
                <td>
                  {currencyFormatter.format(offer.unitPrice)} / {offer.unit}
                </td>
                <td>{offer.promotion ?? "None"}</td>
                <td>{dateFormatter.format(new Date(offer.lastSeen))}</td>
                <td>
                  <a href={offer.sourceUrl} target="_blank" rel="noreferrer">
                    Open
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {filteredOffers.length === 0 ? (
          <p className="empty-state">No sample offers match the current filters.</p>
        ) : null}
      </div>
    </section>
  );
}
