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

API results per request are in [`../API_Testing/API_Test_Results.md`](../API_Testing/API_Test_Results.md);
unit and coverage results in [`../White_Box_Testing/Coverage_Report.md`](../White_Box_Testing/Coverage_Report.md);
black-box technique results in [`../Black_Box_Testing/Black_Box_Results.md`](../Black_Box_Testing/Black_Box_Results.md).

## Final results

| Suite | Result |
|---|---|
| Black-box EP and BVA (45 cases, 288 tests) | 288 passed, 0 failed |
| Selenium (86 cases) | 86 passed, 0 failed |
| Newman (245 requests, 475 assertions) | 0 failed |
| Unit tests (136) | 136 passed |

## Reproducing the Selenium run

1. Start the backend in test mode and the frontend as a production build (see [`../commands.md`](../commands.md)).
2. From [`../Test_Automation/`](../Test_Automation/):
   `pytest --html=report.html --self-contained-html --junitxml=junit.xml`, then
   `python tools/make_results_table.py junit.xml`.

## Related

- Plan: [`../Test_Plan/Test_Plan.md`](../Test_Plan/Test_Plan.md)
- Cases: [`../Test_Case_Design/Test_Cases.csv`](../Test_Case_Design/Test_Cases.csv)
- Defects: [`../Defect_Reports/`](../Defect_Reports/)
- Rollup: [`../Test_Reports/Test_Summary_Report.md`](../Test_Reports/Test_Summary_Report.md)
