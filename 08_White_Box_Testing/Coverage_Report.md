# Coverage Report

Tool: coverage.py 7.x through pytest-cov 7.1.0, branch coverage on, `source = app`. Run on 2026-11-14 against the
final code. Raw output is next to this file; every number below is copied from it.

| Run | What executed | Statements | Branches | Raw output |
|---|---|---|---|---|
| Unit tests | 136 pytest tests (`tests/`) | 1212 / 1858 = **65.2%** | 107 / 280 = **38.2%** | `coverage_term_unit.txt`, `coverage_unit_summary.txt`, `coverage_html/` |
| API suite | Newman, 245 requests, against the backend run under coverage | 1754 / 1858 = **94.4%** | 231 / 280 = **82.5%** | `coverage_term_api.txt`, `coverage_api_summary.txt` |
| Both combined | the two data files merged with `coverage combine` | 1766 / 1858 = **95.0%** | 243 / 280 = **86.8%** | `coverage_combined_totals.txt` |

"Branches" are coverage.py's arcs: each `if` or loop counts two (taken, not taken), per decision, not per condition.
The single "Cover" figure in the tool's table (62% unit, 93% API) mixes statements and branches.

The unit tests were written for the five modules chosen in [`README.md`](README.md), so the unit total is low by design;
the rest of the code is exercised by the API suite. Neither run includes the Selenium suite.

## Targeted functions (unit tests)

| Function | Statements | Branches |
|---|---|---|
| `pricing_service.validate_coupon` | 13 / 13 | 12 / 12 |
| `pricing_service.compute_discount` | 6 / 6 | 4 / 4 |
| `pricing_service.compute_delivery_fee`, `round2` | 2 / 2 | 0 / 0 |
| `checkout_service._validate_payment` | 16 / 16 | 12 / 12 |
| `checkout_service._luhn_ok` | 9 / 9 | 6 / 6 |
| `checkout_service._validate_slot` | 11 / 11 | 8 / 8 |
| `checkout_service._validate_address` | 3 / 3 | 2 / 2 |
| `order_service.complete_delivery` | 18 / 18 | 12 / 12 |
| `order_service.admin_advance_status` | 5 / 5 | 2 / 2 |
| `order_service.assign_delivery_partner` | 10 / 10 | 4 / 4 |
| `order_service.cancel_order` | 9 / 10 | 5 / 6 |
| `auth_service.authenticate_user` | 22 / 22 | 10 / 10 |
| `core.security.decode_access_token` / `create_access_token` | 13 / 13 | 2 / 2 |

`cancel_order` misses the loop body that restores stock (line 67) and one loop-exit arc because the unit fixtures create
orders without items; the API suite covers it (10 / 10 statements, 6 / 6 branches).

## Per module

| Module | Unit: statements | Unit: branches | API: statements | API: branches |
|---|---|---|---|---|
| `services/pricing_service.py` | 100% | 100% | 93.8% | 81.2% |
| `services/checkout_service.py` | 56.9% | 58.3% | 95.1% | 95.8% |
| `services/order_service.py` | 80.6% | 73.5% | 98.1% | 94.1% |
| `services/auth_service.py` | 75.0% | 83.3% | 93.8% | 91.7% |
| `core/security.py` | 100% | 100% | 96.2% | 50.0% |
| `services/cart_service.py` | 19.5% | 0% | 91.1% | 86.7% |
| `services/admin_service.py` | 21.1% | 0% | 89.9% | 60.0% |
| `services/catalog_service.py` | 26.7% | 0% | 100% | 100% |
| `services/review_service.py` | 45.8% | 0% | 100% | 100% |
| `services/wishlist_service.py` | 36.7% | 0% | 100% | 100% |
| `routers/*` (all) | 0-100% (`test_utils.py` 0%) | n/a | 93.9-100% except `ws.py` 27.5% | n/a |
| `schemas/order.py` | 100% | 100% | 97.8% | 85.7% |
| `schemas/user.py` | 94.3% | 70.0% | 100% | 100% |

Full per-module lists: `coverage_unit_summary.txt`, `coverage_api_summary.txt`.

## What is not covered, and why

| Code | Why |
|---|---|
| `routers/ws.py` (29 of 40 statements missed in both runs) and most of `core/ws_manager.py` | The WebSocket is not driven by Newman or the unit tests. R6.7 is demonstrated in `07_Screenshots/08_*` and in the demo. This is the largest gap. |
| `schemas/common.py` (10 statements, 0% in both runs) | No code imports it. Likely dead code. |
| Unit run: `cart_service`, `admin_service`, `catalog_service`, `banner_service`, `review_service`, `wishlist_service`, `deps.py` | Mostly SQL and CRUD, not targeted by unit tests. The API suite covers them (about 90% or better). |
| API run: `services/admin_service.py` branches (60%), `pricing_service.py` lines 35, 41, 44->46 | Error branches for unknown ids and the weekday and cap paths are covered by the unit tests, not by the API suite; the combined run closes them. |
| `routers/admin.py` lines 58-59 | The admin cancel endpoint has no API request (the service path is unit tested). |

## Findings from white-box analysis

- `complete_delivery` re-tests `otp_blocked` straight after possibly setting it; one of 7 basis paths is infeasible
  ([`Basis_Path_Testing.md`](Basis_Path_Testing.md)).
- `schemas/common.py` appears unused.
- DEF-003 and DEF-005 were found while writing the security and validation tests.

## How the numbers were produced

Unit tests:

```bash
cd 00_Application/backend
pytest --cov=app --cov-branch --cov-report=term-missing --cov-report=html:../../08_White_Box_Testing/coverage_html
```

API suite (the backend runs under coverage; SQLAlchemy's async layer needs `concurrency=greenlet`, which
`tools/run_instrumented_api.py` sets. Without it the DB-backed functions are under-counted, which happened on the
first attempt and was discarded):

```bash
cd 00_Application/backend
APP_ENV=test FIXED_NOW=2026-11-10T09:00:00 python ../../tools/run_instrumented_api.py 8001 .coverage.api
# in another terminal: newman run ... --env-var base_url=http://localhost:8001/api
# then: touch stop.flag next to .coverage.api (stops the server and writes the data)
coverage report --data-file=.coverage.api --show-missing
coverage json --data-file=.coverage.api -o cov.json && python ../../tools/coverage_summary.py cov.json
```

Screenshot of the HTML report: [`../07_Screenshots/`](../07_Screenshots/README.md).
