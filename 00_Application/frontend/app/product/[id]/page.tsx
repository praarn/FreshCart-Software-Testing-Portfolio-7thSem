"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { useParams, useRouter } from "next/navigation";
import { api, errorMessage } from "@/lib/api";
import { money, formatDateTime } from "@/lib/format";
import { useAuth } from "@/lib/auth";
import type { Product, Review, WishlistItem } from "@/lib/types";

export default function ProductDetailPage() {
  const params = useParams<{ id: string }>();
  const productId = params.id;
  const { user } = useAuth();
  const router = useRouter();

  const [product, setProduct] = useState<Product | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [addMessage, setAddMessage] = useState<string | null>(null);
  const [adding, setAdding] = useState(false);
  const [inWishlist, setInWishlist] = useState(false);
  const [wishlistBusy, setWishlistBusy] = useState(false);

  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [reviewError, setReviewError] = useState<string | null>(null);
  const [reviewSubmitting, setReviewSubmitting] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [p, r] = await Promise.all([
        api.get<Product>(`/catalog/products/${productId}`),
        api.get<Review[]>(`/reviews?product_id=${productId}`),
      ]);
      setProduct(p);
      setReviews(r);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [productId]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (user?.role !== "CUSTOMER") {
      setInWishlist(false);
      return;
    }
    api
      .get<WishlistItem[]>("/wishlist")
      .then((items) => setInWishlist(items.some((i) => i.product.id === Number(productId))))
      .catch(() => {});
  }, [user, productId]);

  async function toggleWishlist() {
    if (!user) {
      router.push("/login");
      return;
    }
    setWishlistBusy(true);
    try {
      if (inWishlist) {
        await api.delete(`/wishlist/items/${productId}`);
        setInWishlist(false);
      } else {
        await api.post("/wishlist/items", { product_id: Number(productId) });
        setInWishlist(true);
      }
    } catch {
      // best-effort toggle; ignore transient errors
    } finally {
      setWishlistBusy(false);
    }
  }

  async function handleAddToCart() {
    if (!user) {
      router.push("/login");
      return;
    }
    setAdding(true);
    setAddMessage(null);
    try {
      await api.post("/cart/items", { product_id: Number(productId), quantity: 1 });
      setAddMessage("Added to cart.");
    } catch (err) {
      setAddMessage(errorMessage(err));
    } finally {
      setAdding(false);
    }
  }

  async function handleReviewSubmit(e: FormEvent) {
    e.preventDefault();
    setReviewError(null);
    setReviewSubmitting(true);
    try {
      await api.post("/reviews", { product_id: Number(productId), rating, comment: comment || null });
      setComment("");
      setRating(5);
      await load();
    } catch (err) {
      setReviewError(errorMessage(err));
    } finally {
      setReviewSubmitting(false);
    }
  }

  if (loading) {
    return (
      <p id="product-detail-loading" data-testid="product-detail-loading" className="p-8 text-center text-gray-500">
        Loading...
      </p>
    );
  }
  if (error || !product) {
    return (
      <p id="product-detail-error" data-testid="product-detail-error" className="p-8 text-center text-red-600">
        {error ?? "Product not found."}
      </p>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <div id="product-detail" data-testid="product-detail" className="relative rounded-xl border border-gray-100 bg-white p-6 shadow-sm">
        {user?.role !== "ADMIN" && user?.role !== "DELIVERY_PARTNER" && (
          <button
            id="product-detail-wishlist-toggle"
            data-testid="product-detail-wishlist-toggle"
            onClick={toggleWishlist}
            disabled={wishlistBusy}
            aria-label="Toggle wishlist"
            className="absolute right-6 top-6 text-xl"
          >
            {inWishlist ? "❤️" : "🤍"}
          </button>
        )}
        <h1 className="pr-8 text-2xl font-bold text-gray-900">{product.name}</h1>
        <p className="mt-1 text-sm text-gray-500">
          {product.category_name} &middot; {product.unit}
        </p>
        {product.description && <p className="mt-3 text-gray-700">{product.description}</p>}
        <p className="mt-4 text-2xl font-bold text-gray-900">{money(product.price)}</p>
        {product.avg_rating != null && (
          <p id="product-avg-rating" data-testid="product-avg-rating" className="mt-1 text-yellow-600">
            ★ {product.avg_rating.toFixed(1)} average rating
          </p>
        )}
        {product.stock === 0 ? (
          <p data-testid="product-detail-out-of-stock" className="mt-2 font-medium text-red-600">
            Out of stock
          </p>
        ) : (
          <p className="mt-2 text-gray-500">{product.stock} in stock</p>
        )}

        {addMessage && (
          <p id="product-detail-add-message" data-testid="product-detail-add-message" className="mt-2 text-sm text-emerald-700">
            {addMessage}
          </p>
        )}

        <button
          id="product-detail-add-to-cart"
          data-testid="product-detail-add-to-cart"
          disabled={product.stock === 0 || adding}
          onClick={handleAddToCart}
          className="mt-4 rounded-full bg-accent-500 px-4 py-2 font-medium text-gray-900 hover:bg-accent-600 disabled:cursor-not-allowed disabled:bg-gray-300"
        >
          {product.stock === 0 ? "Out of stock" : adding ? "Adding..." : "Add to cart"}
        </button>
      </div>

      <div className="mt-8">
        <h2 className="mb-3 text-xl font-semibold text-gray-900">Reviews</h2>

        {user?.role === "CUSTOMER" && (
          <form id="review-form" data-testid="review-form" onSubmit={handleReviewSubmit} className="mb-6 rounded-xl border border-gray-100 bg-white p-4 shadow-sm">
            <label htmlFor="review-rating" className="mb-1 block text-sm font-medium text-gray-700">
              Rating
            </label>
            <select
              id="review-rating"
              data-testid="review-rating-select"
              value={rating}
              onChange={(e) => setRating(Number(e.target.value))}
              className="mb-3 rounded-lg border border-gray-300 px-3 py-2 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-100"
            >
              {[5, 4, 3, 2, 1].map((n) => (
                <option key={n} value={n}>
                  {n} star{n > 1 ? "s" : ""}
                </option>
              ))}
            </select>
            <label htmlFor="review-comment" className="mb-1 block text-sm font-medium text-gray-700">
              Comment (optional)
            </label>
            <textarea
              id="review-comment"
              data-testid="review-comment-input"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              maxLength={300}
              className="mb-3 w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-accent-500 focus:outline-none focus:ring-2 focus:ring-accent-100"
            />
            {reviewError && (
              <p id="review-form-error" data-testid="review-form-error" className="mb-3 text-sm text-red-600">
                {reviewError}
              </p>
            )}
            <button
              id="review-submit-button"
              data-testid="review-submit-button"
              type="submit"
              disabled={reviewSubmitting}
              className="rounded-full bg-accent-500 px-4 py-2 text-sm font-medium text-gray-900 hover:bg-accent-600 disabled:opacity-50"
            >
              {reviewSubmitting ? "Submitting..." : "Submit review"}
            </button>
          </form>
        )}

        {reviews.length === 0 ? (
          <p id="product-reviews-empty" data-testid="product-reviews-empty" className="text-gray-500">
            No reviews yet.
          </p>
        ) : (
          <ul id="product-reviews-list" data-testid="product-reviews-list" className="space-y-3">
            {reviews.map((r) => (
              <li key={r.id} data-testid={`review-row-${r.id}`} className="rounded-xl border border-gray-100 bg-white p-3 shadow-sm">
                <p className="font-medium text-gray-900">
                  {r.user_name} &middot; ★ {r.rating}
                </p>
                {r.comment && <p className="text-gray-700">{r.comment}</p>}
                <p className="text-xs text-gray-400">{formatDateTime(r.created_at)}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
