"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { api, errorMessage } from "@/lib/api";
import { money } from "@/lib/format";
import { useAuth } from "@/lib/auth";
import type { Category, Product, ProductListResponse } from "@/lib/types";

export default function CatalogPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [totalPages, setTotalPages] = useState(0);
  const [search, setSearch] = useState("");
  const [categoryId, setCategoryId] = useState<string>("");
  const [sort, setSort] = useState<string>("");
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [addingId, setAddingId] = useState<number | null>(null);
  const [addMessage, setAddMessage] = useState<string | null>(null);

  useEffect(() => {
    api.get<Category[]>("/catalog/categories").then(setCategories).catch(() => {});
  }, []);

  const loadProducts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (search) params.set("search", search);
      if (categoryId) params.set("category_id", categoryId);
      if (sort) params.set("sort", sort);
      params.set("page", String(page));
      const data = await api.get<ProductListResponse>(`/catalog/products?${params.toString()}`);
      setProducts(data.items);
      setTotalPages(data.total_pages);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [search, categoryId, sort, page]);

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);

  async function handleAddToCart(productId: number) {
    if (!user) {
      router.push("/login");
      return;
    }
    setAddingId(productId);
    setAddMessage(null);
    try {
      await api.post("/cart/items", { product_id: productId, quantity: 1 });
      setAddMessage("Added to cart.");
    } catch (err) {
      setAddMessage(errorMessage(err));
    } finally {
      setAddingId(null);
    }
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Shop Fresh Groceries</h1>

      <div id="catalog-filters" data-testid="catalog-filters" className="mb-6 flex flex-wrap gap-3">
        <input
          id="catalog-search-input"
          data-testid="catalog-search-input"
          type="text"
          placeholder="Search products..."
          value={search}
          onChange={(e) => {
            setPage(1);
            setSearch(e.target.value);
          }}
          className="flex-1 min-w-[200px] rounded-lg border border-gray-300 px-3 py-2 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
        />
        <select
          id="catalog-category-select"
          data-testid="catalog-category-select"
          value={categoryId}
          onChange={(e) => {
            setPage(1);
            setCategoryId(e.target.value);
          }}
          className="rounded-lg border border-gray-300 px-3 py-2 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
        >
          <option value="">All categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <select
          id="catalog-sort-select"
          data-testid="catalog-sort-select"
          value={sort}
          onChange={(e) => {
            setPage(1);
            setSort(e.target.value);
          }}
          className="rounded-lg border border-gray-300 px-3 py-2 focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-100"
        >
          <option value="">Sort: default</option>
          <option value="price_asc">Price: low to high</option>
          <option value="price_desc">Price: high to low</option>
        </select>
      </div>

      {addMessage && (
        <p id="catalog-add-message" data-testid="catalog-add-message" className="mb-4 text-sm text-brand-700">
          {addMessage}
        </p>
      )}

      {loading && (
        <p id="catalog-loading" data-testid="catalog-loading" className="text-gray-500">
          Loading products...
        </p>
      )}
      {error && (
        <p id="catalog-error" data-testid="catalog-error" className="text-red-600">
          {error}
        </p>
      )}
      {!loading && !error && products.length === 0 && (
        <p id="catalog-empty" data-testid="catalog-empty" className="text-gray-500">
          No products found.
        </p>
      )}

      <div id="catalog-product-grid" data-testid="catalog-product-grid" className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {products.map((p) => (
          <div
            key={p.id}
            id={`product-card-${p.id}`}
            data-testid={`product-card-${p.id}`}
            className="flex flex-col justify-between rounded-xl border border-gray-100 bg-white p-4 shadow-sm"
          >
            <div>
              <Link href={`/product/${p.id}`} id={`product-link-${p.id}`} data-testid={`product-link-${p.id}`}>
                <h2 className="font-semibold text-gray-900 hover:underline">{p.name}</h2>
              </Link>
              <p className="text-sm text-gray-500">
                {p.category_name} &middot; {p.unit}
              </p>
              <p className="mt-2 text-lg font-bold text-brand-700">{money(p.price)}</p>
              {p.avg_rating != null && <p className="text-sm text-yellow-600">★ {p.avg_rating.toFixed(1)}</p>}
              {p.stock === 0 ? (
                <p data-testid={`product-out-of-stock-${p.id}`} className="mt-1 text-sm font-medium text-red-600">
                  Out of stock
                </p>
              ) : (
                <p className="mt-1 text-sm text-gray-500">{p.stock} in stock</p>
              )}
            </div>
            <button
              id={`add-to-cart-button-${p.id}`}
              data-testid={`add-to-cart-button-${p.id}`}
              disabled={p.stock === 0 || addingId === p.id}
              onClick={() => handleAddToCart(p.id)}
              className="mt-3 rounded-full bg-brand-700 px-3 py-2 text-sm font-medium text-white hover:bg-brand-800 disabled:cursor-not-allowed disabled:bg-gray-300"
            >
              {p.stock === 0 ? "Out of stock" : addingId === p.id ? "Adding..." : "Add to cart"}
            </button>
          </div>
        ))}
      </div>

      {totalPages > 1 && (
        <div id="catalog-pagination" data-testid="catalog-pagination" className="mt-6 flex items-center justify-center gap-3">
          <button
            id="catalog-prev-page"
            data-testid="catalog-prev-page"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
            className="rounded-full border border-gray-300 px-3 py-1 disabled:opacity-50"
          >
            Previous
          </button>
          <span id="catalog-page-indicator" data-testid="catalog-page-indicator" className="text-sm text-gray-600">
            Page {page} of {totalPages}
          </span>
          <button
            id="catalog-next-page"
            data-testid="catalog-next-page"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="rounded-full border border-gray-300 px-3 py-1 disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
