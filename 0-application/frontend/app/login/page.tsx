"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { errorMessage } from "@/lib/api";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFormError(null);
    setSubmitting(true);
    try {
      await login(email, password);
      router.push("/");
    } catch (err) {
      setFormError(errorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-md px-4 py-10">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Log in</h1>
      <form id="login-form" data-testid="login-form" onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="login-email" className="mb-1 block text-sm font-medium text-gray-700">
            Email
          </label>
          <input
            id="login-email"
            data-testid="login-email-input"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-100"
          />
        </div>

        <div>
          <label htmlFor="login-password" className="mb-1 block text-sm font-medium text-gray-700">
            Password
          </label>
          <input
            id="login-password"
            data-testid="login-password-input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-100"
          />
        </div>

        {formError && (
          <p id="login-form-error" data-testid="login-form-error" className="text-sm text-red-600">
            {formError}
          </p>
        )}

        <button
          id="login-submit-button"
          data-testid="login-submit-button"
          type="submit"
          disabled={submitting}
          className="w-full rounded-md bg-accent-500 px-4 py-2 font-medium text-gray-900 hover:bg-accent-600 disabled:opacity-50"
        >
          {submitting ? "Logging in..." : "Log in"}
        </button>
      </form>
      <p className="mt-4 text-sm text-gray-600">
        No account yet?{" "}
        <Link id="login-register-link" data-testid="login-register-link" href="/register" className="text-gray-900 underline hover:text-accent-700">
          Register
        </Link>
      </p>

      <div id="demo-accounts" data-testid="demo-accounts" className="mt-8 rounded-lg border border-gray-200 bg-gray-50 p-4">
        <h2 className="text-sm font-semibold text-gray-900">Demo accounts</h2>
        <p className="mb-3 text-xs text-gray-500">
          FreshCart has three roles. Pick one to fill the form, then press Log in.
        </p>
        <div className="flex flex-wrap gap-2">
          {DEMO_ACCOUNTS.map((a) => (
            <button
              key={a.role}
              type="button"
              id={`demo-account-${a.role}`}
              data-testid={`demo-account-${a.role}`}
              onClick={() => {
                setEmail(a.email);
                setPassword(a.password);
              }}
              className="rounded-md border border-gray-300 bg-white px-3 py-1.5 text-left text-xs text-gray-700 hover:border-gray-500"
            >
              <span className="block font-semibold text-gray-900">{a.label}</span>
              <span className="block">{a.email}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

const DEMO_ACCOUNTS = [
  { role: "customer", label: "Customer", email: "customer1@freshcart.test", password: "Customer@1234" },
  { role: "admin", label: "Admin", email: "admin@freshcart.test", password: "Admin@1234" },
  { role: "delivery", label: "Delivery partner", email: "driver1@freshcart.test", password: "Driver@1234" },
];
