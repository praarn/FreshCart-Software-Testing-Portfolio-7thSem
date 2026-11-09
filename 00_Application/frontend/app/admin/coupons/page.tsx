"use client";

import { useCallback, useEffect, useState } from "react";
import { api, errorMessage } from "@/lib/api";
import type { Coupon } from "@/lib/types";

export default function AdminCouponsPage() {
  const [coupons, setCoupons] = useState<Coupon[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setCoupons(await api.get<Coupon[]>("/admin/coupons"));
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function toggle(coupon: Coupon) {
    try {
      await api.patch(`/admin/coupons/${coupon.id}`, { active: !coupon.active });
      await load();
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  if (loading) {
    return (
      <p id="admin-coupons-loading" data-testid="admin-coupons-loading" className="text-gray-500">
        Loading...
      </p>
    );
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Coupons</h1>
      {error && (
        <p id="admin-coupons-error" data-testid="admin-coupons-error" className="text-red-600">
          {error}
        </p>
      )}
      <div className="overflow-x-auto">
        <table id="admin-coupons-table" data-testid="admin-coupons-table" className="w-full border-collapse bg-white text-sm">
          <thead>
            <tr className="border-b border-gray-200 text-left text-gray-500">
              <th className="p-2">Code</th>
              <th className="p-2">Type</th>
              <th className="p-2">Value</th>
              <th className="p-2">Min subtotal</th>
              <th className="p-2">Active</th>
            </tr>
          </thead>
          <tbody>
            {coupons.map((c) => (
              <tr key={c.id} data-testid={`admin-coupon-row-${c.id}`} className="border-b border-gray-100">
                <td className="p-2 font-mono">{c.code}</td>
                <td className="p-2">{c.type}</td>
                <td className="p-2">{c.value}</td>
                <td className="p-2">{c.min_subtotal}</td>
                <td className="p-2">
                  <button
                    id={`admin-coupon-toggle-${c.id}`}
                    data-testid={`admin-coupon-toggle-${c.id}`}
                    onClick={() => toggle(c)}
                    className={`rounded px-2 py-1 text-xs font-medium ${c.active ? "bg-green-100 text-green-800" : "bg-gray-200 text-gray-600"}`}
                  >
                    {c.active ? "Enabled" : "Disabled"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
