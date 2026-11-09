"use client";

import { useEffect, useState } from "react";
import { api, errorMessage } from "@/lib/api";
import { money } from "@/lib/format";
import type { Dashboard } from "@/lib/types";

export default function AdminDashboardPage() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<Dashboard>("/admin/dashboard").then(setDashboard).catch((err) => setError(errorMessage(err)));
  }, []);

  if (error) {
    return (
      <p id="admin-dashboard-error" data-testid="admin-dashboard-error" className="text-red-600">
        {error}
      </p>
    );
  }
  if (!dashboard) {
    return (
      <p id="admin-dashboard-loading" data-testid="admin-dashboard-loading" className="text-gray-500">
        Loading...
      </p>
    );
  }

  return (
    <div id="admin-dashboard" data-testid="admin-dashboard">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Dashboard</h1>
      <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div id="dashboard-orders-today" data-testid="dashboard-orders-today" className="rounded border border-gray-200 bg-white p-4">
          <p className="text-sm text-gray-500">Orders today</p>
          <p className="text-3xl font-bold text-gray-900">{dashboard.orders_today}</p>
        </div>
        <div id="dashboard-revenue-today" data-testid="dashboard-revenue-today" className="rounded border border-gray-200 bg-white p-4">
          <p className="text-sm text-gray-500">Revenue today</p>
          <p className="text-3xl font-bold text-gray-900">{money(dashboard.revenue_today)}</p>
        </div>
      </div>

      <h2 className="mb-2 font-semibold text-gray-900">Low stock products (&lt; 10)</h2>
      {dashboard.low_stock_products.length === 0 ? (
        <p id="dashboard-low-stock-empty" data-testid="dashboard-low-stock-empty" className="text-gray-500">
          No low-stock products.
        </p>
      ) : (
        <ul id="dashboard-low-stock-list" data-testid="dashboard-low-stock-list" className="space-y-1">
          {dashboard.low_stock_products.map((p) => (
            <li key={p.id} data-testid={`dashboard-low-stock-${p.id}`} className="flex justify-between rounded border border-gray-200 bg-white px-3 py-2 text-sm">
              <span>{p.name}</span>
              <span className="font-medium text-red-600">{p.stock} left</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
