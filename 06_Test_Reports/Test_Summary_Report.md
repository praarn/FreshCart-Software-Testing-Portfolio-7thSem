# Test Summary Report - FreshCart

**Report date:** 2026-11-14
**Scope:** All 42 business rules (R1.1-R9.3) across modules M1-M9, per
[`../00_Application/docs/REQUIREMENTS.md`](../00_Application/docs/REQUIREMENTS.md)
**References:** [Test Plan](../01_Test_Plan/Test_Plan.md) |
[Requirements Analysis](../01_Test_Plan/Requirements_Analysis.md) |
[Test cases](../02_Test_Case_Design/Test_Cases.csv) |
[Execution Log](../03_Test_Execution/Execution_Log.md) |
[Coverage Report](../08_White_Box_Testing/Coverage_Report.md) |
[API results](../09_API_Testing/API_Test_Results.md)

## Headline numbers

| Metric | Value |
|---|---|
| Business rules covered by the test design | 42 / 42 |
| Test cases designed | 116 (86 Selenium, 22 API, 8 unit, 0 manual) |
| Selenium suite | 86 executed, 86 passed |
| API suite (Newman) | 245 requests, 475 assertions, 0 failed |
| Unit tests (pytest) | 136 executed, 136 passed |
| Defects found in this verification | 6 (DEF-003 to DEF-008), all fixed and re-tested |
| Defects from development | 2 (DEF-001, DEF-002), fixed |
| Open defects | 0 |

Coverage figures (statement and branch, unit tests and API suite) are in the
[Coverage Report](../08_White_Box_Testing/Coverage_Report.md); they are not repeated here so there is one source.

## Results by module

Cases per module by automation level (`Y` Selenium, `A` API, `U` unit). All cases passed in the final runs.

| Module | Rules | Selenium | API | Unit | Total |
|---|---|---|---|---|---|
| M1 Registration and login | 8 | 17 | 7 | 2 | 26 |
| M2 Catalog | 4 | 7 | 0 | 0 | 7 |
| M3 Cart | 5 | 8 | 4 | 0 | 12 |
| M4 Coupons and pricing | 4 | 10 | 1 | 5 | 16 |
| M5 Checkout | 5 | 13 | 4 | 1 | 18 |
| M6 Order lifecycle | 7 | 12 | 5 | 0 | 17 |
| M7 Reviews | 1 | 3 | 1 | 0 | 4 |
| M8 Admin | 5 | 10 | 0 | 0 | 10 |
| M9 Wishlist, banners, offers | 3 | 6 | 0 | 0 | 6 |
| **Total** | 42 | 86 | 22 | 8 | 116 |

M2, M8 and M9 API behaviour is also covered by the Newman requests that carry `API-*` IDs (not counted above because
they are not separate designed cases); see [`API_Test_Results.md`](../09_API_Testing/API_Test_Results.md).

## Defects

| ID | Title | Severity | Found by | Status |
|---|---|---|---|---|
| [DEF-001](../04_Defect_Reports/DEF-001_cart_stale_after_add.md) | Cart shows stale items after the first add | High | Development | Fixed |
| [DEF-002](../04_Defect_Reports/DEF-002_admin_orders_list_crash.md) | `GET /admin/orders` 500 once an order exists | Critical | Development | Fixed |
| [DEF-003](../04_Defect_Reports/DEF-003_test_mode_tokens_expire_vs_real_clock.md) | Test-mode tokens expire against the real clock | High | Selenium re-run | Fixed |
| [DEF-004](../04_Defect_Reports/DEF-004_checkout_slots_endpoint_unauthenticated.md) | `GET /checkout/slots` needs no token | Low | Newman | Fixed |
| [DEF-005](../04_Defect_Reports/DEF-005_validation_regex_accepts_trailing_newline.md) | Regexes accept a trailing newline and non-ASCII digits | Low | Code reading, API | Fixed |
| [DEF-006](../04_Defect_Reports/DEF-006_wishlist_heart_redirects_before_auth_resolves.md) | Heart click before session restore redirects to /login | Low | Code reading | Fixed |
| [DEF-007](../04_Defect_Reports/DEF-007_catalog_search_applies_stale_responses.md) | Search shows a stale response | Medium | Selenium + diagnostic | Fixed |
| [DEF-008](../04_Defect_Reports/DEF-008_session_cleared_on_any_auth_me_error.md) | Any `/auth/me` error clears the session | Medium | Selenium + diagnostic | Fixed |

## Observations that are not defects

- `complete_delivery` re-checks `otp_blocked` after setting it; one of its 7 basis paths is infeasible
  (see [`Basis_Path_Testing.md`](../08_White_Box_Testing/Basis_Path_Testing.md)).
- Quantity above 10 returns 422 for a new line and 400 on a re-add; `REQUIREMENTS.md` lists 400 for both
  (see [`Requirements_Analysis.md`](../01_Test_Plan/Requirements_Analysis.md)).
- The admin cancel endpoint (`POST /admin/orders/{id}/cancel`) is covered by a unit test only, not by the API suite.

## Limitations

- WebSocket live updates (R6.7) are not automated; they are shown in `07_Screenshots/08_*` and in the demo.
- One browser (Chrome), one machine, SQLite only (the Docker/PostgreSQL stack was not tested in this run).
- The GitHub Actions workflow was extended but has not run yet (nothing was pushed); the Selenium job is marked
  non-blocking until it has passed on a hosted runner.
- No performance, security or mutation testing.

## Exit criteria (Test Plan section 7)

| Criterion | Met |
|---|---|
| All automated test cases executed | Yes: 86 + 245 requests + 136 unit tests |
| Every failure has a defect entry or documented rationale | Yes: DEF-003 to DEF-008 |
| No open Critical or High defects | Yes: none open |
