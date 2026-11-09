**Defect ID:** DEF-001
**Title:** Cart shows stale (empty) items immediately after the first add-to-cart call
**Reported by:** Developer (self-testing during M3 build)
**Date found:** 2026-11-09
**Found via:** Manual curl verification during M3 (cart) development, before the automated
suite existed
**Module:** M3 — Cart
**Rule ID(s) affected:** R3.3 (re-adding an item), R3.5 (totals reflect current state)
**Severity:** High
**Priority:** P1
**Environment:** `APP_ENV=test`, SQLite, backend commit at the time of M3 development

## Summary

The very first `POST /cart/items` call for a user returned a cart with an **empty** `items`
array (and zero totals), even though the item had been correctly inserted into the database.
A second add for a *different* item then showed only that second item — the first was
invisible until something else forced a full reload.

## Steps to reproduce

1. Log in as a customer with an empty cart.
2. `POST /api/cart/items {"product_id": 1, "quantity": 2}`.
3. Observe the response body.

## Expected result

Response shows `items: [{product_id: 1, quantity: 2, ...}]` with correct subtotal/total.

## Actual result

Response showed `items: []`, `subtotal: "0.00"`, `total: "0.00"` — as if nothing had been added,
despite the row existing in the `cart_items` table (confirmed by a follow-up `GET /cart`
immediately after, which *did* show it correctly).

## Root cause

`app/services/cart_service.py`'s `_get_or_create_cart` loaded the cart via
`select(Cart).options(selectinload(Cart.items)...)`. The `AsyncSessionLocal` sessionmaker
uses `expire_on_commit=False`. After `add_item` committed the new `CartItem` row, it re-ran
the *same* select to build the response — but because the `Cart` ORM object was already in
the session's identity map with its `items` collection already populated (from the pre-commit
load), SQLAlchemy's `selectinload` strategy did not re-fetch it: by default, an already-loaded
relationship collection is left as-is unless the query explicitly asks to repopulate it.

## Fix

Added `.execution_options(populate_existing=True)` to the cart-fetching query in
`_get_or_create_cart`, forcing SQLAlchemy to overwrite the already-loaded `items` collection
(and its nested `product` relationship) with fresh data on every call.

**File changed:** `00_Application/backend/app/services/cart_service.py`

## Status

Fixed and verified (re-tested the exact repro steps above; subsequent adds, updates, removes,
and clears all reflect immediately). See commit `5cbed04` ("feat(catalog,cart): ...").
