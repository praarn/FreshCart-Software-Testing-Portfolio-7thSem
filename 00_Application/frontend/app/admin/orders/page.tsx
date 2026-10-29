"use client";

import { useCallback, useEffect, useState } from "react";
import { api, errorMessage } from "@/lib/api";
import { money, formatDateTime, statusBadgeClasses } from "@/lib/format";
import type { Order, OrderStatus, User } from "@/lib/types";

const STATUS_OPTIONS: OrderStatus[] = ["PLACED", "CONFIRMED", "PACKED", "OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED"];

export default function AdminOrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [partners, setPartners] = useState<User[]>([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rowError, setRowError] = useState<Record<number, string>>({});
  const [partnerSelect, setPartnerSelect] = useState<Record<number, string>>({});

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const qs = statusFilter ? `?status=${statusFilter}` : "";
      const [o, u] = await Promise.all([api.get<Order[]>(`/admin/orders${qs}`), api.get<User[]>("/admin/users")]);
      setOrders(o);
      setPartners(u.filter((x) => x.role === "DELIVERY_PARTNER"));
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    load();
  }, [load]);

  async function advance(orderId: number, toStatus: string) {
    setRowError((prev) => ({ ...prev, [orderId]: "" }));
    try {
      await api.patch(`/admin/orders/${orderId}/status`, { to_status: toStatus });
      await load();
    } catch (err) {
      setRowError((prev) => ({ ...prev, [orderId]: errorMessage(err) }));
    }
  }

  async function assignPartner(orderId: number) {
    const partnerId = partnerSelect[orderId];
    if (!partnerId) return;
    setRowError((prev) => ({ ...prev, [orderId]: "" }));
    try {
      await api.post(`/admin/orders/${orderId}/assign-partner`, { delivery_partner_id: Number(partnerId) });
      await load();
    } catch (err) {
      setRowError((prev) => ({ ...prev, [orderId]: errorMessage(err) }));
    }
  }

  async function resetOtp(orderId: number) {
    try {
      await api.post(`/admin/orders/${orderId}/reset-otp`);
      await load();
    } catch (err) {
      setRowError((prev) => ({ ...prev, [orderId]: errorMessage(err) }));
    }
  }

  async function cancelOrder(orderId: number) {
    try {
      await api.post(`/admin/orders/${orderId}/cancel`);
      await load();
    } catch (err) {
      setRowError((prev) => ({ ...prev, [orderId]: errorMessage(err) }));
    }
  }

  return (
    <div>
      <h1 className="mb-4 text-2xl font-bold text-gray-900">Orders</h1>

      <select
        id="admin-order-status-filter"
        data-testid="admin-order-status-filter"
        value={statusFilter}
        onChange={(e) => setStatusFilter(e.target.value)}
        className="mb-4 rounded-lg border border-gray-300 px-3 py-2 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-100"
      >
        <option value="">All statuses</option>
        {STATUS_OPTIONS.map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>

      {loading && (
        <p id="admin-orders-loading" data-testid="admin-orders-loading" className="text-gray-500">
          Loading...
        </p>
      )}
      {error && (
        <p id="admin-orders-error" data-testid="admin-orders-error" className="text-red-600">
          {error}
        </p>
      )}

      <ul id="admin-orders-list" data-testid="admin-orders-list" className="space-y-3">
        {orders.map((o) => (
          <li key={o.id} id={`admin-order-row-${o.id}`} data-testid={`admin-order-row-${o.id}`} className="rounded-lg border border-gray-200 bg-white p-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <p className="font-medium text-gray-900">{o.order_number}</p>
                <p className="text-sm text-gray-500">{formatDateTime(o.created_at)}</p>
              </div>
              <span data-testid={`admin-order-status-${o.id}`} className={`rounded-full px-2 py-1 text-sm font-medium ${statusBadgeClasses(o.status)}`}>
                {o.status}
              </span>
              <span className="font-semibold text-gray-900">{money(o.total)}</span>
            </div>

            <div className="mt-3 flex flex-wrap items-center gap-2">
              {o.status === "PLACED" && (
                <button
                  id={`admin-order-confirm-${o.id}`}
                  data-testid={`admin-order-confirm-${o.id}`}
                  onClick={() => advance(o.id, "CONFIRMED")}
                  className="rounded-md border border-gray-300 px-3 py-1 text-sm hover:bg-gray-50"
                >
                  Confirm
                </button>
              )}
              {o.status === "CONFIRMED" && (
                <button
                  id={`admin-order-pack-${o.id}`}
                  data-testid={`admin-order-pack-${o.id}`}
                  onClick={() => advance(o.id, "PACKED")}
                  className="rounded-md border border-gray-300 px-3 py-1 text-sm hover:bg-gray-50"
                >
                  Mark packed
                </button>
              )}
              {o.status === "PACKED" && (
                <>
                  <select
                    id={`admin-order-partner-select-${o.id}`}
                    data-testid={`admin-order-partner-select-${o.id}`}
                    value={partnerSelect[o.id] ?? ""}
                    onChange={(e) => setPartnerSelect((prev) => ({ ...prev, [o.id]: e.target.value }))}
                    className="rounded-lg border border-gray-300 px-2 py-1 text-sm focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-100"
                  >
                    <option value="">Select delivery partner</option>
                    {partners.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name}
                      </option>
                    ))}
                  </select>
                  <button
                    id={`admin-order-assign-${o.id}`}
                    data-testid={`admin-order-assign-${o.id}`}
                    onClick={() => assignPartner(o.id)}
                    disabled={!partnerSelect[o.id]}
                    className="rounded-md border border-gray-300 px-3 py-1 text-sm hover:bg-gray-50 disabled:opacity-50"
                  >
                    Assign
                  </button>
                </>
              )}
              {o.status === "OUT_FOR_DELIVERY" && (
                <button
                  id={`admin-order-reset-otp-${o.id}`}
                  data-testid={`admin-order-reset-otp-${o.id}`}
                  onClick={() => resetOtp(o.id)}
                  className="rounded-md border border-gray-300 px-3 py-1 text-sm hover:bg-gray-50"
                >
                  Reset OTP attempts
                </button>
              )}
              {(o.status === "PLACED" || o.status === "CONFIRMED") && (
                <button
                  id={`admin-order-cancel-${o.id}`}
                  data-testid={`admin-order-cancel-${o.id}`}
                  onClick={() => cancelOrder(o.id)}
                  className="rounded-md border border-red-300 px-3 py-1 text-sm text-red-600 hover:bg-red-50"
                >
                  Cancel
                </button>
              )}
            </div>
            {rowError[o.id] && (
              <p data-testid={`admin-order-error-${o.id}`} className="mt-2 text-sm text-red-600">
                {rowError[o.id]}
              </p>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
