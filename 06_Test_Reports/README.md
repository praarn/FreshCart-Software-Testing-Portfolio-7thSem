# 06 — Test Reports

The final rollup of the testing effort.

## Contents

| File | Description |
|---|---|
| [`Test_Summary_Report.md`](Test_Summary_Report.md) | Headline metrics, rule coverage, results by module, explanation of the failures, defect summary and exit-criteria assessment |

## Headline numbers

| Metric | Value |
|---|---|
| Business rules covered | 42 / 42 |
| Test cases designed | 95 (86 automated, 9 manual) |
| Automated cases executed | 86 / 86 |
| Passed | 80 / 86 (93%) |
| Failed | 6, all Selenium/chromedriver timeouts |
| Open application defects | 0 |
| Defects fixed during development | 2 |

## Exit criteria

| Criterion | Met |
|---|---|
| All automated test cases executed | Yes, 86 / 86 |
| Every failure has a defect entry or documented rationale | Yes, 6 failures traced to tooling and cross-checked with Playwright |
| No open Critical or High defects | Yes, none open |

Overall, the project meets the exit criteria defined in the
[Test Plan](../01_Test_Plan/Test_Plan.md).

## Sections in the report

1. Headline numbers
2. Rule coverage
3. Results by module (M1–M9)
4. The 6 Selenium failures: a tooling issue, not an application defect
5. M6–M9 follow-up run
6. Defects
7. Exit criteria assessment

## Where the numbers come from

- Designed cases and rule coverage: [`../02_Test_Case_Design/`](../02_Test_Case_Design/)
- Per-run results: [`../03_Test_Execution/Execution_Log.md`](../03_Test_Execution/Execution_Log.md)
- Defects: [`../04_Defect_Reports/`](../04_Defect_Reports/)
