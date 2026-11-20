"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { api, errorMessage, fieldErrorMap } from "@/lib/api";
import type { Banner } from "@/lib/types";

export default function AdminBannersPage() {
  const [banners, setBanners] = useState<Banner[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [title, setTitle] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [linkUrl, setLinkUrl] = useState("");
  const [displayOrder, setDisplayOrder] = useState("0");
  const [createErrors, setCreateErrors] = useState<Record<string, string>>({});
  const [createError, setCreateError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setBanners(await api.get<Banner[]>("/admin/banners"));
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setCreateError(null);
    setCreateErrors({});
    setCreating(true);
    try {
      await api.post("/admin/banners", {
        title,
        image_url: imageUrl,
        link_url: linkUrl || null,
        display_order: Number(displayOrder),
        active: true,
      });
      setTitle("");
      setImageUrl("");
      setLinkUrl("");
      setDisplayOrder("0");
      await load();
    } catch (err) {
      setCreateErrors(fieldErrorMap(err));
      setCreateError(errorMessage(err));
    } finally {
      setCreating(false);
    }
  }

  async function toggleActive(banner: Banner) {
    try {
      await api.put(`/admin/banners/${banner.id}`, { active: !banner.active });
      await load();
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  async function remove(bannerId: number) {
    try {
      await api.delete(`/admin/banners/${bannerId}`);
      await load();
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Banners</h1>

      <form
        id="admin-banner-create-form"
        data-testid="admin-banner-create-form"
        onSubmit={handleCreate}
        className="mb-6 grid grid-cols-1 gap-3 rounded-lg border border-gray-200 bg-white p-4 sm:grid-cols-2"
      >
        <div>
          <label htmlFor="admin-banner-title" className="mb-1 block text-sm font-medium text-gray-700">
            Title
          </label>
          <input
            id="admin-banner-title"
            data-testid="admin-banner-title-input"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2"
          />
          {createErrors.title && <p data-testid="admin-banner-title-error" className="text-sm text-red-600">{createErrors.title}</p>}
        </div>
        <div>
          <label htmlFor="admin-banner-image-url" className="mb-1 block text-sm font-medium text-gray-700">
            Image URL
          </label>
          <input
            id="admin-banner-image-url"
            data-testid="admin-banner-image-url-input"
            value={imageUrl}
            onChange={(e) => setImageUrl(e.target.value)}
            required
            className="w-full rounded-lg border border-gray-300 px-3 py-2"
          />
          {createErrors.image_url && <p data-testid="admin-banner-image-url-error" className="text-sm text-red-600">{createErrors.image_url}</p>}
        </div>
        <div>
          <label htmlFor="admin-banner-link-url" className="mb-1 block text-sm font-medium text-gray-700">
            Link URL (optional)
          </label>
          <input
            id="admin-banner-link-url"
            data-testid="admin-banner-link-url-input"
            value={linkUrl}
            onChange={(e) => setLinkUrl(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2"
          />
        </div>
        <div>
          <label htmlFor="admin-banner-display-order" className="mb-1 block text-sm font-medium text-gray-700">
            Display order
          </label>
          <input
            id="admin-banner-display-order"
            data-testid="admin-banner-display-order-input"
            type="number"
            value={displayOrder}
            onChange={(e) => setDisplayOrder(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2"
          />
        </div>
        {createError && (
          <p id="admin-banner-create-error" data-testid="admin-banner-create-error" className="sm:col-span-2 text-sm text-red-600">
            {createError}
          </p>
        )}
        <button
          id="admin-banner-create-button"
          data-testid="admin-banner-create-button"
          type="submit"
          disabled={creating}
          className="sm:col-span-2 rounded-md bg-accent-500 px-4 py-2 font-medium text-gray-900 hover:bg-accent-600 disabled:opacity-50"
        >
          {creating ? "Creating..." : "Create banner"}
        </button>
      </form>

      {loading && (
        <p id="admin-banners-loading" data-testid="admin-banners-loading" className="text-gray-500">
          Loading banners...
        </p>
      )}
      {error && (
        <p id="admin-banners-error" data-testid="admin-banners-error" className="text-red-600">
          {error}
        </p>
      )}

      <ul id="admin-banners-list" data-testid="admin-banners-list" className="space-y-3">
        {banners.map((b) => (
          <li
            key={b.id}
            id={`admin-banner-row-${b.id}`}
            data-testid={`admin-banner-row-${b.id}`}
            className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-gray-200 bg-white p-4"
          >
            <div className="flex items-center gap-3">
              <img src={b.image_url} alt={b.title} className="h-12 w-20 rounded-lg object-cover" />
              <div>
                <p className="font-medium text-gray-900">{b.title}</p>
                <p className="text-sm text-gray-500">order {b.display_order}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                id={`admin-banner-toggle-${b.id}`}
                data-testid={`admin-banner-toggle-${b.id}`}
                onClick={() => toggleActive(b)}
                className={`rounded-full px-2 py-1 text-xs font-medium ${b.active ? "bg-emerald-100 text-emerald-800" : "bg-gray-200 text-gray-600"}`}
              >
                {b.active ? "Active" : "Inactive"}
              </button>
              <button
                id={`admin-banner-delete-${b.id}`}
                data-testid={`admin-banner-delete-${b.id}`}
                onClick={() => remove(b.id)}
                className="rounded-md border border-red-300 px-3 py-1 text-sm text-red-600 hover:bg-red-50"
              >
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
