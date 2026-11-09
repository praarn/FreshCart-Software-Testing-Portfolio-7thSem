"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { fieldErrorMap, errorMessage } from "@/lib/api";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [phone, setPhone] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFormError(null);
    setFieldErrors({});
    setSubmitting(true);
    try {
      await register(name, email, password, phone);
      router.push("/");
    } catch (err) {
      setFieldErrors(fieldErrorMap(err));
      setFormError(errorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-md px-4 py-10">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Create your account</h1>
      <form id="register-form" data-testid="register-form" onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="register-name" className="mb-1 block text-sm font-medium text-gray-700">
            Full name
          </label>
          <input
            id="register-name"
            data-testid="register-name-input"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="w-full rounded border border-gray-300 px-3 py-2 focus:border-green-600 focus:outline-none"
          />
          {fieldErrors.name && (
            <p id="register-name-error" data-testid="register-name-error" className="mt-1 text-sm text-red-600">
              {fieldErrors.name}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="register-email" className="mb-1 block text-sm font-medium text-gray-700">
            Email
          </label>
          <input
            id="register-email"
            data-testid="register-email-input"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full rounded border border-gray-300 px-3 py-2 focus:border-green-600 focus:outline-none"
          />
          {fieldErrors.email && (
            <p id="register-email-error" data-testid="register-email-error" className="mt-1 text-sm text-red-600">
              {fieldErrors.email}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="register-password" className="mb-1 block text-sm font-medium text-gray-700">
            Password
          </label>
          <input
            id="register-password"
            data-testid="register-password-input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full rounded border border-gray-300 px-3 py-2 focus:border-green-600 focus:outline-none"
          />
          <p className="mt-1 text-xs text-gray-500">8-20 characters, at least 1 letter and 1 digit.</p>
          {fieldErrors.password && (
            <p id="register-password-error" data-testid="register-password-error" className="mt-1 text-sm text-red-600">
              {fieldErrors.password}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="register-phone" className="mb-1 block text-sm font-medium text-gray-700">
            Phone
          </label>
          <input
            id="register-phone"
            data-testid="register-phone-input"
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            required
            className="w-full rounded border border-gray-300 px-3 py-2 focus:border-green-600 focus:outline-none"
          />
          <p className="mt-1 text-xs text-gray-500">10 digits, starting with 6-9.</p>
          {fieldErrors.phone && (
            <p id="register-phone-error" data-testid="register-phone-error" className="mt-1 text-sm text-red-600">
              {fieldErrors.phone}
            </p>
          )}
        </div>

        {formError && (
          <p id="register-form-error" data-testid="register-form-error" className="text-sm text-red-600">
            {formError}
          </p>
        )}

        <button
          id="register-submit-button"
          data-testid="register-submit-button"
          type="submit"
          disabled={submitting}
          className="w-full rounded bg-green-700 px-4 py-2 font-medium text-white hover:bg-green-800 disabled:opacity-50"
        >
          {submitting ? "Creating account..." : "Register"}
        </button>
      </form>
      <p className="mt-4 text-sm text-gray-600">
        Already have an account?{" "}
        <Link id="register-login-link" data-testid="register-login-link" href="/login" className="text-green-700 underline">
          Log in
        </Link>
      </p>
    </div>
  );
}
