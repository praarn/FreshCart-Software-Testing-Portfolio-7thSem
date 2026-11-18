# Basis Path Testing

For each function: V(G) computed three ways, the independent path set, and one test per path.
Graphs are in [`Control_Flow_Graphs/`](Control_Flow_Graphs/). Tests live in
`Application/backend/tests/unit/`.

| Function | Predicates | Nodes N | Edges E | E - N + 2 | Predicates + 1 | Regions | Feasible basis paths |
|---|---|---|---|---|---|---|---|
| `validate_coupon` | 9 | 16 | 24 | 10 | 10 | 10 | 10 |
| `_validate_payment` | 6 | 14 | 19 | 7 | 7 | 7 | 7 |
| `complete_delivery` | 6 | 13 | 18 | 7 | 7 | 7 | 6 (one infeasible) |

Predicates are counted per simple condition (`A or B` is two predicates). Counted per `if`
statement instead, `validate_coupon` would be 7; the condition-level figure is used because the
assignment asks for condition coverage.

## 1. `validate_coupon` (R4.1, R4.2): V(G) = 10

| # | Path (predicate outcomes) | Result | Test (`test_pricing_service.py`) | Input |
|---|---|---|---|---|
| 1 | P1=T | invalid code | `test_unknown_coupon_none` | coupon None |
| 2 | P1=F P2=T | invalid code | `test_disabled_coupon` | active=False |
| 3 | P1=F P2=F P3=T P4=T | expired | `test_expired_coupon` | expires 1 s before now |
| 4 | P1=F P2=F P3=F P5=T | below minimum | `test_below_minimum` | subtotal 199.99, min 200 |
| 5 | P1=F P2=F P3=T P4=F P5=F P6=F P8=F | return | `test_coupon_valid_at_expiry_instant` | expires == now |
| 6 | ... P3=F P5=F P6=T P7=T | first-order violation | `test_first_order_violation` | first_order_only, returning customer |
| 7 | ... P3=F P5=F P6=T P7=F P8=F | return | `test_first_order_coupon_for_first_order_customer` | first_order_only, first order |
| 8 | ... P3=F P5=F P6=F P8=T P9=T | weekday violation | `test_weekday_rejected_on_saturday` | weekdays 1-5, Saturday |
| 9 | ... P3=F P5=F P6=F P8=T P9=F | return | `test_weekday_accepted_on_tuesday` | weekdays 1-5, Tuesday |
| 10 | ... P3=F P5=F P6=F P8=F | return | `test_non_first_order_coupon_for_returning_customer` | no limits |

Paths 1-9 already cover all 18 edges; path 10 is linearly independent of them (it combines
the P3=F edge with the P5=F, P6=F, P8=F edges, which no single earlier path does).

## 2. `_validate_payment` (R5.3): V(G) = 7

| # | Path | Result | Test (`test_checkout_service.py`) | Input |
|---|---|---|---|---|
| 1 | Q1=T Q2=T | COD limit | `test_cod_over_limit_rejected` | COD, 5000.01 |
| 2 | Q1=T Q2=F | None | `test_cod_at_limit_accepted` | COD, 5000.00 |
| 3 | Q1=F Q3=T | UPI id | `test_upi_returns_reference` | UPI `jane@okbank` |
| 4 | Q1=F Q3=F Q4=T | declined | `test_card_declined` | 4000000000000002 |
| 5 | ... Q4=F Q5=T | invalid number | `test_card_fails_luhn` | 4111111111111112 |
| 6 | ... Q5=F Q6=T | expired | `test_card_expired_previous_month` | 10/26 at Nov 2026 |
| 7 | ... Q5=F Q6=F | masked card | `test_card_valid_in_current_month` | 11/26 at Nov 2026 |

## 3. `complete_delivery` (R6.4): V(G) = 7, 6 feasible

| # | Path | Result | Test (`test_order_service.py`) | Input |
|---|---|---|---|---|
| 1 | C1=T | 403 | `test_complete_delivery_wrong_partner` | other partner |
| 2 | C1=F C2=T | 409 status | `test_complete_delivery_wrong_status` | order PACKED |
| 3 | C1=F C2=F C3=T | 409 blocked | `test_complete_delivery_blocked_even_with_correct_otp` | otp_blocked, correct OTP |
| 4 | ... C3=F C4=F | DELIVERED | `test_complete_delivery_success` | correct OTP |
| 5 | ... C4=T C5=F C6=F | 400 attempts left | `test_complete_delivery_wrong_otp_attempts_remain` | wrong OTP, 1st and 2nd time |
| 6 | ... C4=T C5=T C6=T | 409 no attempts | `test_complete_delivery_third_wrong_otp_blocks` | wrong OTP, 3rd time |
| 7 | ... C4=T C5=T C6=F | infeasible | none | |

Finding: C6 re-tests `order.otp_blocked` straight after C5 may have set it. Because C3 was false on
entry, C6 is true exactly when C5 is true. The 7th basis path (and C5=F, C6=T) cannot execute.
This is not a bug, but the second check is redundant; replacing it with `if blocked_now` over the
C5 result, or merging the two blocks, would remove the dead branch.

## Statement, branch and condition coverage (these three functions)

Statement and branch figures are from the pytest-cov run in [`Coverage_Report.md`](Coverage_Report.md) (branches are
coverage.py arcs: two per `if`). The condition column is established by the path tables above, because coverage.py
does not measure condition coverage.

| Criterion | `validate_coupon` | `_validate_payment` | `complete_delivery` |
|---|---|---|---|
| Statement (tool) | 13 / 13 | 16 / 16 | 18 / 18 |
| Branch (tool) | 12 / 12 | 12 / 12 | 12 / 12 |
| Edges of the condition-level CFG | 18 / 18 | 12 / 12 | 12 / 12 (the infeasible item is a path, not an edge) |
| Simple conditions true and false (paths above) | 9 / 9 | 6 / 6 | 6 / 6 |
