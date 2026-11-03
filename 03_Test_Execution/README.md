# 03 — Test Execution

The record of actually running the test cases.

## Contents

| File | Description |
|---|---|
| [`Execution_Log.md`](Execution_Log.md) | Run date, environment, per-module pass/fail counts, what happened during the run, and defects logged |

## Run summary

| | |
|---|---|
| Run date | 2026-11-09 |
| Environment | `APP_ENV=test`, `FIXED_NOW=2026-11-10T09:00:00`, SQLite, backend on `:8000`, frontend on `:3000` |
| Tooling | Selenium + pytest in headless Chrome, run module by module |
| Automated cases | 86 executed of 86 |
| Result | 80 passed, 6 failed |
| Manual/exploratory | 9 cases, not executed by design |

| Module | Passed / executed |
|---|---|
| M1 Auth | 17 / 17 |
| M2 Catalog | 7 / 7 |
| M3 Cart | 8 / 8 |
| M4 Coupons and pricing | 10 / 10 |
| M5 Checkout | 9 / 13 |
| M6 Order lifecycle | 12 / 12 |
| M7 Reviews | 3 / 3 |
| M8 Admin | 9 / 10 |
| M9 Wishlist, banners, offers | 5 / 6 |

## About the 6 failures

All six are Selenium `TimeoutException`s waiting for a page to render. The same flows were
re-driven with Playwright, 5 runs each, and rendered correctly every time with no console
errors. They are logged as a Selenium/chromedriver issue on the test machine, not as
application defects.

## Reproducing a run

1. Start the backend in test mode and the frontend (see [`../commands.md`](../commands.md)).
2. From [`../05_Test_Automation/`](../05_Test_Automation/), run `pytest`.

## Related

- Plan this run follows: [`../01_Test_Plan/Test_Plan.md`](../01_Test_Plan/Test_Plan.md)
- Cases executed: [`../02_Test_Case_Design/Test_Cases.csv`](../02_Test_Case_Design/Test_Cases.csv)
- Defects: [`../04_Defect_Reports/`](../04_Defect_Reports/)
- Rollup: [`../06_Test_Reports/Test_Summary_Report.md`](../06_Test_Reports/Test_Summary_Report.md)
