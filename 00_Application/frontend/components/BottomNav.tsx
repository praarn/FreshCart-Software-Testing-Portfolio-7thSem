"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { BoxIcon, CartIcon, DashboardIcon, HeartIcon, HomeIcon, TruckIcon, UserIcon } from "@/components/icons";
import type { ComponentType } from "react";

interface NavItem {
  href: string;
  label: string;
  Icon: ComponentType<{ className?: string }>;
  testid: string;
}

export default function BottomNav() {
  const { user } = useAuth();
  const pathname = usePathname();

  let items: NavItem[] = [{ href: "/", label: "Home", Icon: HomeIcon, testid: "bottom-nav-home" }];

  if (user?.role === "CUSTOMER") {
    items = [
      { href: "/", label: "Home", Icon: HomeIcon, testid: "bottom-nav-home" },
      { href: "/wishlist", label: "Wishlist", Icon: HeartIcon, testid: "bottom-nav-wishlist" },
      { href: "/cart", label: "Cart", Icon: CartIcon, testid: "bottom-nav-cart" },
      { href: "/orders", label: "Orders", Icon: BoxIcon, testid: "bottom-nav-orders" },
    ];
  } else if (user?.role === "ADMIN") {
    items = [
      { href: "/", label: "Home", Icon: HomeIcon, testid: "bottom-nav-home" },
      { href: "/admin", label: "Admin", Icon: DashboardIcon, testid: "bottom-nav-admin" },
    ];
  } else if (user?.role === "DELIVERY_PARTNER") {
    items = [
      { href: "/", label: "Home", Icon: HomeIcon, testid: "bottom-nav-home" },
      { href: "/delivery", label: "Deliveries", Icon: TruckIcon, testid: "bottom-nav-delivery" },
    ];
  } else {
    items = [
      { href: "/", label: "Home", Icon: HomeIcon, testid: "bottom-nav-home" },
      { href: "/login", label: "Login", Icon: UserIcon, testid: "bottom-nav-login" },
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
              active ? "text-gray-900" : "text-gray-400"
            }`}
          >
            <item.Icon className="h-5 w-5" />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
