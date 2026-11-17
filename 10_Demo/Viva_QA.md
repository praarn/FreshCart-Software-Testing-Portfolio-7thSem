# Viva Q&A

Short answers grounded in this repository. Numbers are the committed results; where a number may
change after a re-run, the source file is named.

## Application and process

1. **What is FreshCart?** An online grocery ordering and delivery system with three roles (customer, admin, delivery partner): catalog, cart, coupons, checkout, order lifecycle with live status over WebSocket, reviews, admin tools, wishlist and banners. FastAPI backend, Next.js frontend, 42 business rules (R1.1-R9.3) in `00_Application/docs/REQUIREMENTS.md`.
2. **Which testing activities did you do?** Test plan and requirements analysis, black-box testing with two methods (equivalence partitioning and boundary value analysis, designed and run as a suite, plus decision table and state transition as support), white-box testing with two methods (basis path and coverage), API testing, Selenium UI automation, execution with actual results, defect reports, and a final report. The additional activity is Selenium plus Postman/Newman.
3. **What is traceability and what did it give you?** `Traceability_Matrix.md` maps every rule to its test cases, generated from the CSV. It shows 42 of 42 rules covered and tells you which cases to re-run when a rule changes.
4. **Why a fixed clock (`FIXED_NOW`)?** Slot rules and the `FRESH15` weekday rule depend on today's date. A fixed Tuesday 09:00 makes them repeatable. It also caused DEF-003.

## Black-box techniques

4a. **Which are your two black-box and two white-box methods?** Black box: equivalence partitioning and boundary value analysis, run in `11_Black_Box_Testing` (45 cases, one pytest test per class or boundary value, over HTTP only). White box: basis path testing (CFG, V(G), one test per path, `Basis_Path_Testing.md`) and statement/branch/condition coverage (`Coverage_Report.md`). Each has its own case IDs in `Test_Cases.csv` (types `Black-box EP`, `Black-box BVA`, `White-box basis path`, `White-box coverage`).
5. **Why equivalence partitioning here?** Inputs such as name, email, password, phone, pincode have a few distinct behaviours, so one value per class is enough. Example: pincode classes are in range, out of range, wrong length (`Equivalence_Partitioning.md`).
6. **Why boundary value analysis?** Off-by-one errors cluster at limits. Password 7/8/20/21, quantity 0/1/10/11, COD 5000/5000.01, slot capacity 5/6, lock after 4/5 failures.
7. **What was hard about the delivery-fee boundary?** 299.00 cannot be built from seeded prices (all multiples of 5), so the UI cases use 295.00 and 300.00 and the exact 298.99/299.00 pair is tested on `compute_delivery_fee` (TC-M4-013/014). The black-box suite removes the limit: it creates a product at exactly 298.99, 299.00 or 299.01 through the admin API and checks the cart's fee (TC-M4-020).
8. **What does the coupon decision table show?** Seven rules from the five conditions (code valid, not expired, minimum met, first-order, weekday). Conditions are checked in a fixed order, so later ones are don't-care once an earlier one fails (rule D7 shows the minimum message wins over the first-order message).
9. **Which state transitions did you test?** Seven valid and eight illegal order transitions (illegal ones must return 409), and the lockout machine ACTIVE to LOCKED to ACTIVE (`State_Transition.md`). Three illegal transitions and one valid one had no test before; TC-M6-014 to 017 were added.

## White-box

10. **What does V(G) mean?** Cyclomatic complexity: the number of linearly independent paths, and the minimum number of tests for full branch coverage. Computed as E - N + 2, predicates + 1, and regions; all three agree (10 for `validate_coupon`, 7 for `_validate_payment`, 7 for `complete_delivery`).
11. **Statement vs branch vs condition coverage?** Statement: every line runs. Branch: every decision takes both outcomes. Condition: every simple condition inside a decision takes both outcomes (`A or B` needs A true/false and B true/false). coverage.py measures the first two; condition coverage is shown by the path tables in `Basis_Path_Testing.md`.
12. **Did you find anything by white-box analysis?** In `complete_delivery` the second `otp_blocked` check cannot differ from the first (V(G)=7 but only 6 feasible paths). Reading the regexes found DEF-005.
13. **What is your coverage and why not 100%?** See `Coverage_Report.md`. The unit tests target the five business-logic modules; routers and simple SQL services are covered by the API and Selenium suites, which are not counted by the unit run.
14. **Is high coverage proof of quality?** No. It shows code ran, not that assertions are strong. Mutation testing would measure that (see question 25).

## API and automation

15. **Why Selenium and API tests?** Selenium checks what a user sees but is slow. API tests check the contract and rules quickly: status codes, the error shape, role access, and cases the UI cannot produce (exact boundaries, parallel state like a stock race).
16. **What does the Newman suite check?** 245 requests, 475 assertions: status, shape, the `{status, error, message, field_errors}` contract, role checks, and values such as discount 36.00. Source: `09_API_Testing/API_Test_Results.md`.
17. **Why is the API run slow?** Login and register are limited to 10 per minute (R1.7) and the limiter is in memory, so the collection waits; this also tests the 429 response.
18. **Why Page Object Model?** Locators live in `pages/`, tests read as user steps, and a UI change touches one file. Locators use `data-testid`.
19. **Why a fresh browser per test?** A single long session became unstable and cascaded failures. Function-scoped drivers isolate tests at the cost of time.

## Results and defects

20. **What failed in the Selenium suite and why?** The first run showed 6 timeouts, put down to Selenium. On re-run the causes were in the application: test-mode tokens expiring against the real clock (DEF-003), the session token being cleared when `/auth/me` is aborted by a navigation (DEF-008, lost in 7 of 12 loads before the fix), and stale search responses (DEF-007, 37 of 40 loads before the fix). A slow development server made it worse; the final run on a production build is 86 of 86 (`03_Test_Execution/Execution_Log.md`). The link to the original six is inferred, not proven.
21. **What was DEF-003?** In test mode `exp` was computed from `FIXED_NOW` (2026-11-10 09:30Z) but verified against the real clock, so all tokens were rejected after that moment. The fix checks expiry against the injected clock; a unit test fails on the old code.
22. **What did the API suite find?** DEF-004: `GET /checkout/slots` answered without a token although the spec says CUSTOMER. DEF-005 was found by code reading and confirmed through the API: a name or phone with a trailing newline was accepted.
23. **How did you verify the fixes?** Each defect has a regression test that fails on the old code (DEF-003 test, `test_input_validation.py`: 9 of 12 fail on the old code) and a green Newman request.

## Limits and extensions

24. **What is not covered?** Performance and security testing, real payment, a second browser, and the WebSocket in automation (checked by hand and in a screenshot). Roles and contribution numbers per member depend on the GitHub history.
25. **What would mutation testing add?** It changes the code (for example `>=` to `>` in `compute_delivery_fee`) and checks that a test fails. Surviving mutants point at weak assertions that line coverage cannot reveal. It was not run here; `mutmut` scoped to `pricing_service.py` is the next step.
