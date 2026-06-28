"use client";

import { useEffect, useMemo, useState } from "react";
import { ComparisonTable } from "./comparison-table";
import { sampleOffers, type RetailerOffer } from "../data/sample-offers";
import {
  type BillaProductSearchResponse,
  mapBillaProductToOffer,
} from "../lib/billa-products";

type LoadStatus = "idle" | "loading" | "loaded" | "error";

type ApiState = {
  status: LoadStatus;
  offers: RetailerOffer[];
  response: BillaProductSearchResponse | null;
  error: string | null;
  skippedRows: number;
};

const DATA_SOURCE_MODE =
  process.env.NEXT_PUBLIC_GROCERY_DATA_SOURCE === "sample" ? "sample" : "api";
const DEFAULT_BILLA_QUERY = process.env.NEXT_PUBLIC_GROCERY_BILLA_QUERY ?? "billa";
const DEFAULT_LIMIT = 100;

export function GrocerloDataLoader() {
  const [apiState, setApiState] = useState<ApiState>({
    status: DATA_SOURCE_MODE === "sample" ? "loaded" : "idle",
    offers: DATA_SOURCE_MODE === "sample" ? sampleOffers : [],
    response: null,
    error: null,
    skippedRows: 0,
  });

  useEffect(() => {
    if (DATA_SOURCE_MODE === "sample") {
      return;
    }

    const controller = new AbortController();

    async function loadBillaProducts() {
      setApiState((currentState) => ({
        ...currentState,
        status: "loading",
        error: null,
      }));

      try {
        const params = new URLSearchParams({
          q: DEFAULT_BILLA_QUERY,
          limit: String(DEFAULT_LIMIT),
        });
        const response = await fetch(`/api/billa-products?${params.toString()}`, {
          cache: "no-store",
          signal: controller.signal,
        });
        const payload = await response.json();

        if (!response.ok) {
          throw new Error(payload.error ?? "Failed to load BILLA products.");
        }

        const apiResponse = payload as BillaProductSearchResponse;
        const mappedOffers = apiResponse.items
          .map(mapBillaProductToOffer)
          .filter((offer): offer is RetailerOffer => offer !== null);

        setApiState({
          status: "loaded",
          offers: mappedOffers,
          response: apiResponse,
          error: null,
          skippedRows: apiResponse.items.length - mappedOffers.length,
        });
      } catch (error) {
        if (controller.signal.aborted) {
          return;
        }

        setApiState({
          status: "error",
          offers: [],
          response: null,
          error: error instanceof Error ? error.message : String(error),
          skippedRows: 0,
        });
      }
    }

    loadBillaProducts();

    return () => controller.abort();
  }, []);

  const tableContent = useMemo(() => {
    if (DATA_SOURCE_MODE === "sample") {
      return {
        offers: sampleOffers,
        dataSourceLabel: "Mock sample data",
        dataSourceDescription:
          "Sample mode is explicitly enabled with NEXT_PUBLIC_GROCERY_DATA_SOURCE=sample.",
        statusMessage: null,
      };
    }

    if (apiState.status === "loading" || apiState.status === "idle") {
      return {
        offers: apiState.offers,
        dataSourceLabel: "Loading live BILLA data",
        dataSourceDescription: `Fetching normalized rows from the local backend with query "${DEFAULT_BILLA_QUERY}".`,
        statusMessage: {
          tone: "info" as const,
          title: "Loading real backend data",
          detail: "Grocerlo is asking the local API for normalized BILLA products.",
        },
      };
    }

    if (apiState.status === "error") {
      return {
        offers: [],
        dataSourceLabel: "Live BILLA data unavailable",
        dataSourceDescription:
          "No sample fallback is shown unless sample mode is explicitly configured.",
        statusMessage: {
          tone: "error" as const,
          title: "Could not load backend data",
          detail:
            apiState.error ??
            "Start the local FastAPI backend or set NEXT_PUBLIC_GROCERY_DATA_SOURCE=sample to view mock data.",
        },
      };
    }

    const latestObservedAt = getLatestObservedAt(apiState.offers);
    const skippedCopy =
      apiState.skippedRows > 0
        ? ` ${apiState.skippedRows} API rows without a usable price were skipped.`
        : "";

    return {
      offers: apiState.offers,
      dataSourceLabel: "Live BILLA API data",
      dataSourceDescription: `Loaded ${apiState.offers.length} normalized offers from ${apiState.response?.data_source.endpoint} via ${apiState.response?.data_source.backend_url}. Backend query: "${apiState.response?.query}".${
        latestObservedAt ? ` Latest observation: ${latestObservedAt}.` : ""
      }${skippedCopy}`,
      statusMessage:
        apiState.offers.length === 0
          ? {
              tone: "info" as const,
              title: "No backend rows returned",
              detail: `The local API returned no priced BILLA products for "${apiState.response?.query}". Try NEXT_PUBLIC_GROCERY_BILLA_QUERY with a broader product term.`,
            }
          : null,
    };
  }, [apiState]);

  return <ComparisonTable {...tableContent} />;
}

function getLatestObservedAt(offers: RetailerOffer[]): string | null {
  const timestamps = offers
    .map((offer) => new Date(offer.lastSeen).getTime())
    .filter(Number.isFinite);

  if (timestamps.length === 0) {
    return null;
  }

  return new Intl.DateTimeFormat("en-AT", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(Math.max(...timestamps)));
}
