"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import RoleGuard from "@/components/RoleGuard";
import { api, errorMessage } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import type { Order, PaymentMethod, Slot } from "@/lib/types";

function CheckoutPageContent() {
  const router = useRouter();
  const [slots, setSlots] = useState<Slot[]>([]);
  const [line1, setLine1] = useState("");
  const [city, setCity] = useState("");
  const [pincode, setPincode] = useState("");
  const [slotStart, setSlotStart] = useState("");
  const [method, setMethod] = useState<PaymentMethod>("COD");
  const [upiId, setUpiId] = useState("");
  const [cardNumber, setCardNumber] = useState("");
  const [cardExpiry, setCardExpiry] = useState("");
  const [cvv, setCvv] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const loadSlots = useCallback(async () => {
    try {
      const data = await api.get<Slot[]>("/checkout/slots");
      setSlots(data);
    } catch {
      setSlots([]);
    }
  }, []);

  useEffect(() => {
    loadSlots();
  }, [loadSlots]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFormError(null);
    setSubmitting(true);
    try {
      const payment: Record<string, unknown> = { method };
      if (method === "UPI") payment.upi_id = upiId;
      if (method === "CARD") {
        payment.card_number = cardNumber;
        payment.card_expiry = cardExpiry;
        payment.cvv = cvv;
      }
      const order = await api.post<Order>("/checkout", {
        address: { line1, city, pincode },
        slot_start: slotStart,
        payment,
      });
      router.push(`/orders/${order.id}`);
    } catch (err) {
      setFormError(errorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Checkout</h1>
      <form id="checkout-form" data-testid="checkout-form" onSubmit={handleSubmit} className="space-y-6">
        <fieldset className="rounded border border-gray-200 bg-white p-4">
          <legend className="mb-2 font-semibold text-gray-900">Delivery address</legend>
          <label htmlFor="checkout-line1" className="mb-1 block text-sm font-medium text-gray-700">
            Address line 1
          </label>
          <input
            id="checkout-line1"
            data-testid="checkout-line1-input"
            type="text"
            value={line1}
            onChange={(e) => setLine1(e.target.value)}
            required
            className="mb-3 w-full rounded border border-gray-300 px-3 py-2"
          />
          <label htmlFor="checkout-city" className="mb-1 block text-sm font-medium text-gray-700">
            City
          </label>
          <input
            id="checkout-city"
            data-testid="checkout-city-input"
            type="text"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            required
            className="mb-3 w-full rounded border border-gray-300 px-3 py-2"
          />
          <label htmlFor="checkout-pincode" className="mb-1 block text-sm font-medium text-gray-700">
            Pincode
          </label>
          <input
            id="checkout-pincode"
            data-testid="checkout-pincode-input"
            type="text"
            value={pincode}
            onChange={(e) => setPincode(e.target.value)}
            required
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
          <p className="mt-1 text-xs text-gray-500">Serviceable pincodes: 560001-560100.</p>
        </fieldset>

        <fieldset className="rounded border border-gray-200 bg-white p-4">
          <legend className="mb-2 font-semibold text-gray-900">Delivery slot</legend>
          <select
            id="checkout-slot-select"
            data-testid="checkout-slot-select"
            value={slotStart}
            onChange={(e) => setSlotStart(e.target.value)}
            required
            className="w-full rounded border border-gray-300 px-3 py-2"
          >
            <option value="">Select a slot</option>
            {slots.map((s) => (
              <option key={s.slot_start} value={s.slot_start} disabled={!s.available}>
                {formatDateTime(s.slot_start)} {s.available ? `(${s.remaining_capacity} left)` : "(full)"}
              </option>
            ))}
          </select>
        </fieldset>

        <fieldset className="rounded border border-gray-200 bg-white p-4">
          <legend className="mb-2 font-semibold text-gray-900">Payment</legend>
          <select
            id="checkout-payment-method"
            data-testid="checkout-payment-method-select"
            value={method}
            onChange={(e) => setMethod(e.target.value as PaymentMethod)}
            className="mb-3 w-full rounded border border-gray-300 px-3 py-2"
          >
            <option value="COD">Cash on Delivery</option>
            <option value="UPI">UPI</option>
            <option value="CARD">Card</option>
          </select>

          {method === "UPI" && (
            <div>
              <label htmlFor="checkout-upi-id" className="mb-1 block text-sm font-medium text-gray-700">
                UPI ID
              </label>
              <input
                id="checkout-upi-id"
                data-testid="checkout-upi-id-input"
                type="text"
                placeholder="name@bank"
                value={upiId}
                onChange={(e) => setUpiId(e.target.value)}
                required
                className="w-full rounded border border-gray-300 px-3 py-2"
              />
            </div>
          )}

          {method === "CARD" && (
            <div className="space-y-3">
              <div>
                <label htmlFor="checkout-card-number" className="mb-1 block text-sm font-medium text-gray-700">
                  Card number
                </label>
                <input
                  id="checkout-card-number"
                  data-testid="checkout-card-number-input"
                  type="text"
                  value={cardNumber}
                  onChange={(e) => setCardNumber(e.target.value)}
                  required
                  className="w-full rounded border border-gray-300 px-3 py-2"
                />
              </div>
              <div className="flex gap-3">
                <div className="flex-1">
                  <label htmlFor="checkout-card-expiry" className="mb-1 block text-sm font-medium text-gray-700">
                    Expiry (MM/YY)
                  </label>
                  <input
                    id="checkout-card-expiry"
                    data-testid="checkout-card-expiry-input"
                    type="text"
                    placeholder="12/30"
                    value={cardExpiry}
                    onChange={(e) => setCardExpiry(e.target.value)}
                    required
                    className="w-full rounded border border-gray-300 px-3 py-2"
                  />
                </div>
                <div className="flex-1">
                  <label htmlFor="checkout-cvv" className="mb-1 block text-sm font-medium text-gray-700">
                    CVV
                  </label>
                  <input
                    id="checkout-cvv"
                    data-testid="checkout-cvv-input"
                    type="password"
                    value={cvv}
                    onChange={(e) => setCvv(e.target.value)}
                    required
                    className="w-full rounded border border-gray-300 px-3 py-2"
                  />
                </div>
              </div>
            </div>
          )}
        </fieldset>

        {formError && (
          <p id="checkout-form-error" data-testid="checkout-form-error" className="text-sm text-red-600">
            {formError}
          </p>
        )}

        <button
          id="checkout-submit-button"
          data-testid="checkout-submit-button"
          type="submit"
          disabled={submitting}
          className="w-full rounded bg-green-700 px-4 py-3 font-medium text-white hover:bg-green-800 disabled:opacity-50"
        >
          {submitting ? "Placing order..." : "Place order"}
        </button>
      </form>
    </div>
  );
}

export default function CheckoutPage() {
  return (
    <RoleGuard roles={["CUSTOMER"]}>
      <CheckoutPageContent />
    </RoleGuard>
  );
}
