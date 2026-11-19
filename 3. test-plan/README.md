# 01 — Test Plan

The planning document for testing FreshCart: what is tested, how, in what environment, and
when testing is considered done.

## Contents

| File | Description |
|---|---|
| [`Test_Plan.md`](Test_Plan.md) | The full test plan (12 sections) |

## What the plan covers

| Section | Topic |
|---|---|
| 1–3 | Introduction, scope (in and out), test items: REST API, order-status WebSocket, web frontend |
| 4 | Test approach: automated Selenium + pytest for UI flows, manual/exploratory for the rest, with boundary value analysis and equivalence partitioning |
| 5 | Environment: `APP_ENV=test`, `FIXED_NOW=2026-11-10T09:00:00`, and the seed data the cases rely on |
| 6–8 | Entry criteria, exit criteria, suspension and resumption criteria |
| 9 | Risks and mitigations: clock-dependent flakiness, Selenium timing, shared seeded state, driver drift |
| 10–12 | Deliverables, schedule, roles |

## Exit criteria

1. All automated test cases executed, with the pass rate recorded in `12. final-test-report`.
2. Every failure has a defect entry or a documented rationale.
3. No open Critical or High defects.

The outcome against these criteria is assessed in the
[Test Summary Report](../12.%20final-test-report/Test_Summary_Report.md).

## Out of scope

Load and performance testing, security penetration testing, real payment gateway and SMS/email
integration (all mocked or absent in FreshCart), pixel-level visual regression, and browsers
other than Chrome.

## Related

- Spec the plan tests against: [`../0. application/docs/REQUIREMENTS.md`](../0.%20application/docs/REQUIREMENTS.md)
- Next step: [`../4. test-cases/`](../4.%20test-cases/)
