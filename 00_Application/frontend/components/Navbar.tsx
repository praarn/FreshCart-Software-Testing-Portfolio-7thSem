"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { useAuth } from "@/lib/auth";
import { CartIcon, LogoMark, SearchIcon } from "@/components/icons";

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
    <nav id="navbar" data-testid="navbar" className="sticky top-0 z-20 border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-3 px-4 py-3">
        <Link id="nav-brand" data-testid="nav-brand" href="/" className="flex shrink-0 items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-md bg-ink text-white">
            <LogoMark className="h-4.5 w-4.5" />
          </span>
          <span className="text-lg font-bold tracking-tight text-gray-900">FreshCart</span>
        </Link>

        <form
          id="nav-search-form"
          data-testid="nav-search-form"
          onSubmit={handleSearchSubmit}
          className="order-last flex w-full flex-1 items-center sm:order-none sm:w-auto"
        >
          <div className="flex w-full items-center gap-2 rounded-md border border-gray-300 bg-gray-50 px-3 py-2 focus-within:border-ink">
            <SearchIcon className="h-4 w-4 shrink-0 text-gray-400" />
            <input
              id="nav-search-input"
              data-testid="nav-search-input"
              type="text"
              placeholder="Search for groceries, snacks & more"
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              className="w-full bg-transparent text-sm text-gray-900 outline-none placeholder:text-gray-400"
            />
            <button id="nav-search-button" data-testid="nav-search-button" type="submit" aria-label="Search" className="sr-only">
              Search
            </button>
          </div>
        </form>

        <div className="flex flex-wrap items-center gap-4 text-sm font-medium text-gray-600">
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
                className="flex items-center gap-1.5 rounded-md bg-accent-500 px-3.5 py-2 font-medium text-gray-900 hover:bg-accent-600"
              >
                <CartIcon className="h-4 w-4" />
                Cart
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
                className="rounded-md border border-gray-300 px-3.5 py-2 text-gray-700 transition-colors hover:bg-gray-50"
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
                className="rounded-md bg-ink px-3.5 py-2 text-white transition-colors hover:bg-gray-800"
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
