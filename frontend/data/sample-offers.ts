export type RetailerOffer = {
  id: string;
  product: string;
  brand: string;
  retailer: string;
  category: string;
  packageSize: string;
  price: number;
  unitPrice: number;
  unit: string;
  promotion: string | null;
  lastSeen: string;
  sourceUrl: string;
};

export const sampleOffers: RetailerOffer[] = [
  {
    id: "billa-ja-natuerlich-milk-1l",
    product: "Whole Milk",
    brand: "Ja! Natürlich",
    retailer: "BILLA",
    category: "Dairy",
    packageSize: "1 l",
    price: 1.79,
    unitPrice: 1.79,
    unit: "l",
    promotion: null,
    lastSeen: "2026-06-28",
    sourceUrl: "https://shop.billa.at/",
  },
  {
    id: "mpreis-bio-milk-1l",
    product: "Whole Milk",
    brand: "Bio vom Berg",
    retailer: "MPREIS",
    category: "Dairy",
    packageSize: "1 l",
    price: 1.89,
    unitPrice: 1.89,
    unit: "l",
    promotion: "Club price",
    lastSeen: "2026-06-27",
    sourceUrl: "https://www.mpreis.at/",
  },
  {
    id: "billa-clever-spaghetti-500g",
    product: "Spaghetti",
    brand: "Clever",
    retailer: "BILLA",
    category: "Pantry",
    packageSize: "500 g",
    price: 0.99,
    unitPrice: 1.98,
    unit: "kg",
    promotion: "2+1 free",
    lastSeen: "2026-06-28",
    sourceUrl: "https://shop.billa.at/",
  },
  {
    id: "spar-barilla-spaghetti-500g",
    product: "Spaghetti",
    brand: "Barilla",
    retailer: "SPAR",
    category: "Pantry",
    packageSize: "500 g",
    price: 1.69,
    unitPrice: 3.38,
    unit: "kg",
    promotion: null,
    lastSeen: "2026-06-26",
    sourceUrl: "https://www.interspar.at/",
  },
  {
    id: "rewe-bananas-1kg",
    product: "Bananas",
    brand: "REWE Beste Wahl",
    retailer: "REWE",
    category: "Produce",
    packageSize: "loose",
    price: 1.49,
    unitPrice: 1.49,
    unit: "kg",
    promotion: null,
    lastSeen: "2026-06-24",
    sourceUrl: "https://www.rewe.de/",
  },
  {
    id: "billa-bananas-1kg",
    product: "Bananas",
    brand: "BILLA",
    retailer: "BILLA",
    category: "Produce",
    packageSize: "loose",
    price: 1.69,
    unitPrice: 1.69,
    unit: "kg",
    promotion: "Weekend deal",
    lastSeen: "2026-06-28",
    sourceUrl: "https://shop.billa.at/",
  },
  {
    id: "mpreis-arabica-coffee-500g",
    product: "Coffee Beans",
    brand: "MPreis Privat",
    retailer: "MPREIS",
    category: "Coffee",
    packageSize: "500 g",
    price: 7.99,
    unitPrice: 15.98,
    unit: "kg",
    promotion: null,
    lastSeen: "2026-06-27",
    sourceUrl: "https://www.mpreis.at/",
  },
  {
    id: "billa-dallmayr-coffee-500g",
    product: "Coffee Beans",
    brand: "Dallmayr",
    retailer: "BILLA",
    category: "Coffee",
    packageSize: "500 g",
    price: 6.99,
    unitPrice: 13.98,
    unit: "kg",
    promotion: "Member discount",
    lastSeen: "2026-06-28",
    sourceUrl: "https://shop.billa.at/",
  },
];
