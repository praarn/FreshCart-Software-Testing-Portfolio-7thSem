# FreshCart — Requirements & API Specification

This document is the authoritative list of business rules (each implemented under its rule ID
in the relevant service/model code), the frontend routes, and the REST/WebSocket API surface.

## Roles

`CUSTOMER`, `ADMIN`, `DELIVERY_PARTNER`.

---

## M1 — Registration and login

| ID | Rule |
|---|---|
| R1.1 | Name: 2-50 chars, letters and spaces only. |
| R1.2 | Email: valid format, unique (case-insensitive), max 100 chars. |
| R1.3 | Password: 8-20 chars, at least 1 letter and 1 digit. Stored hashed with bcrypt. |
| R1.4 | Phone: exactly 10 digits, first digit 6-9. |
| R1.5 | Login (email + password) returns a JWT access token (30 min expiry). 5 consecutive failed logins lock the account for 15 minutes (ACTIVE -> LOCKED -> ACTIVE on expiry or admin unlock). A successful login resets the failure counter. Locked accounts get a clear message. |
| R1.6 | Role checks: customer endpoints need a valid token; `/admin/**` needs ADMIN; `/delivery/**` needs DELIVERY_PARTNER. Missing/invalid/expired token -> 401, wrong role -> 403. |
| R1.7 | Rate limiting: `/auth/login` and `/auth/register` allow at most 10 requests/minute/IP; further requests get 429 + `Retry-After`. |
| R1.8 | Logout: frontend discards the token; backend denylists the token's `jti` so a logged-out token is rejected. |

## M2 — Catalog

| ID | Rule |
|---|---|
| R2.1 | At least 6 categories (Fruits, Vegetables, Dairy, Bakery, Beverages, Snacks) and 30+ seeded products. |
| R2.2 | Product: name (2-80), price 0.01-10000.00, stock 0-1000, unit (kg/g/l/ml/pc/pack), category, active flag. |
| R2.3 | Search by name (case-insensitive, partial), filter by category, sort by price asc/desc, pagination 10/page. |
| R2.4 | Out-of-stock products are shown but cannot be added to cart. Inactive products are hidden from customers. |

## M3 — Cart

| ID | Rule |
|---|---|
| R3.1 | Quantity per item 1-10 and not above available stock. |
| R3.2 | Max 20 distinct items in a cart. |
| R3.3 | Adding an existing item increases its quantity (still capped by R3.1; exceeding the cap/stock is rejected, not silently clamped). |
| R3.4 | Update quantity, remove item, clear cart. Cart persists per user in the database. |
| R3.5 | Cart shows subtotal, discount, delivery fee and total, recalculated on every change. |

## M4 — Coupons and pricing

| ID | Rule |
|---|---|
| R4.1 | Seeded coupons: `WELCOME10` (10% off, min 200, first order only, capped at 100), `FLAT50` (flat 50 off, min 500), `FRESH15` (15% off, min 800, capped at 150, Mon-Fri only), `OLD20` (expired, always rejected). |
| R4.2 | Only one coupon per order (applying a new one replaces the previous). Codes are case-insensitive. Unknown, expired, below-minimum, first-order-violated and wrong-day cases each return a distinct error message. |
| R4.3 | Delivery fee: post-discount subtotal below 299.00 -> 40.00; 299.00 or more -> free. |
| R4.4 | All money uses `Decimal`, 2 decimal places, `ROUND_HALF_UP`. |

## M5 — Checkout

| ID | Rule |
|---|---|
| R5.1 | Address: line1 (5-100), city (2-50), pincode exactly 6 digits. Serviceable pincodes 560001-560100; others rejected with "Delivery not available". |
| R5.2 | Delivery slot: 2-hour slots from 08:00 to 20:00. Slot must start at least 2 hours from now and within the next 3 days. Each slot accepts at most 5 orders; a full slot is rejected. |
| R5.3 | Payment: COD (only if total <= 5000), UPI (`name@bank` format, mock verified), CARD (16 digits passing Luhn, future MM/YY expiry, 3-digit CVV; card `4000000000000002` is always declined). |
| R5.4 | Placing an order requires a non-empty cart, re-validates stock/prices at that moment, decrements stock in one transaction, clears the cart, generates an order number `FC-YYYYMMDD-NNNN` and a 4-digit delivery OTP. |
| R5.5 | If any line is no longer available at that moment, checkout fails naming the item and nothing is partially committed. |

## M6 — Orders and lifecycle

| ID | Rule |
|---|---|
| R6.1 | States: `PLACED -> CONFIRMED -> PACKED -> OUT_FOR_DELIVERY -> DELIVERED`, plus `CANCELLED`. Illegal transitions return 409. No backward moves. `DELIVERED`/`CANCELLED` are terminal. |
| R6.2 | Customer can cancel only in `PLACED` or `CONFIRMED`. Cancelling restores stock and records `cancelled_at`. |
| R6.3 | Admin moves `PLACED -> CONFIRMED -> PACKED` and must assign a delivery partner (only once `PACKED`) before `OUT_FOR_DELIVERY`. |
| R6.4 | Delivery partner sees only assigned orders, marks `OUT_FOR_DELIVERY`, then marks `DELIVERED` by entering the customer's 4-digit OTP. 3 wrong OTPs block further attempts until an admin resets them. |
| R6.5 | Every status change is written to an audit log (order_id, from_state, to_state, actor_id, actor_role, timestamp); the customer sees it as a status timeline. |
| R6.6 | Customers see only their own orders (another user's order -> 403). |
| R6.7 | WebSocket `/ws/orders/{order_id}` (token-authenticated) pushes status changes live. |

## M7 — Reviews

| ID | Rule |
|---|---|
| R7.1 | A customer can review a product only after a `DELIVERED` order containing it. Rating 1-5 integer, comment up to 300 chars, one review per product per customer. Average rating shown on the product. |

## M8 — Admin

| ID | Rule |
|---|---|
| R8.1 | Product CRUD (R2.2 validation), stock update, activate/deactivate. |
| R8.2 | Order list filterable by status and date, status updates, delivery-partner assignment, OTP-attempt reset. |
| R8.3 | Coupon list with enable/disable. User list with lock/unlock. |
| R8.4 | Dashboard: orders today, revenue today, low-stock products (stock < 10). |
| R8.5 | Audit log viewer (read-only, filterable by order and actor). |

---

## Frontend routes

| Route | Access | Purpose |
|---|---|---|
| `/register` | Public | Create a customer account |
| `/login` | Public | Log in |
| `/` | Public | Catalog: search/filter/sort/pagination |
| `/product/[id]` | Public (review form for CUSTOMER) | Product detail + reviews |
| `/cart` | CUSTOMER | Cart, coupon apply/remove |
| `/checkout` | CUSTOMER | Address/slot/payment, place order |
| `/orders` | CUSTOMER | Order history |
| `/orders/[id]` | CUSTOMER | Order detail, live status timeline, cancel |
| `/admin` | ADMIN | Dashboard |
| `/admin/products` | ADMIN | Product CRUD/stock/active |
| `/admin/orders` | ADMIN | Order list/status/assignment/OTP reset |
| `/admin/coupons` | ADMIN | Coupon enable/disable |
| `/admin/users` | ADMIN | User lock/unlock |
| `/admin/audit-log` | ADMIN | Audit log viewer |
| `/delivery` | DELIVERY_PARTNER | Assigned orders, dispatch, OTP delivery |

---

## REST API

Base path: `/api`. All error responses use `{status, error, message, field_errors: [{field, message}]}`.
Full interactive docs with request/response examples: **Swagger UI at `/docs`**.

### Health

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/health` | none | 200 `{"status":"ok"}` |

### Auth (M1)

| Method | Path | Auth | Request | Responses |
|---|---|---|---|---|
| POST | `/auth/register` | none (rate-limited) | `{name, email, password, phone}` | 201 user, 409 duplicate email, 422 validation, 429 rate-limited |
| POST | `/auth/login` | none (rate-limited) | `{email, password}` | 200 `{access_token, token_type, expires_in}`, 401 invalid/locked, 429 rate-limited |
| POST | `/auth/logout` | Bearer | - | 200 message, 401 |
| GET | `/auth/me` | Bearer | - | 200 user, 401 |

### Catalog (M2)

| Method | Path | Auth | Request | Responses |
|---|---|---|---|---|
| GET | `/catalog/categories` | none | - | 200 list |
| GET | `/catalog/products` | none | query: `search, category_id, sort, page` | 200 paginated list |
| GET | `/catalog/products/{id}` | none | - | 200 product, 404 |

### Cart (M3, M4)

| Method | Path | Auth | Request | Responses |
|---|---|---|---|---|
| GET | `/cart` | CUSTOMER | - | 200 cart |
| POST | `/cart/items` | CUSTOMER | `{product_id, quantity}` | 200 cart, 400 stock/cap, 404 product |
| PUT | `/cart/items/{item_id}` | CUSTOMER | `{quantity}` | 200 cart, 400, 404 |
| DELETE | `/cart/items/{item_id}` | CUSTOMER | - | 200 cart, 404 |
| DELETE | `/cart` | CUSTOMER | - | 200 cart (cleared) |
| POST | `/cart/coupon` | CUSTOMER | `{code}` | 200 cart, 400 invalid/ineligible coupon |
| DELETE | `/cart/coupon` | CUSTOMER | - | 200 cart |

### Checkout (M5)

| Method | Path | Auth | Request | Responses |
|---|---|---|---|---|
| GET | `/checkout/slots` | CUSTOMER | - | 200 list of slots with remaining capacity |
| POST | `/checkout` | CUSTOMER | `{address, slot_start, payment}` | 201 order, 400 address/slot/payment/empty-cart, 409 stock conflict |

### Orders (M6)

| Method | Path | Auth | Request | Responses |
|---|---|---|---|---|
| GET | `/orders` | CUSTOMER | - | 200 list (own orders) |
| GET | `/orders/{id}` | CUSTOMER | - | 200 order + timeline, 403 not yours, 404 |
| POST | `/orders/{id}/cancel` | CUSTOMER | - | 200 order, 403, 409 wrong state |

### Reviews (M7)

| Method | Path | Auth | Request | Responses |
|---|---|---|---|---|
| POST | `/reviews` | CUSTOMER | `{product_id, rating, comment}` | 201 review, 400 not delivered, 409 duplicate |
| GET | `/reviews?product_id=` | none | - | 200 list |

### Delivery partner (M6)

| Method | Path | Auth | Request | Responses |
|---|---|---|---|---|
| GET | `/delivery/orders` | DELIVERY_PARTNER | - | 200 list (assigned only, OTP hidden) |
| POST | `/delivery/orders/{id}/dispatch` | DELIVERY_PARTNER | - | 200 order, 403 not assigned, 409 wrong state |
| POST | `/delivery/orders/{id}/deliver` | DELIVERY_PARTNER | `{otp}` | 200 order (DELIVERED), 400 wrong OTP, 409 blocked/wrong state |

### Admin (M6, M8)

| Method | Path | Auth | Request | Responses |
|---|---|---|---|---|
| GET | `/admin/orders` | ADMIN | query: `status, date` | 200 list |
| PATCH | `/admin/orders/{id}/status` | ADMIN | `{to_status}` | 200 order, 409 illegal transition |
| POST | `/admin/orders/{id}/assign-partner` | ADMIN | `{delivery_partner_id}` | 200 order, 400 not a partner, 409 not PACKED |
| POST | `/admin/orders/{id}/reset-otp` | ADMIN | - | 200 order |
| POST | `/admin/orders/{id}/cancel` | ADMIN | - | 200 order, 409 wrong state |
| GET | `/admin/products` | ADMIN | query: `search, category_id, page` | 200 list (incl. inactive) |
| POST | `/admin/products` | ADMIN | product fields | 201 product, 422 validation |
| PUT | `/admin/products/{id}` | ADMIN | partial product fields | 200 product, 404 |
| PATCH | `/admin/products/{id}/stock` | ADMIN | `{stock}` | 200 product |
| PATCH | `/admin/products/{id}/active` | ADMIN | `{active}` | 200 product |
| GET | `/admin/coupons` | ADMIN | - | 200 list |
| PATCH | `/admin/coupons/{id}` | ADMIN | `{active}` | 200 coupon |
| GET | `/admin/users` | ADMIN | - | 200 list |
| POST | `/admin/users/{id}/lock` | ADMIN | - | 200 user |
| POST | `/admin/users/{id}/unlock` | ADMIN | - | 200 user |
| GET | `/admin/dashboard` | ADMIN | - | 200 metrics |
| GET | `/admin/audit-log` | ADMIN | query: `order_id, actor_id` | 200 list |

All admin endpoints require role `ADMIN`; non-admins get 403. All `/delivery/**` endpoints require role `DELIVERY_PARTNER`.

### Testability (test mode only)

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/test/reset` | none | Only registered when `APP_ENV=test`. Wipes and reseeds the database. |

### WebSocket

| Path | Auth | Notes |
|---|---|---|
| `/ws/orders/{order_id}?token=<jwt>` | token query param | Pushes `{order_id, status, timestamp}` on every status change. Only the order's owner, its assigned delivery partner, or an admin may connect. |
