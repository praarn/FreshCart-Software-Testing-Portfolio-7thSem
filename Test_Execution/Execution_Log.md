# Test Execution Log

Current results. The original 2026-11-09 log is kept in
[`Execution_Log_2026-11-09_first_run.md`](Execution_Log_2026-11-09_first_run.md).

## Environment of the recorded runs

| Item | Value |
|---|---|
| Date | 2026-11-13 to 2026-11-14 (business clock frozen with `FIXED_NOW=2026-11-10T09:00:00`) |
| Backend | `APP_ENV=test`, SQLite, Python 3.12.10, `uvicorn` on :8000 |
| Frontend | Next.js production build (`npm run build && npm start`) on :3000 |
| Browser | Chrome 157.0.8103.51 headless, driver from Selenium Manager |
| Machine | Windows 11 laptop; one Selenium test takes 10-20 s of which 8-10 s is browser start-up |

## Final results (all executed against the current code)

| Suite | Cases | Passed | Failed | Report |
|---|---|---|---|---|
| Selenium UI (`Test_Automation`) | 86 | 86 | 0 | [`selenium_report.html`](selenium_report.html), [`Selenium_Results.md`](Selenium_Results.md), [`selenium_junit.xml`](selenium_junit.xml) |
| Newman API (`API_Testing`) | 245 requests, 475 assertions | 245 | 0 | [`API_Test_Results.md`](../API_Testing/API_Test_Results.md) |
| Black-box EP and BVA (`Black_Box_Testing`) | 288 | 288 | 0 | [`Black_Box_Results.md`](../Black_Box_Testing/Black_Box_Results.md), [`black_box_junit.xml`](../Black_Box_Testing/results/black_box_junit.xml) |
| Unit tests (`Application/backend/tests`) | 136 | 136 | 0 | [`Coverage_Report.md`](../White_Box_Testing/Coverage_Report.md) |

The 9 cases that were manual in the first run were executed through Newman or unit tests; see
[`Formerly_Manual_Cases.md`](Formerly_Manual_Cases.md).

## History of the Selenium runs

Each row is a full 86-test run unless noted. Counts come from the pytest summary line.

| Run | Frontend | Code state | Result | Failures and finding |
|---|---|---|---|---|
| 0 (first attempt, 2026-11-13) | dev server | before DEF-003 fix | 1 test tried | `test_checkout_serviceable_pincode_succeeds` failed. Diagnostic: `/checkout` renders then redirects to `/login`; `/auth/me` returned 401. **DEF-003** (token expiry checked against the real clock in test mode). |
| 1 | `npm run dev` | DEF-003 fixed | 81 passed, 5 failed | `test_welcome10_applies_for_first_order`, `test_checkout_short_address_line1_rejected`, `test_card_valid_luhn_succeeds`, `test_admin_locks_and_unlocks_user`, `test_remove_from_wishlist`: `TimeoutException` waiting for a page element. Other work was running on the machine at the time. Re-run alone, all five passed (131 s) but each call took 12-15 s against a 20 s wait. |
| 2 | production build | DEF-004, DEF-005 fixed | 85 passed, 1 failed | `test_add_product_to_wishlist` (empty wishlist after the heart click). Passed twice when run alone. |
| 3 | production build | + DEF-006 fix | 85 passed, 1 failed | `test_inactive_product_hidden_from_customers`. Not reproducible by re-running; the diagnostic found that the search box fires one request per keystroke and shows the last response to arrive (37 of 40 loads wrong). **DEF-007**. |
| 4 | production build | + DEF-007 fix | 84 passed, 2 failed | `test_filter_by_category`: `NoSuchElementException` (the select's options load after the select appears; fixed in the test helper). `test_add_product_to_wishlist` failed 3 of 3 re-runs: the session token was missing right after navigation. **DEF-008** (any error from `/auth/me`, including an aborted request, clears the token). |
| 5 (final) | production build | + DEF-008 fix, select wait | **86 passed, 0 failed** | 34 min 16 s |

## Root cause of the six original failures

The first log attributed the six timeouts to Selenium or chromedriver. That is not supported:

- Every one of the six opens a guarded page (`/checkout`, `/admin/users`, the wishlist grid) straight after `login_as()`.
  DEF-008 shows the session token is wiped when the next navigation aborts `/auth/me` (7 of 12 iterations before the
  fix, 0 of 12 after). `RoleGuard` then redirects to `/login` and the wait for the page element times out.
- DEF-003 makes every login-dependent test fail once the real date passes `FIXED_NOW` + 30 minutes.
- A slow development server adds to both (12-15 s page waits against a 20 s limit).

The original environment cannot be recreated, so the link to those six runs is inferred from the reproduction, not
proven. The Playwright cross-checks cited in the first log cannot be inspected (the scripts were never committed).

The two hypotheses suggested at the start of this work were tested: a slow `next dev` contributes
(moving from run 1 to the production build in run 2 changed 5 failures into 1), and `RoleGuard` itself is correct but depends
on `AuthProvider`, which is where the defect was.

## Defects found in this re-verification

| Defect | Found by | Severity | Status |
|---|---|---|---|
| [DEF-003](../Defect_Reports/DEF-003_test_mode_tokens_expire_vs_real_clock.md) | Selenium re-run | High | Fixed |
| [DEF-004](../Defect_Reports/DEF-004_checkout_slots_endpoint_unauthenticated.md) | Newman | Low | Fixed |
| [DEF-005](../Defect_Reports/DEF-005_validation_regex_accepts_trailing_newline.md) | Code reading, confirmed by API | Low | Fixed |
| [DEF-006](../Defect_Reports/DEF-006_wishlist_heart_redirects_before_auth_resolves.md) | Code reading during run 2 | Low | Fixed |
| [DEF-007](../Defect_Reports/DEF-007_catalog_search_applies_stale_responses.md) | Selenium run 3 plus a diagnostic | Medium | Fixed |
| [DEF-008](../Defect_Reports/DEF-008_session_cleared_on_any_auth_me_error.md) | Selenium run 4 plus a diagnostic | Medium | Fixed |

DEF-001 and DEF-002 are from development and remain fixed.
