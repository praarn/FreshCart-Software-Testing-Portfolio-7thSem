"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { api, errorMessage, fieldErrorMap } from "@/lib/api";
import { money } from "@/lib/format";
import type { Category, Product, ProductUnit } from "@/lib/types";

const UNITS: ProductUnit[] = ["kg", "g", "l", "ml", "pc", "pack"];

export default function AdminProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stockEdits, setStockEdits] = useState<Record<number, string>>({});

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [stock, setStock] = useState("");
  const [unit, setUnit] = useState<ProductUnit>("pc");
  const [categoryId, setCategoryId] = useState("");
  const [createErrors, setCreateErrors] = useState<Record<string, string>>({});
  const [createError, setCreateError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [p, c] = await Promise.all([api.get<Product[]>("/admin/products"), api.get<Category[]>("/catalog/categories")]);
      setProducts(p);
      setCategories(c);
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
      await api.post("/admin/products", {
        name,
        description: description || null,
        price,
        stock: Number(stock),
        unit,
        category_id: Number(categoryId),
        active: true,
      });
      setName("");
      setDescription("");
      setPrice("");
      setStock("");
      setCategoryId("");
      await load();
    } catch (err) {
      setCreateErrors(fieldErrorMap(err));
      setCreateError(errorMessage(err));
    } finally {
      setCreating(false);
    }
  }

  async function saveStock(productId: number) {
    const value = stockEdits[productId];
    if (value === undefined) return;
    try {
      await api.patch(`/admin/products/${productId}/stock`, { stock: Number(value) });
      await load();
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  async function toggleActive(product: Product) {
    try {
      await api.patch(`/admin/products/${product.id}/active`, { active: !product.active });
      await load();
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Products</h1>

      <form id="admin-product-create-form" data-testid="admin-product-create-form" onSubmit={handleCreate} className="mb-6 grid grid-cols-1 gap-3 rounded border border-gray-200 bg-white p-4 sm:grid-cols-2">
        <div>
          <label htmlFor="admin-product-name" className="mb-1 block text-sm font-medium text-gray-700">
            Name
          </label>
          <input
            id="admin-product-name"
            data-testid="admin-product-name-input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
          {createErrors.name && <p data-testid="admin-product-name-error" className="text-sm text-red-600">{createErrors.name}</p>}
        </div>
        <div>
          <label htmlFor="admin-product-price" className="mb-1 block text-sm font-medium text-gray-700">
            Price
          </label>
          <input
            id="admin-product-price"
            data-testid="admin-product-price-input"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            required
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
          {createErrors.price && <p data-testid="admin-product-price-error" className="text-sm text-red-600">{createErrors.price}</p>}
        </div>
        <div>
          <label htmlFor="admin-product-stock" className="mb-1 block text-sm font-medium text-gray-700">
            Stock
          </label>
          <input
            id="admin-product-stock"
            data-testid="admin-product-stock-input"
            value={stock}
            onChange={(e) => setStock(e.target.value)}
            required
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
          {createErrors.stock && <p data-testid="admin-product-stock-error" className="text-sm text-red-600">{createErrors.stock}</p>}
        </div>
        <div>
          <label htmlFor="admin-product-unit" className="mb-1 block text-sm font-medium text-gray-700">
            Unit
          </label>
          <select
            id="admin-product-unit"
            data-testid="admin-product-unit-select"
            value={unit}
            onChange={(e) => setUnit(e.target.value as ProductUnit)}
            className="w-full rounded border border-gray-300 px-3 py-2"
          >
            {UNITS.map((u) => (
              <option key={u} value={u}>
                {u}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="admin-product-category" className="mb-1 block text-sm font-medium text-gray-700">
            Category
          </label>
          <select
            id="admin-product-category"
            data-testid="admin-product-category-select"
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
            required
            className="w-full rounded border border-gray-300 px-3 py-2"
          >
            <option value="">Select category</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div className="sm:col-span-2">
          <label htmlFor="admin-product-description" className="mb-1 block text-sm font-medium text-gray-700">
            Description
          </label>
          <input
            id="admin-product-description"
            data-testid="admin-product-description-input"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
        </div>
        {createError && (
          <p id="admin-product-create-error" data-testid="admin-product-create-error" className="sm:col-span-2 text-sm text-red-600">
            {createError}
          </p>
        )}
        <button
          id="admin-product-create-button"
          data-testid="admin-product-create-button"
          type="submit"
          disabled={creating}
          className="sm:col-span-2 rounded bg-green-700 px-4 py-2 font-medium text-white hover:bg-green-800 disabled:opacity-50"
        >
          {creating ? "Creating..." : "Create product"}
        </button>
      </form>

      {loading && (
        <p id="admin-products-loading" data-testid="admin-products-loading" className="text-gray-500">
          Loading products...
        </p>
      )}
      {error && (
        <p id="admin-products-error" data-testid="admin-products-error" className="text-red-600">
          {error}
        </p>
      )}

      <div id="admin-products-table" data-testid="admin-products-table" className="overflow-x-auto">
        <table className="w-full border-collapse bg-white text-sm">
          <thead>
            <tr className="border-b border-gray-200 text-left text-gray-500">
              <th className="p-2">Name</th>
              <th className="p-2">Category</th>
              <th className="p-2">Price</th>
              <th className="p-2">Stock</th>
              <th className="p-2">Active</th>
            </tr>
          </thead>
          <tbody>
            {products.map((p) => (
              <tr key={p.id} data-testid={`admin-product-row-${p.id}`} className="border-b border-gray-100">
                <td className="p-2">{p.name}</td>
                <td className="p-2">{p.category_name}</td>
                <td className="p-2">{money(p.price)}</td>
                <td className="p-2">
                  <div className="flex items-center gap-1">
                    <input
                      id={`admin-product-stock-input-${p.id}`}
                      data-testid={`admin-product-stock-input-${p.id}`}
                      defaultValue={p.stock}
                      onChange={(e) => setStockEdits((prev) => ({ ...prev, [p.id]: e.target.value }))}
                      className="w-20 rounded border border-gray-300 px-2 py-1"
                    />
                    <button
                      id={`admin-product-stock-save-${p.id}`}
                      data-testid={`admin-product-stock-save-${p.id}`}
                      onClick={() => saveStock(p.id)}
                      className="rounded border border-gray-300 px-2 py-1 text-xs"
                    >
                      Save
                    </button>
                  </div>
                </td>
                <td className="p-2">
                  <button
                    id={`admin-product-active-toggle-${p.id}`}
                    data-testid={`admin-product-active-toggle-${p.id}`}
                    onClick={() => toggleActive(p)}
                    className={`rounded px-2 py-1 text-xs font-medium ${p.active ? "bg-green-100 text-green-800" : "bg-gray-200 text-gray-600"}`}
                  >
                    {p.active ? "Active" : "Inactive"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
