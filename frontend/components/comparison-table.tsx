"use client";

import { useMemo, useState } from "react";
import type { RetailerOffer } from "../data/sample-offers";

type SortKey = "product" | "packageSize" | "lowestPrice";
type RetailerFilterMode = "available" | "cheapest";
type ComparisonRow = {
  key: string;
  product: string;
  packageSize: string;
  category: string;
  offersByRetailer: Map<RetailerOffer["retailer"], RetailerOffer>;
  lowestPrice: number;
};

type StatusMessage = {
  tone: "info" | "error";
  title: string;
  detail: string;
};

type ComparisonTableProps = {
  offers: RetailerOffer[];
  dataSourceLabel: string;
  dataSourceDescription: string;
  statusMessage?: StatusMessage | null;
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

export function ComparisonTable({
  offers,
  dataSourceLabel,
  dataSourceDescription,
  statusMessage,
}: ComparisonTableProps) {
  const [query, setQuery] = useState("");
  const [retailer, setRetailer] = useState(allRetailers);
  const [retailerFilterMode, setRetailerFilterMode] =
    useState<RetailerFilterMode>("available");
  const [category, setCategory] = useState(allCategories);
  const [sortKey, setSortKey] = useState<SortKey>("lowestPrice");

  const retailers = useMemo(
    () => [allRetailers, ...Array.from(new Set(offers.map((offer) => offer.retailer))).sort()],
    [offers],
  );
  const categories = useMemo(
    () => [allCategories, ...Array.from(new Set(offers.map((offer) => offer.category))).sort()],
    [offers],
  );

  const comparisonRows = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    const rows = new Map<string, ComparisonRow>();

    for (const offer of offers) {
      const rowKey = `${offer.product}|${offer.packageSize}`;
      const existingRow = rows.get(rowKey);

      if (existingRow) {
        existingRow.offersByRetailer.set(offer.retailer, offer);
        existingRow.lowestPrice = Math.min(existingRow.lowestPrice, offer.price);
      } else {
        rows.set(rowKey, {
          key: rowKey,
          product: offer.product,
          packageSize: offer.packageSize,
          category: offer.category,
          offersByRetailer: new Map([[offer.retailer, offer]]),
          lowestPrice: offer.price,
        });
      }
    }

    return Array.from(rows.values())
      .filter((row) => {
        const rowOffers = Array.from(row.offersByRetailer.values());
        const selectedRetailer = retailer as RetailerOffer["retailer"];
        const selectedRetailerOffer = row.offersByRetailer.get(selectedRetailer);
        const matchesRetailer =
          retailer === allRetailers ||
          (retailerFilterMode === "cheapest"
            ? selectedRetailerOffer?.price === row.lowestPrice
            : Boolean(selectedRetailerOffer));
        const matchesCategory = category === allCategories || row.category === category;
        const searchableText = [
          row.product,
          row.packageSize,
          row.category,
          ...rowOffers.flatMap((offer) => [
            offer.retailer,
            offer.brand,
            offer.promotion ?? "",
          ]),
        ]
          .join(" ")
          .toLowerCase();

        return (
          matchesRetailer &&
          matchesCategory &&
          (normalizedQuery.length === 0 || searchableText.includes(normalizedQuery))
        );
      })
      .sort((firstRow, secondRow) => {
        if (sortKey === "lowestPrice") {
          return firstRow.lowestPrice - secondRow.lowestPrice;
        }

        return String(firstRow[sortKey]).localeCompare(String(secondRow[sortKey]));
      });
  }, [category, offers, query, retailer, retailerFilterMode, sortKey]);

  return (
    <section className="comparison-card" aria-labelledby="comparison-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">{dataSourceLabel}</p>
          <h2 id="comparison-title">Comparison table</h2>
          <p className="source-note">{dataSourceDescription}</p>
        </div>
        <p className="result-count">
          Showing {comparisonRows.length} comparison rows from {offers.length} offers
        </p>
      </div>

      {statusMessage ? (
        <div className={`status-panel ${statusMessage.tone}`} role="status">
          <strong>{statusMessage.title}</strong>
          <span>{statusMessage.detail}</span>
        </div>
      ) : null}

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
          <select
            value={retailer}
            onChange={(event) => {
              const nextRetailer = event.target.value;

              setRetailer(nextRetailer);
              if (nextRetailer === allRetailers) {
                setRetailerFilterMode("available");
              }
            }}
          >
            {retailers.map((retailerName) => (
              <option key={retailerName}>{retailerName}</option>
            ))}
          </select>
        </label>

        <label>
          Retailer filter
          <select
            value={retailerFilterMode}
            onChange={(event) => setRetailerFilterMode(event.target.value as RetailerFilterMode)}
            disabled={retailer === allRetailers}
          >
            <option value="available">Available at retailer</option>
            <option value="cheapest">Cheapest at selected retailer</option>
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
            <option value="lowestPrice">Lowest price</option>
            <option value="product">Product</option>
            <option value="packageSize">Package</option>
          </select>
        </label>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th scope="col">Product</th>
              <th scope="col">Package</th>
              {retailers
                .filter((retailerName) => retailerName !== allRetailers)
                .map((retailerName) => (
                  <th key={retailerName} scope="col">
                    {retailerName}
                  </th>
                ))}
            </tr>
          </thead>
          <tbody>
            {comparisonRows.map((row) => (
              <tr key={row.key}>
                <td>
                  <strong>{row.product}</strong>
                  <span>{row.category}</span>
                </td>
                <td>{row.packageSize}</td>
                {retailers
                  .filter((retailerName) => retailerName !== allRetailers)
                  .map((retailerName) => {
                    const offer = row.offersByRetailer.get(retailerName as RetailerOffer["retailer"]);
                    const isCheapestOffer = offer?.price === row.lowestPrice;

                    return (
                      <td className={isCheapestOffer ? "cheapest-offer-cell" : undefined} key={retailerName}>
                        {offer ? (
                          <div className="offer-cell">
                            <strong>{currencyFormatter.format(offer.price)}</strong>
                            {isCheapestOffer ? <span className="cheapest-offer-label">Cheapest</span> : null}
                            <span>
                              {currencyFormatter.format(offer.unitPrice)} / {offer.unit}
                            </span>
                            <a href={offer.sourceUrl} target="_blank" rel="noreferrer">
                              Source
                            </a>
                            <span>{offer.promotion ?? "No promotion"}</span>
                            <span>Seen {dateFormatter.format(new Date(offer.lastSeen))}</span>
                          </div>
                        ) : (
                          <span className="missing-offer">No offer</span>
                        )}
                      </td>
                    );
                  })}
              </tr>
            ))}
          </tbody>
        </table>

        {comparisonRows.length === 0 ? (
          <p className="empty-state">No products match the current data set and filters.</p>
        ) : null}
      </div>
    </section>
  );
}
