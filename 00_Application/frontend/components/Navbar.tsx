"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function Navbar() {
  const { user, logout } = useAuth();
  const router = useRouter();

  async function handleLogout() {
    await logout();
    router.push("/login");
  }

  return (
    <nav id="navbar" data-testid="navbar" className="bg-brand-700 text-white shadow-md">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-4">
        <Link id="nav-brand" data-testid="nav-brand" href="/" className="flex items-center gap-2 text-lg font-bold tracking-tight">
          <span className="flex h-7 w-7 items-center justify-center rounded-full bg-brand-50 text-brand-700">🌿</span>
          FreshCart
        </Link>
        <div className="flex flex-wrap items-center gap-5 text-sm font-medium">
          <Link id="nav-catalog" data-testid="nav-catalog" href="/" className="hover:underline">
            Catalog
          </Link>
          {user?.role === "CUSTOMER" && (
            <>
              <Link id="nav-cart" data-testid="nav-cart" href="/cart" className="hover:underline">
                Cart
              </Link>
              <Link id="nav-orders" data-testid="nav-orders" href="/orders" className="hover:underline">
                My Orders
              </Link>
            </>
          )}
          {user?.role === "ADMIN" && (
            <Link id="nav-admin" data-testid="nav-admin" href="/admin" className="hover:underline">
              Admin
            </Link>
          )}
          {user?.role === "DELIVERY_PARTNER" && (
            <Link id="nav-delivery" data-testid="nav-delivery" href="/delivery" className="hover:underline">
              Deliveries
            </Link>
          )}
          {user ? (
            <>
              <span id="nav-user-name" data-testid="nav-user-name" className="opacity-90">
                {user.name}
              </span>
              <button
                id="nav-logout-button"
                data-testid="nav-logout-button"
                onClick={handleLogout}
                className="rounded-full bg-brand-900 px-4 py-1.5 transition-colors hover:bg-brand-950"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <Link id="nav-login" data-testid="nav-login" href="/login" className="hover:underline">
                Login
              </Link>
              <Link
                id="nav-register"
                data-testid="nav-register"
                href="/register"
                className="rounded-full bg-brand-900 px-4 py-1.5 transition-colors hover:bg-brand-950"
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
