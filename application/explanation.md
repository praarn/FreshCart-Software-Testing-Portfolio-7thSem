# FreshCart — application overview

FreshCart is an online grocery shopping and delivery system: the application under test for
this Software Testing portfolio. This file explains how the pieces fit together. For *run
commands*, see [`../commands.md`](../commands.md). For the full business-rule and REST/
WebSocket API reference, see [`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md). For how each
half is built internally, see [`backend/explanation.md`](backend/explanation.md) and
[`frontend/explanation.md`](frontend/explanation.md).

## The two halves

```
backend/     FastAPI + SQLAlchemy 2 (async) + Alembic + JWT auth — REST API + one WebSocket
frontend/    Next.js (App Router) + React 19 + TypeScript + Tailwind — talks to the API only
```

They're independent processes connected over HTTP: the frontend never touches the database
directly, and the backend has no knowledge of how it's rendered. In local dev they run on
`:8000` and `:3000`; under Docker Compose the same two images run alongside a Postgres
container (see the root [`docker-compose.yml`](../docker-compose.yml)).

## Roles and the three experiences

Every user has exactly one role — `CUSTOMER`, `ADMIN`, or `DELIVERY_PARTNER` — set at
registration (customers) or by the seed script (admin/drivers; there's no self-serve
admin/driver signup). The frontend shows a different navigation and page set per role; the
backend enforces the same boundaries independently via JWT role claims, so the UI gating is
a convenience, not the security boundary.

## Module map (business rules)

| Module | What it covers |
|---|---|
| M1 | Registration, login, JWT, account lockout, rate limiting, logout/token denylist |
| M2 | Product catalog: search, filter, sort, pagination |
| M3 | Cart: add/update/remove, quantity caps, recalculated totals |
| M4 | Coupons and pricing math (percent/flat discounts, delivery fee tiering) |
| M5 | Checkout: address, delivery slots, payment validation, atomic order placement |
| M6 | Order lifecycle (state machine), audit log, live WebSocket status updates |
| M7 | Reviews (delivered-order-gated) |
| M8 | Admin: product/order/coupon/user management, dashboard, audit log viewer |
| M9 | Wishlist, promotional banners, public coupon "offers" — added later at the project |
|    | owner's request, inspired by a reference app; not in the original spec |

Every rule has an ID (e.g. `R3.1`) referenced in both the implementing code and
`docs/REQUIREMENTS.md` — grep for the ID to find where a rule lives.

## A request, start to finish (placing an order)

1. **Frontend** (`frontend/app/checkout/page.tsx`): the customer fills address/slot/payment,
   the form calls `api.post("/checkout", {...})` (`frontend/lib/api.ts`), which attaches the
   JWT from `localStorage`.
2. **Backend** (`backend/app/routers/checkout.py`): the route depends on `require_customer`
   and `get_now`, validates the request shape via `schemas/order.py`, and calls
   `services/checkout_service.checkout(...)`.
3. The service re-validates everything that could have changed since the cart was last
   viewed — stock, prices, the applied coupon, slot capacity — inside one flow that only
   commits once every check passes (R5.4/R5.5: nothing partially committed).
4. The response is a full `OrderOut`, including the 4-digit delivery OTP, which the frontend
   then displays on `/orders/:id`.
5. From there, every admin/delivery-partner status change goes through
   `services/order_service.py`'s state machine, which writes an audit-log row and broadcasts
   the new status over `/ws/orders/:id` — the customer's order page updates live without a
   page refresh, via `backend/app/core/ws_manager.py` on the server and a plain
   `new WebSocket(...)` in `frontend/app/orders/[id]/page.tsx` on the client.

## Testability hooks (for the student's test suite)

- `APP_ENV=test` mounts `POST /api/test/reset`, which wipes and reseeds the database. It
  does not exist under any other `APP_ENV` value, so it's never reachable in a normal run.
- `FIXED_NOW=<ISO datetime>` freezes the backend's clock (`backend/app/deps.get_now`), so
  delivery-slot and weekday-coupon (`FRESH15`) rules are deterministic across test runs.
- Every interactive frontend element has a stable `id`/`data-testid` — see
  [`frontend/explanation.md`](frontend/explanation.md#testability).
- Seed data (`backend/app/seed.py`) is idempotent and includes boundary-case products
  (stock 0, stock 1-3) and both a first-order and a non-first-order customer, specifically
  so coupon and stock-limit test cases have fixtures to exercise against without extra setup.
