# Test metrics

Every figure comes from a file in this repository (named in the Source column). Derived ratios are computed from those figures and the arithmetic is shown. The charts are in [`../Screenshots/metrics/`](../Screenshots/metrics/) and are regenerated with `python tools/make_evidence.py charts`.

## Design metrics

| Metric | Value | Source |
|---|---|---|
| Business rules | 42 | `Application/docs/REQUIREMENTS.md` |
| Rules with at least one test case | 42 (100%) | `Traceability_Matrix.md` |
| Test cases designed | 169 | `Test_Cases.csv` |
| Test cases per rule (average) | 4.0 (169 / 42) | derived |
| By automation level | Selenium 86, API 22, black-box 45, unit 16, manual 0 | `Test_Cases.csv` `Automated` column |
| By priority | Critical 7, High 99, Medium 56, Low 7 | `Test_Cases.csv` |
| Black-box cases | EP 19, BVA 26 | `Test_Cases.csv` `Type` column |
| White-box cases | basis path 3, coverage 5 | `Test_Cases.csv` `Type` column |
| Cases automated | 169 of 169 (100%) | `Test_Cases.csv`, `Formerly_Manual_Cases.md` |

## Execution metrics

| Suite | Executed | Passed | Failed | Wall-clock | Per test |
|---|---|---|---|---|---|
| Selenium UI | 86 | 86 | 0 | 2,056.7 s (34.3 min) | 23.9 s |
| Newman API | 245 requests (291 HTTP calls, 475 assertions) | 245 requests, 475 assertions | 0 | 351.1 s (5.9 min) | 1.4 s |
| Black-box EP/BVA | 288 | 288 | 0 | 141.6 s (2.4 min) | 0.49 s |
| Unit (pytest) | 136 | 136 | 0 | not recorded | n/a |
| **Total** | **755** (excluding assertions) | **755** | **0** | | |

Pass rate: 755 / 755 = 100% in the final runs. Sources: `selenium_junit.xml`, `newman_report.json`, `black_box_junit.xml`, `Execution_Log.md`. The first Selenium run on 2026-11-09 is kept in `Execution_Log_2026-11-09_first_run.md`; the figures above are the final runs only.

The black-box suite runs 288 tests in the time Selenium needs for about 6, because it uses HTTP and no browser.

## Coverage metrics (white box)

| Measure | Unit tests | API suite | Combined |
|---|---|---|---|
| Statements | 1,212 / 1,858 = 65.2% | 1,754 / 1,858 = 94.4% | 1,766 / 1,858 = **95.0%** |
| Branches | 107 / 280 = 38.2% | 231 / 280 = 82.5% | 243 / 280 = **86.8%** |

Source: `White_Box_Testing/coverage_*_summary.txt`, `coverage_combined_totals.txt`. The unit tests are aimed at 15 business-logic functions, not the whole backend, so 65.2% is expected. 14 of the 15 are at 100% statement and branch coverage; `cancel_order` is 9/10 statements and 5/6 branches.

Basis path testing: `validate_coupon` V(G) = 10 (10 paths), `_validate_payment` 7 paths, `complete_delivery` 7 paths of which 6 are feasible. Each feasible path has a test.

## Defect metrics

| Metric | Value |
|---|---|
| Defects found | 8 |
| By severity | Critical 1, High 2, Medium 2, Low 3 |
| Found during development / found while verifying | 2 / 6 |
| Found by | Selenium 3 (DEF-003, 007, 008), Newman 1 (DEF-004), code reading plus API 1 (DEF-005), code reading 1 (DEF-006), development 2 (DEF-001, 002) |
| Fixed and re-tested | 8 of 8 |
| Open | 0 |
| Defects found by the black-box EP/BVA suite | 0 (it closed four equivalence classes that had no test) |

Source: `Defect_Reports/README.md`, `Test_Summary_Report.md`.

## What these numbers do not show

- No performance, security or mutation figures exist; none were measured.
- Coverage is for the backend only. The Next.js frontend has no coverage measurement.
- Wall-clock times are from one Windows laptop and include browser start-up for Selenium.
- A 100% pass rate with 0 defects from the black-box suite means the suite found no further defects, not that none remain.

## Charts

| File | Shows |
|---|---|
| `01_cases_by_module.png` | 169 cases by module and automation level |
| `02_cases_by_type.png` | Cases by design technique |
| `03_cases_by_priority.png` | Cases by priority |
| `04_execution_results.png` | Passed and failed per suite |
| `05_execution_time.png` | Wall-clock time per suite |
| `06_black_box_by_module.png` | EP and BVA tests per module |
| `07_coverage_totals.png` | Statement and branch coverage: unit, API, combined |
| `08_function_coverage_unit.png` | Coverage per white-box target function |
| `09_defects.png` | Defects by severity and by how found |
| `10_newman_requests_by_folder.png` | Newman requests per folder |
