export function formatEUR(amount) {
  return new Intl.NumberFormat("en-IE", { style: "currency", currency: "EUR" }).format(amount);
}
