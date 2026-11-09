"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import RoleGuard from "@/components/RoleGuard";
import { api, errorMessage } from "@/lib/api";
import { money, formatDateTime } from "@/lib/format";
import type { Order } from "@/lib/types";

function OrdersPageContent() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<Order[]>("/orders")
      .then(setOrders)
      .catch((err) => setError(errorMessage(err)))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <p id="orders-loading" data-testid="orders-loading" className="p-8 text-center text-gray-500">
        Loading orders...
      </p>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">My Orders</h1>
      {error && (
        <p id="orders-error" data-testid="orders-error" className="text-red-600">
          {error}
        </p>
      )}
      {!error && orders.length === 0 && (
        <p id="orders-empty" data-testid="orders-empty" className="text-gray-500">
          You haven&apos;t placed any orders yet.
        </p>
      )}
      <ul id="orders-list" data-testid="orders-list" className="space-y-3">
        {orders.map((o) => (
          <li key={o.id}>
            <Link
              id={`order-row-${o.id}`}
              data-testid={`order-row-${o.id}`}
              href={`/orders/${o.id}`}
              className="flex flex-wrap items-center justify-between gap-2 rounded border border-gray-200 bg-white p-4 hover:bg-gray-50"
            >
              <div>
                <p className="font-medium text-gray-900">{o.order_number}</p>
                <p className="text-sm text-gray-500">{formatDateTime(o.created_at)}</p>
              </div>
              <span data-testid={`order-status-${o.id}`} className="rounded bg-green-100 px-2 py-1 text-sm font-medium text-green-800">
                {o.status}
              </span>
              <span className="font-semibold text-gray-900">{money(o.total)}</span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function OrdersPage() {
  return (
    <RoleGuard roles={["CUSTOMER"]}>
      <OrdersPageContent />
    </RoleGuard>
  );
}
