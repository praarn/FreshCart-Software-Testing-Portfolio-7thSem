"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { useAuth } from "@/lib/auth";

export default function Navbar() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [searchValue, setSearchValue] = useState("");

  async function handleLogout() {
    await logout();
    router.push("/login");
  }

  function handleSearchSubmit(e: FormEvent) {
    e.preventDefault();
    const qs = searchValue ? `?search=${encodeURIComponent(searchValue)}` : "";
    router.push(`/${qs}`);
  }

  return (
    <nav id="navbar" data-testid="navbar" className="sticky top-0 z-20 border-b border-gray-100 bg-white shadow-sm">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-3 px-4 py-3">
        <Link id="nav-brand" data-testid="nav-brand" href="/" className="flex shrink-0 items-center gap-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-ink text-lg text-accent-400">⚡</span>
          <span className="text-lg font-extrabold tracking-tight text-gray-900">FreshCart</span>
        </Link>

        <form
          id="nav-search-form"
          data-testid="nav-search-form"
          onSubmit={handleSearchSubmit}
          className="order-last flex w-full flex-1 items-center sm:order-none sm:w-auto"
        >
          <div className="flex w-full items-center rounded-full border border-gray-200 bg-gray-50 px-4 py-2 focus-within:border-accent-400">
            <input
              id="nav-search-input"
              data-testid="nav-search-input"
              type="text"
              placeholder="Search for groceries, snacks & more..."
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              className="w-full bg-transparent text-sm text-gray-900 outline-none placeholder:text-gray-400"
            />
            <button id="nav-search-button" data-testid="nav-search-button" type="submit" aria-label="Search" className="text-gray-400">
              🔍
            </button>
          </div>
        </form>

        <div className="flex flex-wrap items-center gap-4 text-sm font-medium text-gray-700">
          <Link id="nav-catalog" data-testid="nav-catalog" href="/" className="hidden hover:text-gray-900 sm:inline">
            Catalog
          </Link>
          {user?.role === "CUSTOMER" && (
            <>
              <Link id="nav-wishlist" data-testid="nav-wishlist" href="/wishlist" className="hidden hover:text-gray-900 sm:inline">
                Wishlist
              </Link>
              <Link id="nav-orders" data-testid="nav-orders" href="/orders" className="hidden hover:text-gray-900 sm:inline">
                My Orders
              </Link>
              <Link
                id="nav-cart"
                data-testid="nav-cart"
                href="/cart"
                className="rounded-full bg-accent-500 px-4 py-2 font-semibold text-gray-900 hover:bg-accent-600"
              >
                🛒 Cart
              </Link>
            </>
          )}
          {user?.role === "ADMIN" && (
            <Link id="nav-admin" data-testid="nav-admin" href="/admin" className="hover:text-gray-900">
              Admin
            </Link>
          )}
          {user?.role === "DELIVERY_PARTNER" && (
            <Link id="nav-delivery" data-testid="nav-delivery" href="/delivery" className="hover:text-gray-900">
              Deliveries
            </Link>
          )}
          {user ? (
            <>
              <span id="nav-user-name" data-testid="nav-user-name" className="hidden text-gray-500 md:inline">
                {user.name}
              </span>
              <button
                id="nav-logout-button"
                data-testid="nav-logout-button"
                onClick={handleLogout}
                className="rounded-full bg-ink px-4 py-1.5 text-white transition-colors hover:bg-gray-800"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link id="nav-login" data-testid="nav-login" href="/login" className="hover:text-gray-900">
                Login
              </Link>
              <Link
                id="nav-register"
                data-testid="nav-register"
                href="/register"
                className="rounded-full bg-ink px-4 py-1.5 text-white transition-colors hover:bg-gray-800"
              >
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
