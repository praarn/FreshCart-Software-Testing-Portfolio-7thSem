"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import RoleGuard from "@/components/RoleGuard";
import { api, errorMessage, getToken } from "@/lib/api";
import { money, formatDateTime, statusBadgeClasses } from "@/lib/format";
import type { Order } from "@/lib/types";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
const CANCELLABLE = new Set(["PLACED", "CONFIRMED"]);

function OrderDetailContent() {
  const params = useParams<{ id: string }>();
  const orderId = params.id;
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cancelling, setCancelling] = useState(false);
  const [liveNote, setLiveNote] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.get<Order>(`/orders/${orderId}`);
      setOrder(data);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [orderId]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    const token = getToken();
    if (!token) return;
    const ws = new WebSocket(`${WS_URL}/ws/orders/${orderId}?token=${token}`);
    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        setLiveNote(`Status updated to ${msg.status}`);
      } catch {
        // ignore malformed message
      }
      load();
    };
    return () => ws.close();
  }, [orderId, load]);

  async function handleCancel() {
    setCancelling(true);
    setError(null);
    try {
      const data = await api.post<Order>(`/orders/${orderId}/cancel`);
      setOrder(data);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setCancelling(false);
    }
  }

  if (loading) {
    return (
      <p id="order-detail-loading" data-testid="order-detail-loading" className="p-8 text-center text-gray-500">
        Loading order...
      </p>
    );
  }
  if (error || !order) {
    return (
      <p id="order-detail-error" data-testid="order-detail-error" className="p-8 text-center text-red-600">
        {error ?? "Order not found."}
      </p>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <h1 id="order-detail-number" data-testid="order-detail-number" className="mb-1 text-2xl font-bold text-gray-900">
        {order.order_number}
      </h1>
      <p id="order-detail-status" data-testid="order-detail-status" className={`mb-4 inline-block rounded-full px-2 py-1 text-sm font-medium ${statusBadgeClasses(order.status)}`}>
        {order.status}
      </p>

      {liveNote && (
        <p id="order-live-note" data-testid="order-live-note" className="mb-4 text-sm text-blue-600">
          {liveNote} (live update)
        </p>
      )}

      {order.delivery_otp && (
        <p id="order-delivery-otp" data-testid="order-delivery-otp" className="mb-4 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
          Delivery OTP: <span className="font-mono font-bold">{order.delivery_otp}</span> — share this with your delivery partner.
        </p>
      )}

      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <h2 className="mb-2 font-semibold text-gray-900">Items</h2>
        <ul data-testid="order-detail-items" className="space-y-1">
          {order.items.map((it) => (
            <li key={it.product_id} className="flex justify-between text-sm">
              <span>
                {it.product_name} × {it.quantity}
              </span>
              <span>{money(it.line_total)}</span>
            </li>
          ))}
        </ul>
        <div className="mt-3 border-t border-gray-200 pt-2 text-sm">
          <div className="flex justify-between">
            <span>Subtotal</span>
            <span>{money(order.subtotal)}</span>
          </div>
          <div className="flex justify-between">
            <span>Discount</span>
            <span>-{money(order.discount)}</span>
          </div>
          <div className="flex justify-between">
            <span>Delivery fee</span>
            <span>{money(order.delivery_fee)}</span>
          </div>
          <div className="mt-1 flex justify-between font-bold">
            <span>Total</span>
            <span>{money(order.total)}</span>
          </div>
        </div>
      </div>

      <div className="mt-4 rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-700">
        <p>
          <span className="font-medium">Deliver to:</span> {order.address_line1}, {order.address_city} - {order.address_pincode}
        </p>
        <p>
          <span className="font-medium">Slot:</span> {formatDateTime(order.slot_start)} - {formatDateTime(order.slot_end)}
        </p>
        <p>
          <span className="font-medium">Payment:</span> {order.payment_method}
          {order.payment_reference ? ` (${order.payment_reference})` : ""}
        </p>
      </div>

      {CANCELLABLE.has(order.status) && (
        <button
          id="order-cancel-button"
          data-testid="order-cancel-button"
          onClick={handleCancel}
          disabled={cancelling}
          className="mt-4 rounded-md border border-red-300 px-4 py-2 text-sm text-red-600 hover:bg-red-50 disabled:opacity-50"
        >
          {cancelling ? "Cancelling..." : "Cancel order"}
        </button>
      )}

      <div className="mt-6">
        <h2 className="mb-2 font-semibold text-gray-900">Status timeline</h2>
        <ul id="order-timeline" data-testid="order-timeline" className="space-y-2">
          {order.audits.map((a, idx) => (
            <li key={idx} data-testid={`order-timeline-entry-${idx}`} className="flex justify-between rounded-lg border border-gray-200 bg-white p-3 text-sm">
              <span>
                {a.from_state ? `${a.from_state} → ${a.to_state}` : a.to_state} <span className="text-gray-400">by {a.actor_role}</span>
              </span>
              <span className="text-gray-500">{formatDateTime(a.timestamp)}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default function OrderDetailPage() {
  return (
    <RoleGuard roles={["CUSTOMER"]}>
      <OrderDetailContent />
    </RoleGuard>
  );
}
