"use client";

import { useCallback, useEffect, useState } from "react";
import { api, errorMessage } from "@/lib/api";
import type { User } from "@/lib/types";

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setUsers(await api.get<User[]>("/admin/users"));
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function lock(userId: number) {
    try {
      await api.post(`/admin/users/${userId}/lock`);
      await load();
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  async function unlock(userId: number) {
    try {
      await api.post(`/admin/users/${userId}/unlock`);
      await load();
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  if (loading) {
    return (
      <p id="admin-users-loading" data-testid="admin-users-loading" className="text-gray-500">
        Loading...
      </p>
    );
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Users</h1>
      {error && (
        <p id="admin-users-error" data-testid="admin-users-error" className="text-red-600">
          {error}
        </p>
      )}
      <div className="overflow-x-auto">
        <table id="admin-users-table" data-testid="admin-users-table" className="w-full border-collapse bg-white text-sm">
          <thead>
            <tr className="border-b border-gray-200 text-left text-gray-500">
              <th className="p-2">Name</th>
              <th className="p-2">Email</th>
              <th className="p-2">Role</th>
              <th className="p-2">Status</th>
              <th className="p-2">Action</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} data-testid={`admin-user-row-${u.id}`} className="border-b border-gray-100">
                <td className="p-2">{u.name}</td>
                <td className="p-2">{u.email}</td>
                <td className="p-2">{u.role}</td>
                <td className="p-2" data-testid={`admin-user-status-${u.id}`}>
                  {u.status}
                </td>
                <td className="p-2">
                  {u.status === "ACTIVE" ? (
                    <button
                      id={`admin-user-lock-${u.id}`}
                      data-testid={`admin-user-lock-${u.id}`}
                      onClick={() => lock(u.id)}
                      className="rounded-md border border-red-300 px-2 py-1 text-xs text-red-600 hover:bg-red-50"
                    >
                      Lock
                    </button>
                  ) : (
                    <button
                      id={`admin-user-unlock-${u.id}`}
                      data-testid={`admin-user-unlock-${u.id}`}
                      onClick={() => unlock(u.id)}
                      className="rounded-md border border-emerald-300 px-2 py-1 text-xs text-emerald-700 hover:bg-emerald-50"
                    >
                      Unlock
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
