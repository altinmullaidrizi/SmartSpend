export const CATEGORIES = [
  "groceries",
  "dining",
  "coffee",
  "transport",
  "mobile_topup",
  "utilities",
  "rent",
  "shopping",
  "health",
  "education",
  "transfers",
  "entertainment",
];

export function categoryLabel(cat) {
  if (!cat) return "Uncategorized";
  return cat
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}
