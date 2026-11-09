# Test Execution Log

**Run date:** 2026-11-09
**Environment:** `APP_ENV=test`, `FIXED_NOW=2026-11-10T09:00:00`, local (SQLite) — backend on
`:8000`, frontend on `:3000`, per [`../commands.md`](../commands.md)
**Executed by:** [`../05_Test_Automation`](../05_Test_Automation) (Selenium + pytest), run
module-by-module in headless Chrome
**Suite commit:** backend/frontend at the point `05_Test_Automation` was built (see
`git log` around the "test: add Selenium automation suite" commits)

## Summary

Counts below are the **automated** cases per module (see
`../02_Test_Case_Design/Test_Cases.csv`'s `Automated` column); each module also has a small
number of manual/exploratory cases not covered here (9 total across the suite — rate limiting,
cross-session timing, a rounding edge case, etc.), which were not executed in this run either.

| Module | Automated cases | Executed | Passed | Failed | Not yet run |
|---|---|---|---|---|---|
| M1 — Auth | 17 | 17 | 17 | 0 | 0 |
| M2 — Catalog | 7 | 7 | 7 | 0 | 0 |
| M3 — Cart | 8 | 8 | 8 | 0 | 0 |
| M4 — Coupons/pricing | 10 | 10 | 10 | 0 | 0 |
| M5 — Checkout | 13 | 13 | 9 | 4 | 0 |
| M6 — Order lifecycle | 12 | 0 | 0 | 0 | 12 |
| M7 — Reviews | 3 | 0 | 0 | 0 | 3 |
| M8 — Admin | 10 | 0 | 0 | 0 | 10 |
| M9 — Wishlist/banners/offers | 6 | 0 | 0 | 0 | 6 |
| **Total (automated)** | **86** | **55** | **51** | **4** | **31** |
| Manual/exploratory (9 cases) | — | 0 | — | — | 9 |

## What happened

A first full-suite run (one shared browser session for all 86 automated cases) surfaced two
real issues in the **test suite itself** (not the application — see "Issues found and fixed"
below), plus a Selenium session that became unstable and crashed partway through a 15-minute
run, cascading failures into every test after that point. The driver fixture was changed from
session-scoped to function-scoped (a fresh browser per test) to make that failure mode
structurally impossible, and the suite was re-run module-by-module in headless mode to keep
memory use down (the development machine was under real memory pressure during this run — see
"Known limitation" below).

### Issues found and fixed (in the test suite, not the application)

1. **Native HTML5 validation blocking a negative test.** `TC-M1-005` originally submitted
   `not-an-email` against an `<input type="email">`; Chrome's native validator blocks the
   form submission before React ever sees it, so the test was exercising the browser's
   validator, not the application's. Fixed by using `foo@bar` (passes native HTML5 email
   validation, which only requires one label after `@`, but fails the backend's stricter
   `local@domain.tld` regex) — now correctly reaches and tests the server-side rule (R1.2).
2. **Selenium's `visibility_of_element_located` on a childless container.** `TC-M2-007`
   waited for the product grid container after a search expected to return zero results; an
   empty CSS grid `<div>` with no children collapses to zero height, which Selenium treats as
   "not displayed". Fixed by waiting on the empty-state message instead, which is also the
   more precise assertion for "hidden from customers" (R2.4).
3. **A boundary test case that was mathematically unreachable.** `TC-M4-010`/`011` specified
   an exact `299.00`/`298.99` subtotal, but every seeded product price is a multiple of 5, so
   299.00 cannot be built from any combination of seeded items. Corrected to the nearest
   achievable values either side of the threshold (`300.00` / `295.00`) — see
   `02_Test_Case_Design/Test_Cases.csv` for the exact product combinations used.

### M5 — 4 unresolved failures (Selenium-environment issue, not an application defect)

`test_checkout_serviceable_pincode_succeeds`, `test_checkout_non_serviceable_pincode_rejected`,
`test_card_valid_luhn_succeeds`, and `test_declined_test_card_rejected` fail with a Selenium
`TimeoutException` waiting for the checkout form to render after login + navigation, even with
the wait timeout raised from 10s to 20s. To rule out an application bug, the identical
login → navigate → `/checkout` flow was driven with Playwright (a different browser-automation
tool) 5 times in a row: the page rendered in under 1 second every time, with zero console
errors. This isolates the failure to the Selenium/chromedriver setup on this machine — quite
possibly aggravated by the memory pressure noted below — rather than FreshCart itself. Not
logged as an application defect. A clean re-run on a less-loaded machine (or with chromedriver
logging enabled) is the next step to root-cause it on the tooling side.

### Known limitation: M6–M9 and 9 manual cases not executed this run

While diagnosing the M5 issue above, the host machine's available memory dropped low enough
that the harness running this session twice stopped a background Selenium process to protect
the system, with an explicit instruction not to restart such work automatically. Per the
project owner's decision, this run stops here rather than pushing further against a
resource-constrained machine. **M6 (order lifecycle), M7 (reviews), M8 (admin), and M9
(wishlist/banners/offers) — 31 automated cases — plus the 9 manual/exploratory cases were not
executed in this run.** All of M1–M9's *business logic* was, however, exercised and manually
verified via curl/Playwright during the original application build (see the commit history
and `00_Application/backend/explanation.md`) — this gap is specifically in **automated
Selenium coverage**, not in whether the features work at all.

**Recommended next step:** re-run `pytest tests/test_m6_order_lifecycle.py
tests/test_m7_reviews.py tests/test_m8_admin.py tests/test_m9_wishlist_banners_offers.py` from
`05_Test_Automation` on a machine with more headroom (or after closing other heavy
applications), plus the 4 flagged M5 cases.

## Defects logged

| Defect | Found via | Status |
|---|---|---|
| [`DEF-001`](../04_Defect_Reports/DEF-001_cart_stale_after_add.md) | Manual testing during M3 development (predates this automated run) | Fixed |
| [`DEF-002`](../04_Defect_Reports/DEF-002_admin_orders_list_crash.md) | Manual/Playwright testing during M8 development (predates this automated run) | Fixed |

No new defects were found in the 51 cases that executed cleanly in this run.
