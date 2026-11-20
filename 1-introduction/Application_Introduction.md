# 1. Introduction to the application

**FreshCart** is an online grocery shopping and delivery system and is the application under test for this portfolio.
Its source is in [`../0-application/`](../0-application/); the business rules and API reference are in
[`../0-application/docs/REQUIREMENTS.md`](../0-application/docs/REQUIREMENTS.md).

## Roles

| Role | What they do |
|---|---|
| Customer | Browses and searches the catalog, keeps a cart and wishlist, applies coupons, checks out with a delivery slot and COD, UPI or card payment, follows the order live over a WebSocket, and reviews products |
| Admin | Manages products, orders, coupons, users and banners, and reads the audit log |
| Delivery partner | Picks up assigned orders, updates their status and confirms delivery with the customer's OTP |

## Technology

| Layer | Stack |
|---|---|
| Backend | FastAPI (Python), SQLAlchemy, Alembic migrations, JWT authentication, WebSocket for live order status |
| Frontend | Next.js 16 (React, TypeScript) |
| Database | SQLite locally, PostgreSQL under Docker Compose |
| Test support | A test mode with a resettable database and a frozen clock (`APP_ENV=test`, `FIXED_NOW`), described in [`../commands.md`](../commands.md) |

## Why it suits a testing project

- 42 business rules (R1.1-R9.3) with clear boundaries: password and phone formats, pincode range, coupon minimums,
  stock limits, delivery slots.
- A multi-step order lifecycle with states and guarded transitions, which suits state transition testing.
- Combined conditions (coupon type, weekday, cart total, payment mode), which suit decision tables.
- A REST API and a browser UI over the same services, so the same rules can be tested at unit, API and UI level.

## Where to go next

Requirements analysis: [`../2-requirements/`](../2-requirements/). Test plan: [`../3-test-plan/`](../3-test-plan/).
How to run the application: [`../0-application/README.md`](../0-application/README.md).
