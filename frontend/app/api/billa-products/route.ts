import { NextResponse } from "next/server";

const DEFAULT_BACKEND_URL = "http://127.0.0.1:8000";
const DEFAULT_BILLA_QUERY = "billa";
const DEFAULT_LIMIT = 100;
const MAX_LIMIT = 100;

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  const requestUrl = new URL(request.url);
  const query = (
    requestUrl.searchParams.get("q") ??
    process.env.GROCERY_BILLA_SEARCH_QUERY ??
    DEFAULT_BILLA_QUERY
  ).trim();
  const limit = parseLimit(requestUrl.searchParams.get("limit"));

  if (query.length < 2) {
    return NextResponse.json(
      { error: "BILLA product search query must contain at least 2 characters." },
      { status: 400 },
    );
  }

  const backendBaseUrl = (process.env.GROCERY_API_BASE_URL ?? DEFAULT_BACKEND_URL).replace(
    /\/$/,
    "",
  );
  const backendUrl = new URL("/products/search", backendBaseUrl);
  backendUrl.searchParams.set("q", query);
  backendUrl.searchParams.set("limit", String(limit));

  try {
    const response = await fetch(backendUrl, {
      headers: { accept: "application/json" },
      cache: "no-store",
    });
    const body = await response.text();

    if (!response.ok) {
      return NextResponse.json(
        {
          error: `Backend product search failed with status ${response.status}.`,
          detail: body,
        },
        { status: 502 },
      );
    }

    return NextResponse.json({
      ...JSON.parse(body),
      data_source: {
        kind: "api",
        backend_url: backendBaseUrl,
        endpoint: "/products/search",
        fetched_at: new Date().toISOString(),
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        error: "Could not reach the local Grocery Saver backend.",
        detail: error instanceof Error ? error.message : String(error),
      },
      { status: 502 },
    );
  }
}

function parseLimit(value: string | null): number {
  const parsed = value ? Number(value) : DEFAULT_LIMIT;

  if (!Number.isFinite(parsed)) {
    return DEFAULT_LIMIT;
  }

  return Math.max(1, Math.min(Math.trunc(parsed), MAX_LIMIT));
}
