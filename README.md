# Software Testing Portfolio — FreshCart

A university Software Testing portfolio. The application under test is **FreshCart**, an
online grocery shopping and delivery system (FastAPI backend, Next.js frontend). Around it
sits a full set of testing deliverables: test plan, test case design with a traceability
matrix, a Selenium + pytest automation suite, execution logs, defect reports, a summary
report, and screenshots.

## At a glance

| | |
|---|---|
| Application | FreshCart — FastAPI + Next.js, SQLite locally / PostgreSQL via Docker |
| Business rules | 42 (R1.1–R9.3) across 9 modules, all covered by test cases |
| Test cases designed | 95 (86 automated, 9 manual/exploratory) |
| Automated cases executed | 86 / 86 — 80 passed, 6 failed (Selenium/chromedriver timeouts) |
| Open application defects | 0 (2 found and fixed during development) |
| Automation stack | Selenium + pytest, Page Object Model, `data-testid` locators |
| CI | GitHub Actions: install, migrate, seed, API smoke test, frontend build |

The 6 failures were re-run with Playwright (5 clean runs each, no console errors), which
points to the Selenium setup on the test machine rather than the app. Details are in the
[Test Summary Report](06_Test_Reports/Test_Summary_Report.md).

## Repository layout

| Folder / file | Contents |
|---|---|
| [`00_Application/`](00_Application/) | FreshCart: `backend/` (FastAPI), `frontend/` (Next.js), `docs/REQUIREMENTS.md` (every business rule, route and endpoint) |
| [`01_Test_Plan/`](01_Test_Plan/) | Scope, strategy, schedule, resources, exit criteria |
| [`02_Test_Case_Design/`](02_Test_Case_Design/) | `Test_Cases.csv` (95 cases) and the rule-to-case `Traceability_Matrix.md` |
| [`03_Test_Execution/`](03_Test_Execution/) | `Execution_Log.md`: run-by-run results and the Playwright cross-checks |
| [`04_Defect_Reports/`](04_Defect_Reports/) | DEF-001, DEF-002 and a reusable defect report template |
| [`05_Test_Automation/`](05_Test_Automation/) | Selenium + pytest suite: `pages/`, `tests/`, `utils/`, `conftest.py` |
| [`06_Test_Reports/`](06_Test_Reports/) | `Test_Summary_Report.md` with metrics and results by module |
| [`07_Screenshots/`](07_Screenshots/) | Evidence screenshots from development and verification |
| `.github/workflows/` | CI pipeline |
| `docker-compose.yml` | PostgreSQL + backend + frontend in one command |

## Quick start

Local, with SQLite and no external services (two terminals):

```bash
# Terminal 1: backend
cd 00_Application/backend
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload      # http://localhost:8000  (Swagger UI at /docs)

# Terminal 2: frontend
cd 00_Application/frontend
npm install
npm run dev                        # http://localhost:3000
```

Or with Docker (PostgreSQL included):

```bash
docker compose up --build
```

Prerequisites: Python 3.11+ (3.12 recommended), Node.js 20+, Docker Desktop only for the
Docker path. Per-OS commands, including Windows PowerShell, are in [`commands.md`](commands.md).

## Running the tests

Start the app in test mode so the database can be reset and the clock is fixed:

```bash
cd 00_Application/backend
APP_ENV=test FIXED_NOW=2026-11-10T09:00:00 uvicorn app.main:app --reload
```

Then, with the frontend running, in another terminal:

```bash
cd 05_Test_Automation
pip install -r requirements.txt
pytest
```

See [`05_Test_Automation/README.md`](05_Test_Automation/README.md) for the full setup and
options.

## Seed accounts

| Role | Email | Password |
|---|---|---|
| Admin | admin@freshcart.test | Admin@1234 |
| Delivery partner | driver1@freshcart.test | Driver@1234 |
| Customer | customer1@freshcart.test | Customer@1234 |
| Customer (no orders, eligible for `WELCOME10`) | customer2@freshcart.test | Customer@1234 |

More accounts, seeded coupons and test-mode variables are in
[`00_Application/README.md`](00_Application/README.md).

## Where to read next

- [`explanation.md`](explanation.md): a map of the repo and why FreshCart looks the way it does
- [`commands.md`](commands.md): copy-pasteable run commands for macOS, Linux and Windows
- [`00_Application/docs/REQUIREMENTS.md`](00_Application/docs/REQUIREMENTS.md): the authoritative spec to write test cases against
- [`06_Test_Reports/Test_Summary_Report.md`](06_Test_Reports/Test_Summary_Report.md): results and metrics
