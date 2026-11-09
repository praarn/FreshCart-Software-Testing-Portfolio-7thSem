export function money(v: string | number): string {
  const n = typeof v === "string" ? parseFloat(v) : v;
  return `₹${n.toFixed(2)}`;
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });
}
