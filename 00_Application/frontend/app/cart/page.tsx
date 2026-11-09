"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import Link from "next/link";
import RoleGuard from "@/components/RoleGuard";
import { api, errorMessage } from "@/lib/api";
import { money } from "@/lib/format";
import type { Cart } from "@/lib/types";

function CartPageContent() {
  const [cart, setCart] = useState<Cart | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [couponCode, setCouponCode] = useState("");
  const [couponError, setCouponError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.get<Cart>("/cart");
      setCart(data);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function updateQuantity(itemId: number, quantity: number) {
    setBusy(true);
    setError(null);
    try {
      const data = await api.put<Cart>(`/cart/items/${itemId}`, { quantity });
      setCart(data);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function removeItem(itemId: number) {
    setBusy(true);
    setError(null);
    try {
      const data = await api.delete<Cart>(`/cart/items/${itemId}`);
      setCart(data);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function clearCart() {
    setBusy(true);
    setError(null);
    try {
      const data = await api.delete<Cart>("/cart");
      setCart(data);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function applyCoupon(e: FormEvent) {
    e.preventDefault();
    setCouponError(null);
    setBusy(true);
    try {
      const data = await api.post<Cart>("/cart/coupon", { code: couponCode });
      setCart(data);
      setCouponCode("");
    } catch (err) {
      setCouponError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function removeCoupon() {
    setBusy(true);
    try {
      const data = await api.delete<Cart>("/cart/coupon");
      setCart(data);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return (
      <p id="cart-loading" data-testid="cart-loading" className="p-8 text-center text-gray-500">
        Loading cart...
      </p>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Your Cart</h1>

      {error && (
        <p id="cart-error" data-testid="cart-error" className="mb-4 text-red-600">
          {error}
        </p>
      )}

      {!cart || cart.items.length === 0 ? (
        <p id="cart-empty" data-testid="cart-empty" className="text-gray-500">
          Your cart is empty.{" "}
          <Link href="/" className="text-gray-900 underline hover:text-accent-700">
            Browse products
          </Link>
          .
        </p>
      ) : (
        <>
          <ul id="cart-items-list" data-testid="cart-items-list" className="space-y-3">
            {cart.items.map((item) => (
              <li
                key={item.id}
                id={`cart-item-${item.id}`}
                data-testid={`cart-item-${item.id}`}
                className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-gray-100 bg-white p-4 shadow-sm"
              >
                <div>
                  <p className="font-medium text-gray-900">{item.product_name}</p>
                  <p className="text-sm text-gray-500">
                    {money(item.unit_price)} / {item.unit}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <select
                    id={`cart-item-qty-${item.id}`}
                    data-testid={`cart-item-qty-${item.id}`}
                    value={item.quantity}
                    disabled={busy}
                    onChange={(e) => updateQuantity(item.id, Number(e.target.value))}
                    className="rounded-lg border border-gray-300 px-2 py-1 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-100"
                  >
                    {Array.from({ length: Math.min(10, item.stock) }, (_, i) => i + 1).map((n) => (
                      <option key={n} value={n}>
                        {n}
                      </option>
                    ))}
                  </select>
                  <span className="w-20 text-right font-medium text-gray-900">{money(item.line_total)}</span>
                  <button
                    id={`cart-item-remove-${item.id}`}
                    data-testid={`cart-item-remove-${item.id}`}
                    disabled={busy}
                    onClick={() => removeItem(item.id)}
                    className="rounded-full border border-red-300 px-2 py-1 text-sm text-red-600 hover:bg-red-50"
                  >
                    Remove
                  </button>
                </div>
              </li>
            ))}
          </ul>

          <button
            id="cart-clear-button"
            data-testid="cart-clear-button"
            disabled={busy}
            onClick={clearCart}
            className="mt-4 text-sm text-red-600 underline"
          >
            Clear cart
          </button>

          <form id="coupon-form" data-testid="coupon-form" onSubmit={applyCoupon} className="mt-6 flex flex-wrap items-end gap-2">
            <div className="flex-1">
              <label htmlFor="coupon-code-input" className="mb-1 block text-sm font-medium text-gray-700">
                Coupon code
              </label>
              <input
                id="coupon-code-input"
                data-testid="coupon-code-input"
                type="text"
                value={couponCode}
                onChange={(e) => setCouponCode(e.target.value)}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-100"
              />
            </div>
            <button
              id="coupon-apply-button"
              data-testid="coupon-apply-button"
              type="submit"
              disabled={busy || !couponCode}
              className="rounded-full bg-accent-500 px-4 py-2 text-sm font-medium text-gray-900 hover:bg-accent-600 disabled:opacity-50"
            >
              Apply
            </button>
            {cart.coupon_code && (
              <button
                id="coupon-remove-button"
                data-testid="coupon-remove-button"
                type="button"
                disabled={busy}
                onClick={removeCoupon}
                className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-100"
              >
                Remove coupon
              </button>
            )}
          </form>
          {couponError && (
            <p id="coupon-error" data-testid="coupon-error" className="mt-2 text-sm text-red-600">
              {couponError}
            </p>
          )}
          {cart.coupon_code && (
            <p id="coupon-applied" data-testid="coupon-applied" className="mt-2 text-sm text-emerald-700">
              Applied coupon: {cart.coupon_code}
            </p>
          )}

          <div id="cart-summary" data-testid="cart-summary" className="mt-6 rounded-xl border border-gray-100 bg-white p-4 shadow-sm">
            <div className="flex justify-between py-1">
              <span>Subtotal</span>
              <span data-testid="cart-subtotal">{money(cart.subtotal)}</span>
            </div>
            <div className="flex justify-between py-1">
              <span>Discount</span>
              <span data-testid="cart-discount">-{money(cart.discount)}</span>
            </div>
            <div className="flex justify-between py-1">
              <span>Delivery fee</span>
              <span data-testid="cart-delivery-fee">{money(cart.delivery_fee)}</span>
            </div>
            <div className="mt-2 flex justify-between border-t border-gray-200 pt-2 text-lg font-bold">
              <span>Total</span>
              <span data-testid="cart-total">{money(cart.total)}</span>
            </div>
          </div>

          <Link
            id="cart-checkout-link"
            data-testid="cart-checkout-link"
            href="/checkout"
            className="mt-6 block w-full rounded-full bg-accent-500 px-4 py-3 text-center font-medium text-gray-900 hover:bg-accent-600"
          >
            Proceed to checkout
          </Link>
        </>
      )}
    </div>
  );
}

export default function CartPage() {
  return (
    <RoleGuard roles={["CUSTOMER"]}>
      <CartPageContent />
    </RoleGuard>
  );
}
