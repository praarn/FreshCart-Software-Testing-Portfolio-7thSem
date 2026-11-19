"use client";

import { useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { useAuth } from "@/lib/auth";
import type { Role } from "@/lib/types";

export default function RoleGuard({ roles, children }: { roles: Role[]; children: ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  if (loading) {
    return (
      <div id="role-guard-loading" data-testid="role-guard-loading" className="p-8 text-center text-gray-500">
        Loading...
      </div>
    );
  }

  if (!user) return null;

  if (!roles.includes(user.role)) {
    return (
      <div id="role-guard-denied" data-testid="role-guard-denied" className="p-8 text-center text-red-600">
        You do not have access to this page.
      </div>
    );
  }

  return <>{children}</>;
}
