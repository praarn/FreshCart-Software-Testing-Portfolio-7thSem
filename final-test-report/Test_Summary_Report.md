# Test Summary Report - FreshCart

**Report date:** 2026-11-14
**Scope:** All 42 business rules (R1.1-R9.3) across modules M1-M9, per
[`../application/docs/REQUIREMENTS.md`](../application/docs/REQUIREMENTS.md)
**References:** [Test Plan](../test-plan/Test_Plan.md) |
[Requirements Analysis](../requirements/Requirements_Analysis.md) |
[Test cases](../test-cases/Test_Cases.csv) |
[Execution Log](../test-execution/Execution_Log.md) |
[Coverage Report](../white-box-testing/Coverage_Report.md) |
[API results](../api-testing/API_Test_Results.md)

## Headline numbers

| Metric | Value |
|---|---|
| Business rules covered by the test design | 42 / 42 |
| Test cases designed | 169 (86 Selenium, 22 API, 45 black-box EP/BVA, 16 unit, 0 manual) |
| Black-box suite (equivalence partitioning, boundary value analysis) | 288 executed, 288 passed |
| Selenium suite | 86 executed, 86 passed |
| API suite (Newman) | 245 requests, 475 assertions, 0 failed |
| Unit tests (pytest) | 136 executed, 136 passed |
| Defects found in this verification | 6 (DEF-003 to DEF-008), all fixed and re-tested |
| Defects from development | 2 (DEF-001, DEF-002), fixed |
| Open defects | 0 |

Coverage figures (statement and branch, unit tests and API suite) are in the
[Coverage Report](../white-box-testing/Coverage_Report.md); they are not repeated here so there is one source.

## Results by module

Cases per module by automation level (`Y` Selenium, `A` API, `B` black-box EP/BVA suite, `U` unit including the white-box basis path and coverage cases). All cases passed in the final runs.

| Module | Rules | Selenium | API | Black-box | Unit | Total |
|---|---|---|---|---|---|---|
| M1 Registration and login | 8 | 17 | 7 | 11 | 4 | 39 |
| M2 Catalog | 4 | 7 | 0 | 3 | 0 | 10 |
| M3 Cart | 5 | 8 | 4 | 5 | 0 | 17 |
| M4 Coupons and pricing | 4 | 10 | 1 | 5 | 7 | 23 |
| M5 Checkout | 5 | 13 | 4 | 9 | 3 | 29 |
| M6 Order lifecycle | 7 | 12 | 5 | 2 | 2 | 21 |
| M7 Reviews | 1 | 3 | 1 | 3 | 0 | 7 |
| M8 Admin | 5 | 10 | 0 | 4 | 0 | 14 |
| M9 Wishlist, banners, offers | 3 | 6 | 0 | 3 | 0 | 9 |
| **Total** | 42 | 86 | 22 | 45 | 16 | 169 |

## Results by testing method

| Kind | Method | Test cases | Executed by | Result |
|---|---|---|---|---|
| Black box | Equivalence partitioning | 19 | `black-box-testing/tests/test_ep_*.py` | see [`Black_Box_Results.md`](../black-box-testing/Black_Box_Results.md) |
| Black box | Boundary value analysis | 26 | `black-box-testing/tests/test_bva_*.py` | see the same file |
| White box | Basis path testing | 3 (`validate_coupon` 10 paths, `_validate_payment` 7, `complete_delivery` 6 feasible) | `application/backend/tests/unit/` | all paths executed, 136 unit tests passed |
| White box | Statement, branch and condition coverage | 5 | same unit tests, measured by pytest-cov | targeted functions at 100% statements and branches except `cancel_order` (9/10, 5/6); see the [Coverage Report](../white-box-testing/Coverage_Report.md) |

M2, M8 and M9 API behaviour is also covered by the Newman requests that carry `API-*` IDs (not counted above because
they are not separate designed cases); see [`API_Test_Results.md`](../api-testing/API_Test_Results.md).

## Defects

| ID | Title | Severity | Found by | Status |
|---|---|---|---|---|
| [DEF-001](../defect-reports/DEF-001_cart_stale_after_add.md) | Cart shows stale items after the first add | High | Development | Fixed |
| [DEF-002](../defect-reports/DEF-002_admin_orders_list_crash.md) | `GET /admin/orders` 500 once an order exists | Critical | Development | Fixed |
| [DEF-003](../defect-reports/DEF-003_test_mode_tokens_expire_vs_real_clock.md) | Test-mode tokens expire against the real clock | High | Selenium re-run | Fixed |
| [DEF-004](../defect-reports/DEF-004_checkout_slots_endpoint_unauthenticated.md) | `GET /checkout/slots` needs no token | Low | Newman | Fixed |
| [DEF-005](../defect-reports/DEF-005_validation_regex_accepts_trailing_newline.md) | Regexes accept a trailing newline and non-ASCII digits | Low | Code reading, API | Fixed |
| [DEF-006](../defect-reports/DEF-006_wishlist_heart_redirects_before_auth_resolves.md) | Heart click before session restore redirects to /login | Low | Code reading | Fixed |
| [DEF-007](../defect-reports/DEF-007_catalog_search_applies_stale_responses.md) | Search shows a stale response | Medium | Selenium + diagnostic | Fixed |
| [DEF-008](../defect-reports/DEF-008_session_cleared_on_any_auth_me_error.md) | Any `/auth/me` error clears the session | Medium | Selenium + diagnostic | Fixed |

## Observations that are not defects

- `complete_delivery` re-checks `otp_blocked` after setting it; one of its 7 basis paths is infeasible
  (see [`Basis_Path_Testing.md`](../white-box-testing/Basis_Path_Testing.md)).
- Quantity above 10 returns 422 for a new line and 400 on a re-add; `REQUIREMENTS.md` lists 400 for both
  (see [`Requirements_Analysis.md`](../requirements/Requirements_Analysis.md)).
- The admin cancel endpoint (`POST /admin/orders/{id}/cancel`) is covered by a unit test only, not by the API suite.

## Limitations

- WebSocket live updates (R6.7) are not automated; they are shown in `evidence/screenshots/08_*` and in the demo.
- One browser (Chrome), one machine, SQLite only (the Docker/PostgreSQL stack was not tested in this run).
- The GitHub Actions workflow passed on a hosted runner on 2026-11-14 (backend 136 passed, Newman 0 failed, frontend
  build, Selenium 86 passed). The first hosted Selenium run failed with 49 HTTP 429 responses because the suite ran
  faster than the login rate limit allows; `/test/reset` now clears the limiter (commit `e3638b8`).
- The new `black-box` CI job was added after the hosted run above and has not yet run on a hosted runner; the suite itself ran locally.
- No performance, security or mutation testing.

## Exit criteria (Test Plan section 7)

| Criterion | Met |
|---|---|
| All automated test cases executed | Yes: 86 Selenium + 245 requests + 288 black-box tests + 136 unit tests |
| Every failure has a defect entry or documented rationale | Yes: DEF-003 to DEF-008 |
| No open Critical or High defects | Yes: none open |
