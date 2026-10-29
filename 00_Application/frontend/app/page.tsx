"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { api, errorMessage } from "@/lib/api";
import { money } from "@/lib/format";
import { useAuth } from "@/lib/auth";
import { HeartIcon } from "@/components/icons";
import type { Banner, Category, Product, ProductListResponse, PublicCoupon, WishlistItem } from "@/lib/types";

export default function CatalogPage() {
  return (
    <Suspense
      fallback={
        <p id="catalog-loading" data-testid="catalog-loading" className="p-8 text-center text-gray-500">
          Loading...
        </p>
      }
    >
      <CatalogPageContent />
    </Suspense>
  );
}

function CatalogPageContent() {
  const { user } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [categories, setCategories] = useState<Category[]>([]);
  const [banners, setBanners] = useState<Banner[]>([]);
  const [offers, setOffers] = useState<PublicCoupon[]>([]);
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
  const [wishlistIds, setWishlistIds] = useState<Set<number>>(new Set());
  const [wishlistBusyId, setWishlistBusyId] = useState<number | null>(null);

  useEffect(() => {
    api.get<Category[]>("/catalog/categories").then(setCategories).catch(() => {});
    api.get<Banner[]>("/banners").then(setBanners).catch(() => {});
    api.get<PublicCoupon[]>("/catalog/offers").then(setOffers).catch(() => {});
  }, []);

  useEffect(() => {
    if (user?.role !== "CUSTOMER") {
      setWishlistIds(new Set());
      return;
    }
    api
      .get<WishlistItem[]>("/wishlist")
      .then((items) => setWishlistIds(new Set(items.map((i) => i.product.id))))
      .catch(() => {});
  }, [user]);

  async function toggleWishlist(productId: number) {
    if (!user) {
      router.push("/login");
      return;
    }
    setWishlistBusyId(productId);
    try {
      if (wishlistIds.has(productId)) {
        await api.delete(`/wishlist/items/${productId}`);
        setWishlistIds((prev) => {
          const next = new Set(prev);
          next.delete(productId);
          return next;
        });
      } else {
        await api.post("/wishlist/items", { product_id: productId });
        setWishlistIds((prev) => new Set(prev).add(productId));
      }
    } catch {
      // best-effort toggle; ignore transient errors
    } finally {
      setWishlistBusyId(null);
    }
  }

  useEffect(() => {
    setSearch(searchParams.get("search") ?? "");
    setCategoryId(searchParams.get("category_id") ?? "");
    setPage(1);
  }, [searchParams]);

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

  function selectCategory(id: string) {
    setPage(1);
    setCategoryId((prev) => (prev === id ? "" : id));
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      {banners.length > 0 && (
        <div id="banner-carousel" data-testid="banner-carousel" className="mb-8 flex gap-4 overflow-x-auto pb-2">
          {banners.map((b) => {
            const content = (
              <div
                className="relative flex h-32 w-72 shrink-0 items-end overflow-hidden rounded-xl bg-cover bg-center shadow-sm sm:h-40 sm:w-96"
                style={{ backgroundImage: `url(${b.image_url})` }}
              >
                <div className="w-full bg-gradient-to-t from-black/70 to-transparent p-3">
                  <p className="font-semibold text-white">{b.title}</p>
                </div>
              </div>
            );
            return b.link_url ? (
              <Link key={b.id} href={b.link_url} id={`banner-${b.id}`} data-testid={`banner-${b.id}`}>
                {content}
              </Link>
            ) : (
              <div key={b.id} id={`banner-${b.id}`} data-testid={`banner-${b.id}`}>
                {content}
              </div>
            );
          })}
        </div>
      )}

      {categories.length > 0 && (
        <div className="mb-8">
          <h2 className="mb-3 text-lg font-semibold text-gray-900">Shop by Category</h2>
          <div id="category-showcase" data-testid="category-showcase" className="flex flex-wrap gap-2">
            {categories.map((c) => (
              <button
                key={c.id}
                id={`category-card-${c.id}`}
                data-testid={`category-card-${c.id}`}
                onClick={() => selectCategory(String(c.id))}
                className={`rounded-md border px-4 py-2 text-sm font-medium transition-colors ${
                  categoryId === String(c.id)
                    ? "border-ink bg-ink text-white"
                    : "border-gray-200 bg-white text-gray-700 hover:border-gray-400"
                }`}
              >
                {c.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {offers.length > 0 && (
        <div className="mb-8">
          <h2 className="mb-3 text-lg font-bold text-gray-900">Special Offers</h2>
          <div id="offers-section" data-testid="offers-section" className="flex flex-wrap gap-3">
            {offers.map((o) => (
              <div
                key={o.code}
                data-testid={`offer-${o.code}`}
                className="rounded-lg border border-accent-200 bg-accent-50 px-4 py-3 text-sm"
              >
                <p className="font-mono text-base font-bold text-gray-900">{o.code}</p>
                <p className="text-gray-700">
                  {o.type === "PERCENT" ? `${o.value}% off` : `${money(o.value)} off`}
                  {o.max_discount ? ` (up to ${money(o.max_discount)})` : ""} on orders over {money(o.min_subtotal)}
                  {o.first_order_only ? " — first order only" : ""}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

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
          className="flex-1 min-w-[200px] rounded-lg border border-gray-300 px-3 py-2 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-100"
        />
        <select
          id="catalog-category-select"
          data-testid="catalog-category-select"
          value={categoryId}
          onChange={(e) => {
            setPage(1);
            setCategoryId(e.target.value);
          }}
          className="rounded-lg border border-gray-300 px-3 py-2 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-100"
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
          className="rounded-lg border border-gray-300 px-3 py-2 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-100"
        >
          <option value="">Sort: default</option>
          <option value="price_asc">Price: low to high</option>
          <option value="price_desc">Price: high to low</option>
        </select>
      </div>

      {addMessage && (
        <p id="catalog-add-message" data-testid="catalog-add-message" className="mb-4 text-sm text-emerald-700">
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
            className="relative flex flex-col justify-between rounded-lg border border-gray-200 bg-white p-4"
          >
            {user?.role !== "ADMIN" && user?.role !== "DELIVERY_PARTNER" && (
              <button
                id={`wishlist-toggle-${p.id}`}
                data-testid={`wishlist-toggle-${p.id}`}
                onClick={() => toggleWishlist(p.id)}
                disabled={wishlistBusyId === p.id}
                aria-label="Toggle wishlist"
                className={`absolute right-3 top-3 ${wishlistIds.has(p.id) ? "text-red-500" : "text-gray-300 hover:text-gray-400"}`}
              >
                <HeartIcon className="h-5 w-5" filled={wishlistIds.has(p.id)} />
              </button>
            )}
            <div>
              <Link href={`/product/${p.id}`} id={`product-link-${p.id}`} data-testid={`product-link-${p.id}`}>
                <h2 className="pr-6 font-semibold text-gray-900 hover:underline">{p.name}</h2>
              </Link>
              <p className="text-sm text-gray-500">
                {p.category_name} &middot; {p.unit}
              </p>
              <p className="mt-2 text-lg font-bold text-gray-900">{money(p.price)}</p>
              {p.avg_rating != null && <p className="text-sm text-amber-600">★ {p.avg_rating.toFixed(1)}</p>}
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
              className="mt-3 rounded-md bg-accent-500 px-3 py-2 text-sm font-medium text-gray-900 hover:bg-accent-600 disabled:cursor-not-allowed disabled:bg-gray-200 disabled:text-gray-400"
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
            className="rounded-md border border-gray-300 px-3 py-1 disabled:opacity-50"
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
            className="rounded-md border border-gray-300 px-3 py-1 disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
