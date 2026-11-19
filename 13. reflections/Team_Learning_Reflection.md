# Team Contribution and Learning Reflection

The individual sections below were drafted from the repository history (`git log --author`), the defect reports and the
test results. Each member should read their own section and edit it so it matches their own experience.

## Team

| Member | Roll number | Role | GitHub username |
|---|---|---|---|
| Prapti R. N. | 1MS23IS094 | Test Analyst | [@praarn](https://github.com/praarn) |
| Poorvika G. J. | 1MS23IS090 | Test Engineer | [@poorvikagj](https://github.com/poorvikagj) |

## GitHub activity (from `git shortlog -sne HEAD`)

| Author in the history | GitHub | Commits |
|---|---|---|
| praarn | [@praarn](https://github.com/praarn) | 31 of 58 |
| poorvikagj | [@poorvikagj](https://github.com/poorvikagj) | 27 of 58 |

The repository has no pull requests or reviews yet; all work was committed directly to `main`. The open items below
are best done in branches with reviewed pull requests.

## Deliverables by suggested role

The deliverables are listed under the role they naturally belong to. Confirm or change the assignment; the
`Author` column in `git log` is the record that counts.

| Role | Deliverables |
|---|---|
| Test Analyst | `3. test-plan/` (plan, requirements analysis), `4. test-cases/` (EP, BVA, decision table, state transition, test cases, xlsx, traceability) |
| Test Engineer | `10. test-execution/`, `9. defect-reports/`, `12. final-test-report/`, `6. white-box-testing/`, `5. black-box-testing/` and `0. application/backend/tests/unit/` |

## Open items per role (to create real, attributable contributions)

| Role | Item |
|---|---|
| Test Analyst | Review the Test Plan and the new black-box case rows (`Black-box EP` / `Black-box BVA` in `Test_Cases.csv`); the four formerly unmapped EP classes are now covered by TC-M1-029, TC-M1-030 and TC-M5-019 |
| Test Engineer | Run `mutmut` on `pricing_service.py` and write `6. white-box-testing/Mutation_Testing.md`; decide whether to remove the redundant branch found in `complete_delivery` |

## Individual contribution and reflection

### Prapti R. N. (Test Analyst)

- Contributions (from `git log --author`): 31 commits. Test Plan, requirements analysis, the equivalence partitioning,
  boundary value analysis, decision table and state transition documents, the test case spreadsheet and traceability
  matrix; the white-box work (control flow graphs, basis path tests, unit tests and the coverage report); the Postman
  collection (245 requests) and its Newman reports; the black-box EP/BVA pytest suite (288 tests); fixes for DEF-003,
  DEF-006 and DEF-008; the final report, README and, in the last week, the restructure of the repository into the 13
  portfolio sections. On the application side, the catalog, cart, coupon, checkout, wishlist and banner modules.
- What I learned: Test cases are only as good as the rules they come from, so numbering the 42 business rules first
  and tracing every case back to one made gaps visible; the black-box review found four equivalence classes with no
  case (password without a letter, phone with non-digits, pincode below the range, pincode of the wrong length).
  Basis path testing forced me to read the code closely: `complete_delivery` has V(G) = 7 but only 6 feasible paths,
  and the analysis found a redundant branch. I also learned to read a coverage number critically: the unit tests alone
  reach 65.2% statements and 38.2% branches by design, and only the combination with the API suite (95.0% and 86.8%)
  says anything about the whole application.
- What was difficult: Keeping every number consistent across many documents (case counts, assertion counts, coverage
  figures) while the suites kept changing; that is why `14. tools/consistency_check.py` exists. Driving `validate_coupon`
  (V(G) = 10) through every path with realistic data was also slow, and a Selenium test that asserted the logout token
  was revoked before the asynchronous logout had finished was flaky on CI until it waited for the request.
- What I would do differently: Build the traceability matrix and the consistency check on day one instead of after
  the suites existed, run CI as soon as the first test exists, and use branches with pull requests and reviews so that
  each change has a visible reviewer.

### Poorvika G. J. (Test Engineer)

- Contributions (from `git log --author`): 27 commits. The Selenium suite for modules M1 to M9 (86 tests, with page
  objects) and its diagnostic scripts; test execution and the per-case results and execution log; the GitHub Actions
  workflow (unit tests with coverage, Newman, Selenium); fixes for DEF-004, DEF-005 and DEF-007 and the
  `/test/reset` rate-limit fix; the screenshots, metric charts, summary PDF and walkthrough GIF; and the move of the
  Selenium and defect folders in the restructure. On the application side, authentication, orders, reviews, admin and
  the Docker setup.
- What I learned: UI tests fail for timing reasons far more often than for functional ones, so waiting on `data-testid`
  elements instead of fixed sleeps matters. A failing test can point to a real defect: re-running the suite exposed
  stale catalog search results (DEF-007) and a session cleared by any `/auth/me` error (DEF-008), and small diagnostic
  scripts were needed to reproduce each one reliably. Running the suite on a hosted runner showed problems that never
  appeared locally: 49 requests got HTTP 429 because the suite ran faster than the login rate limit allowed.
- What was difficult: Isolating race conditions. The search defect only showed when the response to an earlier
  keystroke arrived after the response to a later one, so it needed a purpose-built diagnostic script to reproduce. Making the Selenium job stable on
  CI, and keeping the test-mode frozen clock and resettable database consistent between the local and CI runs, also took
  several iterations.
- What I would do differently: Add the CI workflow before writing the bulk of the Selenium tests so that runner-only
  failures appear early, clear shared state (rate limits, seed data) from the first run, and put each fix behind a pull
  request with a regression test that fails on the old code.

## Team reflection

The defects came mostly from re-running and reading, not from the design techniques alone. Selenium re-runs with
diagnostic scripts found three (DEF-003, DEF-007, DEF-008), code reading two (DEF-005, DEF-006), Newman one (DEF-004)
and development two (DEF-001, DEF-002). The black-box equivalence partitioning and boundary value suite found no new
defect once it ran (288 passed), but designing it exposed four unmapped equivalence classes, which now have cases. The
hardest defects to isolate were DEF-007 and DEF-008 because they depend on request timing, and DEF-003 because the test
suite only passed while real time was still before the frozen test clock plus 30 minutes (two clocks, one for issuing
tokens and one for validating them). Next time we would automate earlier, set up
CI and the consistency check at the start, add a traceability matrix before writing tests, and use pull requests with
reviews so that contributions are visible beyond commit counts. The suites do not cover performance, security or
mutation testing, and WebSocket live updates are shown in the demo rather than automated.

Prompts: Which technique found the most defects? Which defect was hardest to isolate and why? What would you
automate earlier next time?
