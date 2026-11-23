# Conclusion

## What was tested and the outcome

FreshCart (online grocery shopping and delivery, 42 business rules in 9 modules) was tested at five levels, with two
black-box and two white-box methods. All results below come from the runs recorded in `10-test-execution/`,
`6-white-box-testing/`, `7-api-testing/` and `5-black-box-testing/`.

| Level | Tool | Result |
|---|---|---|
| UI end to end | Selenium + pytest, 86 cases | 86 passed, 0 failed (last run before DEF-004 and DEF-005 were reopened) |
| API | Postman collection run with Newman, 245 requests, 475 assertions | 23 assertions failed, in 15 requests (DEF-004, DEF-005 and their knock-on effects) |
| Black box: EP and BVA | pytest over HTTP, 45 cases, 288 tests (one per class or boundary value) | 288 passed, 0 failed |
| White box: basis path and coverage | pytest + pytest-cov, 136 unit tests | 136 run: 127 passed, 9 failed (DEF-005 regression tests) |
| Design | EP, BVA, decision tables, state transition; 169 cases tracing to 42 of 42 rules | n/a |

Coverage (coverage.py, branch on): unit tests 65.2% of statements and 38.2% of branches; API suite 94.4% and 82.5%;
combined 95.0% and 86.8%. The five functions chosen for white-box analysis are at 100% statement and branch coverage in
the unit run. See [`6-white-box-testing/Coverage_Report.md`](../6-white-box-testing/Coverage_Report.md).

Eight defects are recorded; two are open. Two came from development (DEF-001, DEF-002). Six were found while
re-verifying the automated results (DEF-003 to DEF-008). DEF-004 and DEF-005 (both Low) were fixed and then reopened on
2026-11-23 by backing out their code changes, so that the suites show failing tests: nine unit tests and 23 Newman
assertions fail, and the black-box and Selenium suites do not notice. That gap is a finding in itself: the technique-based
black-box suite has no case for a trailing newline or an anonymous call to the slots endpoint.

## What each technique found

| Technique | What it contributed |
|---|---|
| Selenium UI automation | DEF-003 (tokens rejected in test mode), DEF-007 (stale search results), DEF-008 (session cleared by an aborted request). Also the intermittent timeouts that the first report had put down to the tooling. |
| API testing | DEF-004 (an endpoint without authentication), a 400 versus 422 inconsistency for cart quantity, and cases the UI cannot reach (the 21st cart item, the rate limit, a stock race, exact money boundaries). |
| White-box review and unit tests | DEF-005 (a `$` anchor accepting a trailing newline), a redundant branch in `complete_delivery` (one of its 7 basis paths cannot execute), an unused module (`schemas/common.py`), exact boundary checks for 299.00, 5000.00 and the 15-minute lock. |
| Black box: EP and BVA suite | Every class and boundary of every input in M1-M9, including the four classes that had no case and exact money edges (298.99/299.00, 5000.00/5000.01, 199.99/200.00) that the UI cannot build. No new defect: all 288 tests passed. The value was confirming each rule at both sides of its limit and closing the design gaps. |
| Decision table, state transition | 21 added test cases for transitions that had none (for example the CONFIRMED to cancelled path, backward moves, and a 4-then-success login). They found no new defect; they all passed. Their value was in making the gaps visible: 3 illegal order transitions and 1 valid one had no test. |

## Limitations

- The six timeouts in the first report cannot be reproduced exactly; the link to DEF-008 is an inference from a
  reproduction, stated as such in the Execution Log.
- WebSocket live updates (R6.7) have no automated test; the largest uncovered code is `routers/ws.py`.
- One browser, one machine, SQLite only. The PostgreSQL and Docker stack was not part of the recorded runs.
- The black-box suite sees only the API: it cannot show that a branch executed, and the exact 2-hour slot lead-time edge cannot be hit because slots start on even hours (it is probed at 1 h and 3 h).
- The GitHub Actions workflow runs unit tests with coverage, Newman, the frontend build and the Selenium suite, and
  passed on a hosted runner on 2026-11-14 (the black-box job was added afterwards and has not run on a hosted runner yet). Its first Selenium run failed on the login rate limit (HTTP 429) because CI
  is faster than a local run; `/test/reset` now clears the limiter.
- Mutation testing was not run, so the strength of the assertions is unmeasured beyond coverage.
- All commits so far come from one GitHub identity; the group contribution record still has to be built
  (see `13-reflections/Team_Learning_Reflection.md`).

## Lessons

- A flaky test is a result to investigate. The intermittent timeouts that the first report put down to the tooling
  hid a clock bug in test mode (DEF-003) and two front-end defects (DEF-007, DEF-008). Each was isolated with a script
  that counts how often the failure happens, before and after the change.
- Two clocks in one system (the injected one and the real one) caused DEF-003. A test hook such as `FIXED_NOW` has to be
  applied everywhere time is read, including token validation.
- Run end-to-end suites against a production build and wait on application state (the logged-in navbar, the filled
  heart, the select option) rather than on the existence of a container element.
- Coverage numbers need a check that the tool can see the code: the first API coverage run reported 3 of 18 statements for
  a function that Newman had plainly exercised, because async database code runs in greenlets.
- Numbers quoted in documents drift. `14-tools/consistency_check.py` compares them with the CSV, the Newman report and the
  test files.
