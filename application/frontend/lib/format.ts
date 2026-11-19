export function money(v: string | number): string {
  const n = typeof v === "string" ? parseFloat(v) : v;
  return `₹${n.toFixed(2)}`;
}

export function formatDateTime(iso: string): string {
  return new Date(iso).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });
}

const STATUS_BADGE_CLASSES: Record<string, string> = {
  PLACED: "bg-amber-100 text-amber-800",
  CONFIRMED: "bg-sky-100 text-sky-800",
  PACKED: "bg-violet-100 text-violet-800",
  OUT_FOR_DELIVERY: "bg-blue-100 text-blue-800",
  DELIVERED: "bg-emerald-100 text-emerald-800",
  CANCELLED: "bg-red-100 text-red-700",
};

export function statusBadgeClasses(status: string): string {
  return STATUS_BADGE_CLASSES[status] ?? "bg-gray-100 text-gray-700";
}
