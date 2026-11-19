# 03 - Test Execution

The record of actually running the test cases.

## Contents

| File | Description |
|---|---|
| [`Execution_Log.md`](Execution_Log.md) | Environment, final results, history of each Selenium run, root causes, defects |
| [`Selenium_Results.md`](Selenium_Results.md) | One row per Selenium case: expected, actual, status, evidence, time (generated) |
| [`selenium_report.html`](selenium_report.html), [`selenium_junit.xml`](selenium_junit.xml) | pytest-html report and JUnit XML of the final Selenium run |
| [`Formerly_Manual_Cases.md`](Formerly_Manual_Cases.md) | The 9 cases that were manual, now executed through Newman or unit tests, with actual results |
| [`Execution_Log_2026-11-09_first_run.md`](Execution_Log_2026-11-09_first_run.md) | The original log (superseded) |

API results per request are in [`../api-testing/API_Test_Results.md`](../api-testing/API_Test_Results.md);
unit and coverage results in [`../white-box-testing/Coverage_Report.md`](../white-box-testing/Coverage_Report.md);
black-box technique results in [`../black-box-testing/Black_Box_Results.md`](../black-box-testing/Black_Box_Results.md).

## Final results

| Suite | Result |
|---|---|
| Black-box EP and BVA (45 cases, 288 tests) | 288 passed, 0 failed |
| Selenium (86 cases) | 86 passed, 0 failed |
| Newman (245 requests, 475 assertions) | 0 failed |
| Unit tests (136) | 136 passed |

## Reproducing the Selenium run

1. Start the backend in test mode and the frontend as a production build (see [`../commands.md`](../commands.md)).
2. From [`../automation-testing/selenium-or-playwright/`](../automation-testing/selenium-or-playwright/):
   `pytest --html=report.html --self-contained-html --junitxml=junit.xml`, then
   `python tools/make_results_table.py junit.xml`.

## Related

- Plan: [`../test-plan/Test_Plan.md`](../test-plan/Test_Plan.md)
- Cases: [`../test-cases/Test_Cases.csv`](../test-cases/Test_Cases.csv)
- Defects: [`../defect-reports/`](../defect-reports/)
- Rollup: [`../final-test-report/Test_Summary_Report.md`](../final-test-report/Test_Summary_Report.md)
