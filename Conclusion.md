# Conclusion

## What was tested and the outcome

FreshCart (online grocery shopping and delivery, 42 business rules in 9 modules) was tested at four levels. All
results below come from the runs recorded in `03_Test_Execution/`, `08_White_Box_Testing/` and `09_API_Testing/`.

| Level | Tool | Result |
|---|---|---|
| UI end to end | Selenium + pytest, 86 cases | 86 passed, 0 failed |
| API | Postman collection run with Newman, 245 requests, 475 assertions | 0 failed |
| Unit / white box | pytest + pytest-cov, 136 tests | 136 passed |
| Design | EP, BVA, decision tables, state transition; 116 cases tracing to 42 of 42 rules | n/a |

Coverage (coverage.py, branch on): unit tests 65.2% of statements and 38.2% of branches; API suite 94.4% and 82.5%;
combined 95.0% and 86.8%. The five functions chosen for white-box analysis are at 100% statement and branch coverage in
the unit run. See [`08_White_Box_Testing/Coverage_Report.md`](08_White_Box_Testing/Coverage_Report.md).

Eight defects are recorded; none is open. Two came from development (DEF-001, DEF-002). Six were found while
re-verifying the automated results (DEF-003 to DEF-008).

## What each technique found

| Technique | What it contributed |
|---|---|
| Selenium UI automation | DEF-003 (tokens rejected in test mode), DEF-007 (stale search results), DEF-008 (session cleared by an aborted request). Also the intermittent timeouts that the first report had put down to the tooling. |
| API testing | DEF-004 (an endpoint without authentication), a 400 versus 422 inconsistency for cart quantity, and cases the UI cannot reach (the 21st cart item, the rate limit, a stock race, exact money boundaries). |
| White-box review and unit tests | DEF-005 (a `$` anchor accepting a trailing newline), a redundant branch in `complete_delivery` (one of its 7 basis paths cannot execute), an unused module (`schemas/common.py`), exact boundary checks for 299.00, 5000.00 and the 15-minute lock. |
| EP, BVA, decision table, state transition | 21 added test cases for boundaries and transitions that had none (for example the CONFIRMED to cancelled path, backward moves, and a 4-then-success login). They found no new defect; they all passed. Their value was in making the gaps visible: 3 illegal order transitions and 1 valid one had no test. |

## Limitations

- The six timeouts in the first report cannot be reproduced exactly; the link to DEF-008 is an inference from a
  reproduction, stated as such in the Execution Log.
- WebSocket live updates (R6.7) have no automated test; the largest uncovered code is `routers/ws.py`.
- One browser, one machine, SQLite only. The PostgreSQL and Docker stack was not part of the recorded runs.
- Four equivalence classes have no test (see `02_Test_Case_Design/Equivalence_Partitioning.md`).
- The GitHub Actions workflow now runs unit tests with coverage, Newman and the Selenium suite, but has not run yet
  because nothing was pushed. The Selenium job is non-blocking until it passes on a hosted runner.
- Mutation testing was not run, so the strength of the assertions is unmeasured beyond coverage.
- All commits so far come from one GitHub identity; the group contribution record still has to be built
  (see `Team_Learning_Reflection.md`).

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
- Numbers quoted in documents drift. `tools/consistency_check.py` compares them with the CSV, the Newman report and the
  test files.
