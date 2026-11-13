# Requirements Analysis

Input: [`REQUIREMENTS.md`](../00_Application/docs/REQUIREMENTS.md) (42 rules, R1.1-R9.3, 9 modules).
Method: each rule was checked for testability (a single observable pass/fail outcome), then
compared with the running code to find points where the written rule leaves room for two
readings. Behaviour quoted below was observed in the code or the API, not assumed.

## 1. Testability summary

| Module | Rules | Directly testable | Needs a test hook | Ambiguous (see section 2) |
|---|---|---|---|---|
| M1 Auth | 8 | R1.1-R1.4, R1.6, R1.8 | R1.5 (clock), R1.7 (rate window) | R1.5 |
| M2 Catalog | 4 | R2.1-R2.4 | | |
| M3 Cart | 5 | R3.2-R3.5 | | R3.1 |
| M4 Pricing | 4 | R4.1-R4.4 | R4.1 FRESH15 weekday (clock) | R4.3 |
| M5 Checkout | 5 | R5.1, R5.4, R5.5 | R5.2 (clock) | R5.2, R5.3 |
| M6 Orders | 7 | R6.1-R6.6 | R6.7 (WebSocket) | R6.2 |
| M7 Reviews | 1 | R7.1 | | |
| M8 Admin | 5 | R8.1-R8.5 | | |
| M9 Extras | 3 | R9.1-R9.3 | | |

Test hooks that exist: `APP_ENV=test` mounts `POST /api/test/reset`; `FIXED_NOW` freezes the
business clock; every UI element has a `data-testid`.

## 2. Ambiguities and how they were resolved

| Rule | Question | Observed behaviour (used as the oracle) | Test |
|---|---|---|---|
| R1.5 | Is the 5th failed login answered as "invalid" or "locked"? Does a lock set by an admin expire? | 5th failure returns 401 "Invalid email or password" and sets LOCKED; later attempts get the locked message. Admin lock has no expiry. | TC-M1-014, TC-M1-020 |
| R3.1 / R3.3 | Which status for a quantity above 10? | New line, qty 11: 422 (schema). Re-add pushing a line above 10: 400. `REQUIREMENTS.md` lists 400 for both. | TC-M3-012, TC-M3-005 |
| R4.3 | "post-discount subtotal": is it the subtotal minus the coupon? | Yes. Fee is computed on subtotal minus discount. | TC-M4-010/011/013/014 |
| R5.2 | Is "at least 2 hours from now" inclusive? Do cancelled orders use up slot capacity? | Inclusive (slot exactly now + 2 h is accepted). Cancelled orders do not count. | `test_checkout_service.py` slot tests |
| R5.3 | "future MM/YY expiry": is the current month valid? | Current month is valid (11/26 accepted in Nov 2026), previous month is rejected. | `test_card_valid_in_current_month`, TC-M5-011 |
| R6.2 | Can an admin cancel? | Yes, `POST /admin/orders/{id}/cancel` uses the same state rule as the customer. Not in the rule text. | not separately tested |
| R6.4 | Status of the 3rd wrong OTP? | 1st and 2nd: 400 with attempts remaining. 3rd: 409. | TC-M6-009 |
| R1.2 | Where is case-insensitive uniqueness enforced? | Email is trimmed and lower-cased by the request schema, so the stored value is always lower case. | TC-M1-004 |

## 3. Assumptions

- A single backend process. The rate limiter and WebSocket manager are in memory.
- The clock is injected. Without `FIXED_NOW` the slot and weekday cases depend on the day the suite runs.
- Payment is mocked; no gateway is contacted.
- Seeded prices are multiples of 5 (so exactly 299.00 is not reachable in the UI).
- Chrome is the only browser under test.

## 4. Risks (product)

| Risk | Rules | Why it matters | Mitigation in the suite |
|---|---|---|---|
| Money rounding and discount caps | R4.1, R4.4 | Wrong totals reach customers | Unit tests on `compute_discount`, `round2`; UI and API assertions on totals |
| Stock consistency at checkout | R5.4, R5.5 | Oversell or partial commit | TC-M5-012, TC-M5-015 (API stock race) |
| Order state machine | R6.1-R6.4 | Illegal moves skip steps (for example delivery without OTP) | 36-pair unit matrix, 8 invalid transitions in the API suite |
| Role checks | R1.6 | Data exposure | 401/403 checks in every API folder |
| Account lockout | R1.5 | Lockout bypass or permanent lockout | Unit tests for 14:59 / 15:00 boundary, API 4-then-success |
| Input validation | R1.1-R1.4, R5.1 | Malformed data stored | EP and BVA cases, see `02_Test_Case_Design/` |

## 5. Test conditions derived per module

| Module | Conditions | Technique | Where |
|---|---|---|---|
| M1 | name, email, password, phone classes and bounds; failed-login count 4/5; lock expiry 14:59/15:00; token expiry; logout | EP, BVA, state transition | `Equivalence_Partitioning.md`, `Boundary_Value_Analysis.md`, `State_Transition.md` |
| M2 | search, filter, sort, page size, hidden inactive, out-of-stock | EP | Test_Cases.csv |
| M3 | quantity 0/1/10/11, stock edge, distinct items 20/21, re-add | BVA | `Boundary_Value_Analysis.md` |
| M4 | coupon x (known, active, expiry, minimum, first order, weekday); fee at 298.99/299.00; discount cap | Decision table, BVA | `Decision_Table.md` |
| M5 | pincode range, slot lead/window/capacity, payment method x validity | EP, BVA, decision table | `Decision_Table.md` |
| M6 | all (state, event) pairs; OTP attempts 2/3 | State transition | `State_Transition.md` |
| M7 | delivered-only, one review per product, rating 1-5, comment 300 | EP, BVA | Test_Cases.csv |
| M8, M9 | CRUD, filters, role access | EP, error guessing | Test_Cases.csv, `09_API_Testing/` |
