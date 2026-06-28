import type { RetailerOffer } from "../data/sample-offers";

export type ApiMoney = {
  amount: string | null;
  currency: string | null;
};

export type ApiUnitPrice = {
  amount: string | null;
  unit: string | null;
  price_per_base_unit: string | null;
  base_unit: string | null;
};

export type ApiPackage = {
  quantity: string | null;
  unit: string | null;
  normalized_quantity: string | null;
  normalized_unit: string | null;
};

export type ApiPromotion = {
  is_promotion: boolean;
  promotion_type: string | null;
};

export type ApiBillaProduct = {
  id: number;
  retailer: string;
  country: string;
  source_product_id: string | null;
  name: string;
  brand: string | null;
  category: string | null;
  price: ApiMoney;
  unit_price: ApiUnitPrice;
  package: ApiPackage;
  source_url: string | null;
  promotion: ApiPromotion;
  availability: string | null;
  observed_at: string;
};

export type ApiDataSource = {
  kind: "api";
  backend_url: string;
  endpoint: string;
  fetched_at: string;
};

export type BillaProductSearchResponse = {
  query: string;
  retailer: string;
  count: number;
  items: ApiBillaProduct[];
  data_source: ApiDataSource;
};

export function mapBillaProductToOffer(product: ApiBillaProduct): RetailerOffer | null {
  const price = parseDecimal(product.price.amount);

  if (price === null) {
    return null;
  }

  const unitPrice =
    parseDecimal(product.unit_price.price_per_base_unit) ??
    parseDecimal(product.unit_price.amount) ??
    price;

  return {
    id: `billa-api-${product.id}`,
    product: product.name,
    brand: product.brand ?? "Unknown brand",
    retailer: product.retailer.toUpperCase(),
    country: product.country.toUpperCase(),
    category: product.category ?? "Uncategorized",
    packageSize: formatPackageSize(product.package),
    price,
    unitPrice,
    unit: product.unit_price.base_unit ?? product.unit_price.unit ?? product.package.unit ?? "unit",
    promotion: product.promotion.is_promotion
      ? formatPromotion(product.promotion.promotion_type)
      : null,
    lastSeen: product.observed_at,
    sourceUrl: product.source_url ?? "https://shop.billa.at/",
  };
}

function parseDecimal(value: string | null): number | null {
  if (value === null) {
    return null;
  }

  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function formatPackageSize(packageDetails: ApiPackage): string {
  if (packageDetails.quantity && packageDetails.unit) {
    return `${formatQuantity(packageDetails.quantity)} ${packageDetails.unit}`;
  }

  if (packageDetails.normalized_quantity && packageDetails.normalized_unit) {
    return `${formatQuantity(packageDetails.normalized_quantity)} ${packageDetails.normalized_unit}`;
  }

  return "Package not listed";
}

function formatQuantity(value: string): string {
  const parsed = Number(value);

  if (!Number.isFinite(parsed)) {
    return value;
  }

  return Number.isInteger(parsed) ? String(parsed) : String(parsed);
}

function formatPromotion(promotionType: string | null): string {
  if (!promotionType) {
    return "Promotion";
  }

  return promotionType
    .split(/[_-]/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}
