export const CATEGORIES = [
  "All",
  "Cargo And Courier Services",
  "Corporate Website",
  "eCommerce Website",
  "Education",
  "Healthcare",
  "Manufacturer Industrial",
  "Others",
  "Real Estate",
  "Religious and Communities",
  "Religious Organization",
  "Travel and Tourism"
] as const;

export type Category = (typeof CATEGORIES)[number];
