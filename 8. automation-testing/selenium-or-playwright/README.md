# 05 — Test Automation

A Selenium + pytest suite (Page Object Model) automating 86 of the 169 test cases in
[`../../4. test-cases/Test_Cases.csv`](../../4.%20test-cases/Test_Cases.csv), covering
every module M1–M9. The other 83 are covered at the API level (`A`, Newman), by the black-box EP/BVA suite (`B`, `black-box-testing`) or at unit level (`U`, pytest); see the CSV's
`Automated` column and
[`../../4. test-cases/Traceability_Matrix.md`](../../4.%20test-cases/Traceability_Matrix.md).

## At a glance

| | |
|---|---|
| Stack | Selenium 4.27, pytest 8.3, requests, pytest-html |
| Pattern | Page Object Model; locators use the frontend's `data-testid` attributes |
| Tests | 86 automated cases across 9 files, one per business module |
| Latest result | 86 passed, 0 failed (34 min 16 s, production build) - [`selenium_report.html`](../../10.%20test-execution/selenium_report.html) |

| Test file | Module | Tests |
|---|---|---|
| `tests/test_m1_auth.py` | Registration and login | 17 |
| `tests/test_m2_catalog.py` | Catalog | 7 |
| `tests/test_m3_cart.py` | Cart | 8 |
| `tests/test_m4_coupons.py` | Coupons and pricing | 10 |
| `tests/test_m5_checkout.py` | Checkout | 13 |
| `tests/test_m6_order_lifecycle.py` | Order lifecycle | 12 |
| `tests/test_m7_reviews.py` | Reviews | 3 |
| `tests/test_m8_admin.py` | Admin | 10 |
| `tests/test_m9_wishlist_banners_offers.py` | Wishlist, banners, offers | 6 |

Page objects in `pages/`: `base_page`, `auth_pages`, `catalog_pages`, `cart_checkout_pages`,
`orders_pages`, `admin_pages`, `delivery_page`, `wishlist_page`.

## Structure

```
conftest.py     Session/test fixtures: server health check, a function-scoped headless Chrome driver,
                an autouse per-test DB reset + browser-state clear, and login_as() (a
                fast, UI-free login helper used as setup for tests that aren't about login)
pages/          Page Object Model, one module per functional area, keyed on the
                frontend's data-testid attributes
tests/          One file per business module (test_m1_auth.py ... test_m9_*.py)
diagnostics/    Scripts that reproduce and measure the failures described in the Execution Log
"14. tools/"          make_results_table.py: JUnit XML -> "../../10. test-execution/Selenium_Results.md"
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

Start the application in test mode first (see [`../../commands.md`](../../commands.md)):

```bash
# terminal 1
cd "../../0. application/backend"
APP_ENV=test FIXED_NOW=2026-11-10T09:00:00 uvicorn app.main:app --reload
# terminal 2
cd "../../0. application/frontend"
npm run dev
```

Then, from this folder:

```bash
pytest
# or, with an HTML report:
pytest --html=report.html --self-contained-html   # report.html is git-ignored here; the committed copy is "10. test-execution/selenium_report.html"
```

Chrome runs headless (`--headless=new`, set in `conftest.py`'s `driver` fixture); remove that
option to watch it. Chrome's driver is auto-resolved by Selenium Manager (built into
Selenium 4.6+), so no manual driver download is needed.

**Use a production build of the frontend** (`npm run build && npm start`). Against `npm run dev`
each route is compiled on first use and pages take 12-15 s to become ready under load, which
sits close to the 20 s wait and produced intermittent timeouts (see the Execution Log).

Every test runs against a database freshly reset to the seeded baseline (`conftest.py`'s
`reset_state` fixture calls `POST /api/test/reset` before each test), so tests are
independent of each other and of execution order.

## Design notes

- **API for setup, UI for the thing under test.** Fixtures like "log in as X" or "build a
  cart with Y in it" go through `utils/api_client.py` directly — faster and more reliable
  than re-driving the UI for pure setup. The actual assertions for each test case exercise
  the UI element(s) the rule is about.
- **One fresh browser per test** — `driver` is function-scoped. A single long-lived session
  became unstable partway through a full run and cascaded failures into later tests. Each test
  also starts from a clean app/browser state via the autouse `reset_state` fixture.
- **No fixed sleeps.** All waits are explicit (`WebDriverWait` on a `data-testid`) except a
  couple of short settle delays after a non-reactive admin table refresh, called out inline.

## Running a subset

```bash
pytest tests/test_m4_coupons.py            # one module
pytest -k "TC_M4_007 or wishlist"          # by name
pytest -x                                  # stop at the first failure
```

## Flakiness and its causes

The suite had intermittent timeouts. Investigation found real causes, listed in the
[Execution Log](../../10.%20test-execution/Execution_Log.md): DEF-003 (test-mode token expiry), DEF-007 (stale search
response), DEF-008 (session cleared when `/auth/me` is aborted) and, for the wishlist, DEF-006. Scripts that reproduce
them are in [`diagnostics/`](diagnostics/). The remaining rules for stable runs:

- run against the production build (`npm run build && npm start`), not `npm run dev`;
- after `login_as()`, wait for something on the page before navigating again;
- wait for asynchronously loaded `<select>` options (`BasePage.select_by_value` does this).

## Prerequisites

- The backend running with `APP_ENV=test` and `FIXED_NOW=2026-11-10T09:00:00`, and the
  frontend running (see [`../../commands.md`](../../commands.md)).
- Google Chrome installed. Selenium Manager fetches the matching driver.
- Python 3.11+.
