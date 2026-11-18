# Backend — how it's put together

FastAPI + SQLAlchemy 2 (async) + Alembic + JWT auth. This file explains the folder structure
and the patterns used throughout, so you can find your way around without reading every file.
For *what* each endpoint does, see [`../docs/REQUIREMENTS.md`](../docs/REQUIREMENTS.md) and
Swagger UI at `/docs`. For *how to run it*, see [`../../commands.md`](../../commands.md).

## Folder structure

```
app/
  main.py          FastAPI app creation, CORS, error handlers, router registration
  config.py        Settings (env vars), loaded once via get_settings()
  database.py      Async engine/session, declarative Base, get_db() dependency
  deps.py          Shared dependencies: get_now(), get_current_user(), require_role()
  models/          SQLAlchemy ORM models — one file per entity group
  schemas/         Pydantic v2 request/response models — one file per module
  services/        Business logic — one file per module, imported by routers
  routers/         FastAPI route handlers — thin, delegate to services
  core/
    security.py    Password hashing (bcrypt) and JWT encode/decode
    errors.py      AppError hierarchy + the {status, error, message, field_errors} shape
    rate_limit.py  In-memory fixed-window limiter for /auth/register and /auth/login
    ws_manager.py  In-memory pub/sub used by the order-status WebSocket
  seed.py          Idempotent seed script (python -m app.seed)
alembic/           Migrations; env.py runs them against the async engine
tests/
  test_health.py   The one trivial smoke test CI runs (the real suite is the
                    student's deliverable under Test_Automation/)
```

## The layering rule

**Routers stay thin.** A route handler decodes the request (via its Pydantic schema),
calls one or two service functions, and returns the result. All validation beyond basic
shape, all business rules, and all database queries live in `services/`. This means the
same business logic (say, cart pricing) is exercised identically whether it's called from
`POST /cart/items` or from inside checkout — there's exactly one place each rule lives.

Models (`models/`) are plain SQLAlchemy ORM classes with no behavior beyond relationships.
Schemas (`schemas/`) are plain Pydantic models with field-shape validation only (length,
range, regex) — anything that needs a database lookup (uniqueness, "does this coupon still
apply") is a service-level check, not a schema validator.

## Request flow, end to end (example: adding a cart item)

1. `routers/cart.py` — `POST /cart/items` depends on `require_customer` (role check) and
   `get_now` (the clock), parses the body as `schemas.cart.AddToCartRequest`.
2. It calls `services/cart_service.add_item(db, user, product_id, quantity, now)`.
3. The service loads the product, checks stock/active (R2.4), checks the 1-10/cap-by-stock
   rule (R3.1) and the 20-distinct-item limit (R3.2), mutates the `CartItem` row, commits,
   and returns a freshly computed cart view (`services/pricing_service.py` for the money math).
4. If anything is wrong, the service raises an `AppError` subclass from `core/errors.py`
   (e.g. `BadRequestError`, `ConflictError`) with a human-readable message; a registered
   FastAPI exception handler turns that into the standard JSON error shape.
5. On success, FastAPI serializes the returned dict against `schemas.cart.CartOut`.

## Cross-cutting pieces worth knowing about

- **The injectable clock** (`deps.get_now`) is used everywhere a business rule depends on
  "now" — login lockout expiry, delivery slot math, the `FRESH15` weekday check, order
  timestamps. In production it's `datetime.utcnow()`; in test mode, setting `FIXED_NOW`
  freezes it, which is what makes slot/weekday tests deterministic.
- **Role enforcement** (`deps.require_role`, and the convenience `require_customer` /
  `require_admin` / `require_delivery_partner`) wraps `get_current_user`, which decodes the
  JWT, checks it against `TokenDenylist` (logout support), and auto-unlocks accounts whose
  15-minute lock has expired.
- **Rate limiting** (`core/rate_limit.py`) is a deliberately tiny in-memory sliding-window
  limiter — not a new dependency — applied only to `/auth/register` and `/auth/login`.
- **The WebSocket** (`routers/ws.py` + `core/ws_manager.py`) authenticates via a `token`
  query param (same JWT as REST), checks the connecting user is the order's owner, its
  assigned delivery partner, or an admin, then just relays whatever
  `order_service._transition()` broadcasts on every status change.
- **Testability hooks**: `APP_ENV=test` mounts `POST /api/test/reset` (wipes + reseeds);
  it's never registered otherwise, so there's no way to hit it in a normal deployment.

## Database: SQLite and PostgreSQL from the same code

Nothing in the code branches on database type. `DATABASE_URL` picks the driver
(`sqlite+aiosqlite:///...` locally, `postgresql+asyncpg://...` under Docker Compose); the
Alembic migrations in `alembic/versions/` run against either unchanged. See
[`../../docker-compose.yml`](../../docker-compose.yml) for how the Compose setup wires
Postgres in.

## Adding a new rule or endpoint

1. If it needs new persisted state, add/extend a model in `models/`, then
   `alembic revision --autogenerate -m "..."` and `alembic upgrade head`.
2. Add or extend the Pydantic schema in `schemas/`.
3. Put the actual logic in `services/` — that's where you'll find (and should add) the
   business-rule comments referencing rule IDs like `# R3.1`.
4. Add a thin route in `routers/`, wire it into `main.py` if it's a new router file.
5. Update [`../docs/REQUIREMENTS.md`](../docs/REQUIREMENTS.md) with the rule ID and the
   endpoint row.
