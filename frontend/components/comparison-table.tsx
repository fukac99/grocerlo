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
  offers: RetailerOffer[];
  offersByRetailer: Map<RetailerOffer["retailer"], RetailerOffer>;
  lowestPrice: number;
};

type CountrySavingsSummary = {
  label: string;
  detail: string;
};

type RetailerSavingsSummary = {
  label: string;
  detail: string;
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
const allCountries = "All countries";
const allCategories = "All categories";

const currencyFormatter = new Intl.NumberFormat("en-AT", {
  style: "currency",
  currency: "EUR",
});

const dateFormatter = new Intl.DateTimeFormat("en-AT", {
  dateStyle: "medium",
});

const percentFormatter = new Intl.NumberFormat("en-AT", {
  maximumFractionDigits: 1,
  style: "percent",
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
  const [country, setCountry] = useState(allCountries);
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
  const countries = useMemo(
    () => [allCountries, ...Array.from(new Set(offers.map((offer) => offer.country))).sort()],
    [offers],
  );

  const normalizedQuery = query.trim().toLowerCase();
  const activeFilterDescriptions = [
    normalizedQuery.length > 0 ? `product name contains "${query.trim()}"` : null,
    category !== allCategories ? `category is ${category}` : null,
    country !== allCountries ? `cheapest in ${country}` : null,
    retailer !== allRetailers
      ? retailerFilterMode === "cheapest"
        ? `cheapest at ${retailer}`
        : `available at ${retailer}`
      : null,
  ].filter((filter): filter is string => Boolean(filter));
  const activeFilterSummary =
    activeFilterDescriptions.length > 0 ? activeFilterDescriptions.join(", ") : "no active filters";

  const comparisonRows = useMemo(() => {
    const rows = new Map<string, ComparisonRow>();

    for (const offer of offers) {
      const rowKey = `${offer.product}|${offer.packageSize}`;
      const existingRow = rows.get(rowKey);

      if (existingRow) {
        existingRow.offers.push(offer);
        existingRow.offersByRetailer.set(offer.retailer, offer);
        existingRow.lowestPrice = Math.min(existingRow.lowestPrice, offer.price);
      } else {
        rows.set(rowKey, {
          key: rowKey,
          product: offer.product,
          packageSize: offer.packageSize,
          category: offer.category,
          offers: [offer],
          offersByRetailer: new Map([[offer.retailer, offer]]),
          lowestPrice: offer.price,
        });
      }
    }

    return Array.from(rows.values());
  }, [offers]);

  const filteredComparisonRows = useMemo(
    () =>
      comparisonRows
      .filter((row) => {
        const selectedRetailer = retailer as RetailerOffer["retailer"];
        const selectedRetailerOffer = row.offersByRetailer.get(selectedRetailer);
        const matchesRetailer =
          retailer === allRetailers ||
          (retailerFilterMode === "cheapest"
            ? selectedRetailerOffer !== undefined &&
              pricesAreEqual(selectedRetailerOffer.price, row.lowestPrice)
            : Boolean(selectedRetailerOffer));
        const countrySavingsSummary = getCountrySavingsSummary(row, country);
        const matchesCountry = country === allCountries || countrySavingsSummary !== null;
        const matchesCategory = category === allCategories || row.category === category;
        const matchesProductName =
          normalizedQuery.length === 0 || row.product.toLowerCase().includes(normalizedQuery);

        return (
          matchesRetailer &&
          matchesCountry &&
          matchesCategory &&
          matchesProductName
        );
      })
      .sort((firstRow, secondRow) => {
        if (sortKey === "lowestPrice") {
          return firstRow.lowestPrice - secondRow.lowestPrice;
        }

        return String(firstRow[sortKey]).localeCompare(String(secondRow[sortKey]));
      }),
    [category, comparisonRows, country, normalizedQuery, retailer, retailerFilterMode, sortKey],
  );

  return (
    <section className="comparison-card" aria-labelledby="comparison-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">{dataSourceLabel}</p>
          <h2 id="comparison-title">Comparison table</h2>
          <p className="source-note">{dataSourceDescription}</p>
        </div>
        <p className="result-count">
          Showing {filteredComparisonRows.length} of {comparisonRows.length} product groups from{" "}
          {offers.length} offers
          {activeFilterDescriptions.length > 0 ? ` with ${activeFilterSummary}` : ""}
        </p>
      </div>

      {statusMessage ? (
        <div className={`status-panel ${statusMessage.tone}`} role="status">
          <strong>{statusMessage.title}</strong>
          <span>{statusMessage.detail}</span>
        </div>
      ) : null}

      <div className="filters" aria-label="Filter comparison offers">
        <label className="category-filter">
          Category
          <span className="filter-hint">Start with a grocery category, then narrow by market.</span>
          <select value={category} onChange={(event) => setCategory(event.target.value)}>
            {categories.map((categoryName) => (
              <option key={categoryName}>{categoryName}</option>
            ))}
          </select>
        </label>

        <label className="product-search-filter">
          Search product name
          <span className="filter-hint">Matches product names only, not retailer or brand text.</span>
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Try milk, spaghetti, coffee..."
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
          Country cheapest in
          <select value={country} onChange={(event) => setCountry(event.target.value)}>
            {countries.map((countryName) => (
              <option key={countryName}>{countryName}</option>
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
            {filteredComparisonRows.map((row) => {
              const countrySavingsSummary = getCountrySavingsSummary(row, country);
              const retailerSavingsSummary = getRetailerSavingsSummary(
                row,
                retailer,
                retailerFilterMode,
              );

              return (
                <tr key={row.key}>
                  <td>
                    <strong>{row.product}</strong>
                    <span>{row.category}</span>
                    {countrySavingsSummary ? (
                      <span className="country-savings">
                        <strong>{countrySavingsSummary.label}</strong>
                        <span>{countrySavingsSummary.detail}</span>
                      </span>
                    ) : null}
                    {retailerSavingsSummary ? (
                      <span className="retailer-savings">
                        <strong>{retailerSavingsSummary.label}</strong>
                        <span>{retailerSavingsSummary.detail}</span>
                      </span>
                    ) : null}
                  </td>
                  <td>{row.packageSize}</td>
                  {retailers
                    .filter((retailerName) => retailerName !== allRetailers)
                    .map((retailerName) => {
                      const offer = row.offersByRetailer.get(retailerName as RetailerOffer["retailer"]);
                      const isCheapestOffer =
                        offer !== undefined && pricesAreEqual(offer.price, row.lowestPrice);

                      return (
                        <td
                          className={isCheapestOffer ? "cheapest-offer-cell" : undefined}
                          key={retailerName}
                        >
                          {offer ? (
                            <div className="offer-cell">
                              <strong>{currencyFormatter.format(offer.price)}</strong>
                              {isCheapestOffer ? (
                                <span className="cheapest-offer-label">Cheapest</span>
                              ) : null}
                              <span>
                                {currencyFormatter.format(offer.unitPrice)} / {offer.unit}
                              </span>
                              <span>Country {offer.country}</span>
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
              );
            })}
          </tbody>
        </table>

        {filteredComparisonRows.length === 0 ? (
          <p className="empty-state">
            <strong>No products match your filters.</strong>
            <span>
              Showing 0 of {comparisonRows.length} product groups for {activeFilterSummary}. Search
              checks product names only.
            </span>
          </p>
        ) : null}
      </div>
    </section>
  );
}

function getRetailerSavingsSummary(
  row: ComparisonRow,
  selectedRetailer: string,
  retailerFilterMode: RetailerFilterMode,
): RetailerSavingsSummary | null {
  if (selectedRetailer === allRetailers || retailerFilterMode !== "cheapest") {
    return null;
  }

  const selectedOffer = row.offersByRetailer.get(selectedRetailer);

  if (!selectedOffer || !pricesAreEqual(selectedOffer.price, row.lowestPrice)) {
    return null;
  }

  const comparableOffers = row.offers.filter((offer) => offer.retailer !== selectedRetailer);

  if (comparableOffers.length === 0) {
    return {
      label: "No savings delta",
      detail: "No comparable retailer offer is available for this product.",
    };
  }

  const tiedOffers = comparableOffers.filter((offer) =>
    pricesAreEqual(offer.price, selectedOffer.price),
  );

  if (tiedOffers.length > 0) {
    const tiedRetailers = Array.from(new Set(tiedOffers.map((offer) => offer.retailer))).sort();

    return {
      label: "Tied cheapest",
      detail: `${currencyFormatter.format(0)} (0%) versus tied cheapest at ${tiedRetailers.join(", ")}.`,
    };
  }

  const nextBestOffer = comparableOffers.sort(
    (firstOffer, secondOffer) => firstOffer.price - secondOffer.price,
  )[0];

  if (!nextBestOffer) {
    return {
      label: "No savings delta",
      detail: "No comparable retailer offer is available for this product.",
    };
  }

  const savingsAmount = nextBestOffer.price - selectedOffer.price;
  const savingsPercent = savingsAmount / nextBestOffer.price;

  return {
    label: `${currencyFormatter.format(savingsAmount)} cheaper`,
    detail: `${currencyFormatter.format(savingsAmount)} (${percentFormatter.format(savingsPercent)}) below next-best offer at ${nextBestOffer.retailer}.`,
  };
}

function getCountrySavingsSummary(
  row: ComparisonRow,
  selectedCountry: string,
): CountrySavingsSummary | null {
  if (selectedCountry === allCountries) {
    return null;
  }

  const cheapestOffers = row.offers.filter((offer) =>
    pricesAreEqual(offer.price, row.lowestPrice),
  );
  const selectedCountryCheapestOffers = cheapestOffers.filter(
    (offer) => offer.country === selectedCountry,
  );

  if (selectedCountryCheapestOffers.length === 0) {
    return null;
  }

  const nextBestOffer = row.offers
    .filter(
      (offer) =>
        offer.price > row.lowestPrice && !pricesAreEqual(offer.price, row.lowestPrice),
    )
    .sort((firstOffer, secondOffer) => firstOffer.price - secondOffer.price)[0];
  const tiedCountryNames = Array.from(new Set(cheapestOffers.map((offer) => offer.country))).sort();
  const hasTie = cheapestOffers.length > 1;

  if (!nextBestOffer) {
    return {
      label: hasTie ? "Tied cheapest" : "No comparison offer",
      detail: hasTie
        ? `${currencyFormatter.format(0)} (0%) versus tied cheapest offers in ${tiedCountryNames.join(", ")}; no higher-priced offer is available.`
        : "Only one available offer, so there is no next-best price to compare.",
    };
  }

  const savingsAmount = nextBestOffer.price - row.lowestPrice;
  const savingsPercent = savingsAmount / nextBestOffer.price;
  const savingsDetail = `${currencyFormatter.format(savingsAmount)} (${percentFormatter.format(savingsPercent)}) below next-best offer at ${nextBestOffer.retailer} (${nextBestOffer.country}).`;

  if (hasTie) {
    return {
      label: "Tied cheapest",
      detail: `Matches tied cheapest offers in ${tiedCountryNames.join(", ")} and is ${savingsDetail}`,
    };
  }

  return {
    label: `${currencyFormatter.format(savingsAmount)} cheaper`,
    detail: savingsDetail,
  };
}

function pricesAreEqual(firstPrice: number, secondPrice: number): boolean {
  return Math.abs(firstPrice - secondPrice) < 0.001;
}
