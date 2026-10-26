"use client";

import { useCallback, useEffect, useState } from "react";
import RoleGuard from "@/components/RoleGuard";
import { api, errorMessage } from "@/lib/api";
import { money, formatDateTime, statusBadgeClasses } from "@/lib/format";
import type { Order } from "@/lib/types";

function DeliveryPageContent() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [otpInputs, setOtpInputs] = useState<Record<number, string>>({});
  const [actionError, setActionError] = useState<Record<number, string>>({});
  const [busyId, setBusyId] = useState<number | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.get<Order[]>("/delivery/orders");
      setOrders(data);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function dispatchOrder(orderId: number) {
    setBusyId(orderId);
    setActionError((prev) => ({ ...prev, [orderId]: "" }));
    try {
      await api.post(`/delivery/orders/${orderId}/dispatch`);
      await load();
    } catch (err) {
      setActionError((prev) => ({ ...prev, [orderId]: errorMessage(err) }));
    } finally {
      setBusyId(null);
    }
  }

  async function deliverOrder(orderId: number) {
    setBusyId(orderId);
    setActionError((prev) => ({ ...prev, [orderId]: "" }));
    try {
      await api.post(`/delivery/orders/${orderId}/deliver`, { otp: otpInputs[orderId] ?? "" });
      await load();
    } catch (err) {
      setActionError((prev) => ({ ...prev, [orderId]: errorMessage(err) }));
    } finally {
      setBusyId(null);
    }
  }

  if (loading) {
    return (
      <p id="delivery-loading" data-testid="delivery-loading" className="p-8 text-center text-gray-500">
        Loading assigned orders...
      </p>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Assigned Deliveries</h1>
      {error && (
        <p id="delivery-error" data-testid="delivery-error" className="text-red-600">
          {error}
        </p>
      )}
      {!error && orders.length === 0 && (
        <p id="delivery-empty" data-testid="delivery-empty" className="text-gray-500">
          No orders assigned to you right now.
        </p>
      )}
      <ul id="delivery-orders-list" data-testid="delivery-orders-list" className="space-y-4">
        {orders.map((o) => (
          <li key={o.id} id={`delivery-order-${o.id}`} data-testid={`delivery-order-${o.id}`} className="rounded-xl border border-gray-100 bg-white p-4 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div>
                <p className="font-medium text-gray-900">{o.order_number}</p>
                <p className="text-sm text-gray-500">
                  {o.address_line1}, {o.address_city} - {o.address_pincode}
                </p>
                <p className="text-sm text-gray-500">Slot: {formatDateTime(o.slot_start)}</p>
              </div>
              <span data-testid={`delivery-order-status-${o.id}`} className={`rounded-full px-2 py-1 text-sm font-medium ${statusBadgeClasses(o.status)}`}>
                {o.status}
              </span>
              <span className="font-semibold text-gray-900">{money(o.total)}</span>
            </div>

            {o.status === "PACKED" && (
              <button
                id={`delivery-dispatch-button-${o.id}`}
                data-testid={`delivery-dispatch-button-${o.id}`}
                onClick={() => dispatchOrder(o.id)}
                disabled={busyId === o.id}
                className="mt-3 rounded-full bg-brand-700 px-3 py-2 text-sm font-medium text-white hover:bg-brand-800 disabled:opacity-50"
              >
                Mark out for delivery
              </button>
            )}

            {o.status === "OUT_FOR_DELIVERY" && (
              <div className="mt-3 flex items-center gap-2">
                <input
                  id={`delivery-otp-input-${o.id}`}
                  data-testid={`delivery-otp-input-${o.id}`}
                  type="text"
                  maxLength={4}
                  placeholder="4-digit OTP"
                  value={otpInputs[o.id] ?? ""}
                  onChange={(e) => setOtpInputs((prev) => ({ ...prev, [o.id]: e.target.value }))}
                  className="w-32 rounded-lg border border-gray-300 px-3 py-2 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
                />
                <button
                  id={`delivery-deliver-button-${o.id}`}
                  data-testid={`delivery-deliver-button-${o.id}`}
                  onClick={() => deliverOrder(o.id)}
                  disabled={busyId === o.id}
                  className="rounded-full bg-brand-700 px-3 py-2 text-sm font-medium text-white hover:bg-brand-800 disabled:opacity-50"
                >
                  Confirm delivery
                </button>
              </div>
            )}

            {actionError[o.id] && (
              <p id={`delivery-order-error-${o.id}`} data-testid={`delivery-order-error-${o.id}`} className="mt-2 text-sm text-red-600">
                {actionError[o.id]}
              </p>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function DeliveryPage() {
  return (
    <RoleGuard roles={["DELIVERY_PARTNER"]}>
      <DeliveryPageContent />
    </RoleGuard>
  );
}
