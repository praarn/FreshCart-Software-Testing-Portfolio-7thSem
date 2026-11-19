# The 9 formerly manual cases: execution results

In the first run these nine cases (`Automated = N`) were never executed. They are now executed by code that
exercises the real application, so their `Automated` value in `Test_Cases.csv` is `A` (Newman request) or `U` (pytest unit
test). Actual results below are taken from the Newman JSON report
([`../api-testing/reports/newman_report.json`](../api-testing/reports/newman_report.json)) and the unit test run.

| TC ID | Rule | Executed as | Expected | Actual | Status |
|---|---|---|---|---|---|
| TC-M1-015 | R1.5 | Unit: `test_success_resets_counter` | 3 failures, 1 success, 3 failures: not locked | after the sequence `status = ACTIVE`, `failed_login_count = 3` | Pass |
| TC-M1-018 | R1.7 | Newman folder 10: 10 rapid logins, then an 11th | 11th is 429 with `Retry-After` | 429 `RATE_LIMITED`, `Retry-After: 58` | Pass |
| TC-M3-003 | R3.2 | Newman: 20 distinct items added, then a 21st | 400, 20-item message | 400 "Cart can contain at most 20 distinct items." | Pass |
| TC-M4-009 | R4.2 | Newman: apply `FRESH15` while `WELCOME10` applied | Only the second coupon's discount | `coupon_code FRESH15`, discount 135.00, total 765.00 on 900.00 | Pass |
| TC-M4-012 | R4.4 | Unit: `test_percent_discount_rounds_half_up`, `test_round2_half_up` | Half-cent rounds up | 10% of 0.05 gives 0.01; 2.675 gives 2.68 | Pass |
| TC-M5-005 | R5.2 | Newman: slot on 2026-11-14 with the clock at 2026-11-10 09:00 | 400, not within 3 days | 400 "Delivery slot must be within the next 3 days." | Pass |
| TC-M5-015 | R5.5 | Newman: stock of a carted item set to 0, then checkout | 409 naming the item, nothing committed | 409 "'Race Item' is no longer available in the requested quantity."; cart still holds the item | Pass |
| TC-M6-002 | R6.1 | Newman: admin sets a DELIVERED order to CONFIRMED | 409 | 409 "Cannot move order from DELIVERED to CONFIRMED." | Pass |
| TC-M7-004 | R7.1 | Newman: review comment of 301 characters | 422 on `comment` | 422 field error "String should have at most 300 characters" | Pass |

None of the nine could be built in the UI without extra tooling (the rate limit window, 21 distinct items, a stock race
between two sessions, a clock-dependent slot), which is why they use the API layer.
