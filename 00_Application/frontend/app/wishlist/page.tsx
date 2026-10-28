"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import RoleGuard from "@/components/RoleGuard";
import { api, errorMessage } from "@/lib/api";
import { money } from "@/lib/format";
import type { WishlistItem } from "@/lib/types";

function WishlistPageContent() {
  const [items, setItems] = useState<WishlistItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setItems(await api.get<WishlistItem[]>("/wishlist"));
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function remove(productId: number) {
    setBusyId(productId);
    try {
      await api.delete(`/wishlist/items/${productId}`);
      setItems((prev) => prev.filter((i) => i.product.id !== productId));
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusyId(null);
    }
  }

  async function addToCart(productId: number) {
    setBusyId(productId);
    setMessage(null);
    try {
      await api.post("/cart/items", { product_id: productId, quantity: 1 });
      setMessage("Added to cart.");
    } catch (err) {
      setMessage(errorMessage(err));
    } finally {
      setBusyId(null);
    }
  }

  if (loading) {
    return (
      <p id="wishlist-loading" data-testid="wishlist-loading" className="p-8 text-center text-gray-500">
        Loading wishlist...
      </p>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">My Wishlist</h1>

      {error && (
        <p id="wishlist-error" data-testid="wishlist-error" className="mb-4 text-red-600">
          {error}
        </p>
      )}
      {message && (
        <p id="wishlist-message" data-testid="wishlist-message" className="mb-4 text-sm text-emerald-700">
          {message}
        </p>
      )}

      {items.length === 0 ? (
        <p id="wishlist-empty" data-testid="wishlist-empty" className="text-gray-500">
          Your wishlist is empty.{" "}
          <Link href="/" className="text-gray-900 underline hover:text-accent-700">
            Browse products
          </Link>
          .
        </p>
      ) : (
        <div id="wishlist-grid" data-testid="wishlist-grid" className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {items.map(({ id, product: p }) => (
            <div
              key={id}
              id={`wishlist-item-${p.id}`}
              data-testid={`wishlist-item-${p.id}`}
              className="flex flex-col justify-between rounded-xl border border-gray-100 bg-white p-4 shadow-sm"
            >
              <div>
                <Link href={`/product/${p.id}`} className="font-semibold text-gray-900 hover:underline">
                  {p.name}
                </Link>
                <p className="text-sm text-gray-500">
                  {p.category_name} &middot; {p.unit}
                </p>
                <p className="mt-2 text-lg font-bold text-gray-900">{money(p.price)}</p>
                <p className="mt-1 text-sm text-gray-500">{p.stock === 0 ? "Out of stock" : `${p.stock} in stock`}</p>
              </div>
              <div className="mt-3 flex gap-2">
                <button
                  id={`wishlist-add-to-cart-${p.id}`}
                  data-testid={`wishlist-add-to-cart-${p.id}`}
                  disabled={p.stock === 0 || busyId === p.id}
                  onClick={() => addToCart(p.id)}
                  className="flex-1 rounded-full bg-accent-500 px-3 py-2 text-sm font-medium text-gray-900 hover:bg-accent-600 disabled:cursor-not-allowed disabled:bg-gray-300"
                >
                  Add to cart
                </button>
                <button
                  id={`wishlist-remove-${p.id}`}
                  data-testid={`wishlist-remove-${p.id}`}
                  disabled={busyId === p.id}
                  onClick={() => remove(p.id)}
                  className="rounded-full border border-red-300 px-3 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function WishlistPage() {
  return (
    <RoleGuard roles={["CUSTOMER"]}>
      <WishlistPageContent />
    </RoleGuard>
  );
}
