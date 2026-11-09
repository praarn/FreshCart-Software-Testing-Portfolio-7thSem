"use client";

import { useCallback, useEffect, useState } from "react";
import { api, errorMessage } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import type { AuditLogEntry } from "@/lib/types";

export default function AdminAuditLogPage() {
  const [entries, setEntries] = useState<AuditLogEntry[]>([]);
  const [orderIdFilter, setOrderIdFilter] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const qs = orderIdFilter ? `?order_id=${orderIdFilter}` : "";
      setEntries(await api.get<AuditLogEntry[]>(`/admin/audit-log${qs}`));
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [orderIdFilter]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div>
      <h1 className="mb-4 text-2xl font-bold text-gray-900">Audit Log</h1>
      <input
        id="admin-audit-log-order-filter"
        data-testid="admin-audit-log-order-filter"
        type="text"
        placeholder="Filter by order ID"
        value={orderIdFilter}
        onChange={(e) => setOrderIdFilter(e.target.value)}
        className="mb-4 rounded-lg border border-gray-300 px-3 py-2 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
      />
      {loading && (
        <p id="admin-audit-log-loading" data-testid="admin-audit-log-loading" className="text-gray-500">
          Loading...
        </p>
      )}
      {error && (
        <p id="admin-audit-log-error" data-testid="admin-audit-log-error" className="text-red-600">
          {error}
        </p>
      )}
      <div className="overflow-x-auto">
        <table id="admin-audit-log-table" data-testid="admin-audit-log-table" className="w-full border-collapse bg-white text-sm">
          <thead>
            <tr className="border-b border-gray-200 text-left text-gray-500">
              <th className="p-2">Order</th>
              <th className="p-2">From</th>
              <th className="p-2">To</th>
              <th className="p-2">Actor role</th>
              <th className="p-2">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((e) => (
              <tr key={e.id} data-testid={`admin-audit-log-row-${e.id}`} className="border-b border-gray-100">
                <td className="p-2">{e.order_id}</td>
                <td className="p-2">{e.from_state ?? "-"}</td>
                <td className="p-2">{e.to_state}</td>
                <td className="p-2">{e.actor_role}</td>
                <td className="p-2">{formatDateTime(e.timestamp)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
