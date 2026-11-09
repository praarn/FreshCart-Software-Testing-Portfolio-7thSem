# FreshCart

Online grocery shopping and delivery system — the application under test for this
Software Testing portfolio. Full business-rule and API reference:
[`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md).

## Prerequisites

- Python 3.11+ (tested on 3.12)
- Node.js 20+
- SQLite needs no setup; PostgreSQL is only needed if you run via Docker Compose

## Run locally (SQLite, zero external services)

```bash
# Backend — from 00_Application/backend
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

```bash
# Frontend — from 00_Application/frontend, in a second terminal
npm install
npm run dev
```

- Backend: http://localhost:8000 — **Swagger UI at http://localhost:8000/docs**
- Frontend: http://localhost:3000
- The SQLite database file is created at `00_Application/backend/data/freshcart.db`.

The frontend reads the API base URL from `NEXT_PUBLIC_API_URL` / `NEXT_PUBLIC_WS_URL`
(see `frontend/.env.example`; defaults already point at `localhost:8000`).

## Run with Docker Compose (PostgreSQL + backend + frontend)

```bash
docker compose up --build
```

This starts PostgreSQL, runs migrations and seeds the database, and serves the backend on
`:8000` and frontend on `:3000`. Switch databases purely via the `DATABASE_URL` env var — the
same code runs on SQLite and PostgreSQL unchanged.

## Seed credentials

Loaded idempotently by `python -m app.seed` (or automatically in the Docker image):

| Role | Email | Password | Notes |
|---|---|---|---|
| ADMIN | admin@freshcart.test | Admin@1234 | |
| DELIVERY_PARTNER | driver1@freshcart.test | Driver@1234 | |
| DELIVERY_PARTNER | driver2@freshcart.test | Driver@1234 | |
| CUSTOMER | customer1@freshcart.test | Customer@1234 | Has one past DELIVERED order (not eligible for first-order coupons) |
| CUSTOMER | customer2@freshcart.test | Customer@1234 | No orders yet (eligible for `WELCOME10`) |

Seeded coupons: `WELCOME10`, `FLAT50`, `FRESH15`, `OLD20` (expired) — see
[`docs/REQUIREMENTS.md`](docs/REQUIREMENTS.md#m4--coupons-and-pricing) for exact rules.

## Test mode (for automated/repeatable test runs)

Set `APP_ENV=test` to mount `POST /api/test/reset`, which wipes and reseeds the database.
This route does not exist when `APP_ENV` is anything else.

Set `FIXED_NOW=2026-11-10T09:00:00` (any ISO datetime) to freeze the application clock, so
delivery-slot and weekday-coupon (`FRESH15`) rules are deterministic for testing.

```bash
APP_ENV=test FIXED_NOW=2026-11-10T09:00:00 uvicorn app.main:app --reload
```

A trivial smoke test (`GET /health` returns 200) lives at `backend/tests/test_health.py` and
runs in CI — the real test suite is the student's deliverable under `05_Test_Automation/`.

## Where things are

- Backend: `00_Application/backend` (FastAPI, SQLAlchemy 2 async, Alembic, JWT auth)
- Frontend: `00_Application/frontend` (Next.js App Router, React 19, TypeScript, Tailwind)
- Requirements/API reference: `00_Application/docs/REQUIREMENTS.md`
- Docker: `00_Application/backend/Dockerfile`, `00_Application/frontend/Dockerfile`,
  root `docker-compose.yml`
- CI: `.github/workflows/ci.yml`
