# 04 — Defect Reports

Defects found in FreshCart, each as its own report, plus a template for new ones.

## Contents

| ID | Title | Module | Severity | Status |
|---|---|---|---|---|
| [DEF-001](DEF-001_cart_stale_after_add.md) | Cart shows stale (empty) items right after the first add-to-cart call | M3 Cart | High | Fixed |
| [DEF-002](DEF-002_admin_orders_list_crash.md) | `GET /admin/orders` returns 500 once any order exists | M8 Admin | Critical | Fixed |
| [Defect_Report_Template.md](Defect_Report_Template.md) | Blank template for new reports | | | |

## Open defects

None. Both defects above were found and fixed during the application's development, before
the automated suite existed. The automated run found no new application defects. Its 6
failures were traced to a Selenium tooling issue and are explained in the
[Execution Log](../03_Test_Execution/Execution_Log.md).

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
   [Test Summary Report](../06_Test_Reports/Test_Summary_Report.md).
