"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";

interface NavItem {
  href: string;
  label: string;
  icon: string;
  testid: string;
}

export default function BottomNav() {
  const { user } = useAuth();
  const pathname = usePathname();

  let items: NavItem[] = [{ href: "/", label: "Home", icon: "🏠", testid: "bottom-nav-home" }];

  if (user?.role === "CUSTOMER") {
    items = [
      { href: "/", label: "Home", icon: "🏠", testid: "bottom-nav-home" },
      { href: "/wishlist", label: "Wishlist", icon: "❤️", testid: "bottom-nav-wishlist" },
      { href: "/cart", label: "Cart", icon: "🛒", testid: "bottom-nav-cart" },
      { href: "/orders", label: "Orders", icon: "📦", testid: "bottom-nav-orders" },
    ];
  } else if (user?.role === "ADMIN") {
    items = [
      { href: "/", label: "Home", icon: "🏠", testid: "bottom-nav-home" },
      { href: "/admin", label: "Admin", icon: "📊", testid: "bottom-nav-admin" },
    ];
  } else if (user?.role === "DELIVERY_PARTNER") {
    items = [
      { href: "/", label: "Home", icon: "🏠", testid: "bottom-nav-home" },
      { href: "/delivery", label: "Deliveries", icon: "🚚", testid: "bottom-nav-delivery" },
    ];
  } else {
    items = [
      { href: "/", label: "Home", icon: "🏠", testid: "bottom-nav-home" },
      { href: "/login", label: "Login", icon: "👤", testid: "bottom-nav-login" },
    ];
  }

  return (
    <nav
      id="bottom-nav"
      data-testid="bottom-nav"
      className="fixed inset-x-0 bottom-0 z-20 flex border-t border-gray-200 bg-white sm:hidden"
    >
      {items.map((item) => {
        const active = pathname === item.href;
        return (
          <Link
            key={item.href}
            id={item.testid}
            data-testid={item.testid}
            href={item.href}
            className={`flex flex-1 flex-col items-center gap-0.5 py-2 text-xs font-medium ${
              active ? "text-gray-900" : "text-gray-500"
            }`}
          >
            <span className="text-lg leading-none">{item.icon}</span>
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
