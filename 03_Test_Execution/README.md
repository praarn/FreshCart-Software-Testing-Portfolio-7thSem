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

API results per request are in [`../09_API_Testing/API_Test_Results.md`](../09_API_Testing/API_Test_Results.md);
unit and coverage results in [`../08_White_Box_Testing/Coverage_Report.md`](../08_White_Box_Testing/Coverage_Report.md);
black-box technique results in [`../11_Black_Box_Testing/Black_Box_Results.md`](../11_Black_Box_Testing/Black_Box_Results.md).

## Final results

| Suite | Result |
|---|---|
| Black-box EP and BVA (45 cases, 288 tests) | 288 passed, 0 failed |
| Selenium (86 cases) | 86 passed, 0 failed |
| Newman (245 requests, 475 assertions) | 0 failed |
| Unit tests (136) | 136 passed |

## Reproducing the Selenium run

1. Start the backend in test mode and the frontend as a production build (see [`../commands.md`](../commands.md)).
2. From [`../05_Test_Automation/`](../05_Test_Automation/):
   `pytest --html=report.html --self-contained-html --junitxml=junit.xml`, then
   `python tools/make_results_table.py junit.xml`.

## Related

- Plan: [`../01_Test_Plan/Test_Plan.md`](../01_Test_Plan/Test_Plan.md)
- Cases: [`../02_Test_Case_Design/Test_Cases.csv`](../02_Test_Case_Design/Test_Cases.csv)
- Defects: [`../04_Defect_Reports/`](../04_Defect_Reports/)
- Rollup: [`../06_Test_Reports/Test_Summary_Report.md`](../06_Test_Reports/Test_Summary_Report.md)
