# 9 - Defect Reports

Defects found in FreshCart, each as its own report, plus a template for new ones.

## Contents

| ID | Title | Module | Severity | Status |
|---|---|---|---|---|
| [DEF-001](DEF-001_cart_stale_after_add.md) | Cart shows stale (empty) items right after the first add | M3 Cart | High | Fixed |
| [DEF-002](DEF-002_admin_orders_list_crash.md) | `GET /admin/orders` returns 500 once any order exists | M8 Admin | Critical | Fixed |
| [DEF-003](DEF-003_test_mode_tokens_expire_vs_real_clock.md) | Test-mode tokens expire against the real clock | M1 Auth | High | Fixed |
| [DEF-004](DEF-004_checkout_slots_endpoint_unauthenticated.md) | `GET /checkout/slots` reachable without a token | M5 Checkout | Low | Open |
| [DEF-005](DEF-005_validation_regex_accepts_trailing_newline.md) | Regexes accept a trailing newline and non-ASCII digits | M1, M5 | Low | Open |
| [DEF-006](DEF-006_wishlist_heart_redirects_before_auth_resolves.md) | Wishlist heart before session restore redirects to /login | M9 | Low | Fixed |
| [DEF-007](DEF-007_catalog_search_applies_stale_responses.md) | Catalog search shows an earlier keystroke's results | M2 | Medium | Fixed |
| [DEF-008](DEF-008_session_cleared_on_any_auth_me_error.md) | Any `/auth/me` error (including an aborted request) clears the session | M1 | Medium | Fixed |
| [Defect_Report_Template.md](Defect_Report_Template.md) | Blank template | | | |

## Open defects

Two, both Low: DEF-004 and DEF-005. They were fixed in `0c58076` and `611d7f4` and reopened on 2026-11-23 by backing
the code change out, so the demo shows failing unit and Newman tests and the defect workflow. Their regression checks
fail now: nine unit tests and 8 Newman assertions directly, plus 15 knock-on Newman assertions (see the Execution Log).
The other six are fixed. DEF-001 and DEF-002 were found during development. DEF-003 to DEF-008 were found while re-verifying the
automated results; each was fixed in its own commit (`fix(...)` referencing the ID) and has a regression check:
DEF-003 and DEF-005 unit tests that fail on the old code, DEF-004 and DEF-005 Newman requests, DEF-007 and DEF-008
diagnostic scripts in `8-automation-testing/selenium-or-playwright/diagnostics/`. DEF-006 was not independently reproduced before its fix.

## Report structure

Each report has: ID, title, reporter, date found, how it was found, module, affected rule IDs,
severity, priority and environment, followed by sections for **Summary**, **Steps to
reproduce**, **Expected result**, **Actual result**, **Evidence**, **Root cause**, **Fix** and
**Status**.

## Severity and priority scale

| Severity | Meaning |
|---|---|
| Critical | A core feature is unusable or data is corrupted |
| High | A major feature misbehaves, with no reasonable workaround |
| Medium | A feature misbehaves but a workaround exists |
| Low | Cosmetic or minor |

Priority is P1 (fix now), P2 (fix soon) or P3 (fix when convenient).

## Logging a new defect

1. Copy `Defect_Report_Template.md` to `DEF-NNN_short_description.md`, using the next free number.
2. Fill in every section and cite the failing test case ID where there is one.
3. Add a row to the table above and to the defects table in the
   [Test Summary Report](../12-final-test-report/Test_Summary_Report.md).
