# Test Automation

A Selenium + pytest suite (Page Object Model) automating 86 of the 95 test cases in
[`../02_Test_Case_Design/Test_Cases.csv`](../02_Test_Case_Design/Test_Cases.csv), covering
every module M1–M9. The remaining 9 are manual/exploratory (rate limiting, cross-session
timing, a rounding edge case, etc. — see the CSV's `Automated` column and
[`../02_Test_Case_Design/Traceability_Matrix.md`](../02_Test_Case_Design/Traceability_Matrix.md)).

## Structure

```
conftest.py     Session/test fixtures: server health check, the shared Chrome driver,
                an autouse per-test DB reset + browser-state clear, and login_as() (a
                fast, UI-free login helper used as setup for tests that aren't about login)
pages/          Page Object Model, one module per functional area, keyed on the
                frontend's data-testid attributes
tests/          One file per business module (test_m1_auth.py ... test_m9_*.py)
utils/
  config.py     Base URLs, seed account credentials
  api_client.py Thin requests wrapper for fast fixture setup and backend-truth assertions
```

Each test's docstring names its Test Case ID (`TC-Mn-0xx`) and rule ID(s) for traceability
back to `Test_Cases.csv`.

## Running it

```bash
pip install -r requirements.txt
```

Start the application in test mode first (see [`../commands.md`](../commands.md)):

```bash
# terminal 1
cd ../00_Application/backend
APP_ENV=test FIXED_NOW=2026-11-10T09:00:00 uvicorn app.main:app --reload
# terminal 2
cd ../00_Application/frontend
npm run dev
```

Then, from this folder:

```bash
pytest
# or, with an HTML report:
pytest --html=report.html --self-contained-html
```

A real Chrome window opens and drives the app (set `options.add_argument("--headless=new")`
in `conftest.py`'s `driver` fixture to run headless, e.g. in CI). Chrome's driver is
auto-resolved by Selenium Manager (built into Selenium 4.6+) — no manual driver download.

Every test runs against a database freshly reset to the seeded baseline (`conftest.py`'s
`reset_state` fixture calls `POST /api/test/reset` before each test), so tests are
independent of each other and of execution order.

## Design notes

- **API for setup, UI for the thing under test.** Fixtures like "log in as X" or "build a
  cart with Y in it" go through `utils/api_client.py` directly — faster and more reliable
  than re-driving the UI for pure setup. The actual assertions for each test case exercise
  the UI element(s) the rule is about.
- **One shared browser per run**, not one per test — `driver` is a session-scoped fixture.
  Each test still starts from a clean app/browser state via the autouse `reset_state` fixture.
- **No fixed sleeps.** All waits are explicit (`WebDriverWait` on a `data-testid`) except a
  couple of short settle delays after a non-reactive admin table refresh, called out inline.
