"use client";

import Link from "next/link";
import RoleGuard from "@/components/RoleGuard";

const TABS = [
  { href: "/admin", label: "Dashboard", testid: "admin-tab-dashboard" },
  { href: "/admin/products", label: "Products", testid: "admin-tab-products" },
  { href: "/admin/orders", label: "Orders", testid: "admin-tab-orders" },
  { href: "/admin/coupons", label: "Coupons", testid: "admin-tab-coupons" },
  { href: "/admin/users", label: "Users", testid: "admin-tab-users" },
  { href: "/admin/audit-log", label: "Audit Log", testid: "admin-tab-audit-log" },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <RoleGuard roles={["ADMIN"]}>
      <div className="mx-auto max-w-6xl px-4 py-6">
        <nav id="admin-subnav" data-testid="admin-subnav" className="mb-6 flex flex-wrap gap-2 border-b border-gray-200 pb-3">
          {TABS.map((t) => (
            <Link
              key={t.href}
              id={t.testid}
              data-testid={t.testid}
              href={t.href}
              className="rounded-full px-3 py-1 text-sm font-medium text-gray-700 hover:bg-gray-100"
            >
              {t.label}
            </Link>
          ))}
        </nav>
        {children}
      </div>
    </RoleGuard>
  );
}
