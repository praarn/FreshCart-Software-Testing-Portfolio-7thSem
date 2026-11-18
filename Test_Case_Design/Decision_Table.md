# Decision Tables

## 1. Coupon eligibility (R4.1, R4.2)

Implemented by `pricing_service.validate_coupon`. Conditions are evaluated in the order
listed; the first failing condition decides the message, so later conditions are "don't care"
(`-`) once an earlier one fails.

Conditions: C1 code exists and is active; C2 not expired; C3 subtotal >= coupon minimum;
C4 first-order rule satisfied (always true if the coupon is not first-order-only);
C5 today is an allowed weekday (always true if the coupon has no weekday limit).

| Rule | C1 | C2 | C3 | C4 | C5 | Outcome | Message | TC |
|---|---|---|---|---|---|---|---|---|
| D1 | N | - | - | - | - | Reject | "'X' is not a valid coupon code." | TC-M4-007, TC-M8-006 (disabled) |
| D2 | Y | N | - | - | - | Reject | "Coupon 'OLD20' has expired." | TC-M4-006 |
| D3 | Y | Y | N | - | - | Reject | "requires a minimum order value of N" | TC-M4-003 |
| D4 | Y | Y | Y | N | - | Reject | "valid for first-time orders only" | TC-M4-004 |
| D5 | Y | Y | Y | Y | N | Reject | "only valid Monday to Friday" | TC-M4-015 |
| D6 | Y | Y | Y | Y | Y | Apply, discount computed | none | TC-M4-001, TC-M4-005, TC-M4-008 |
| D7 | Y | Y | N | N | - | Reject with the D3 message (precedence) | minimum order value | TC-M4-016 |

Discount when applied (`compute_discount`): FLAT = value; PERCENT = subtotal x value / 100;
then capped by `max_discount` and by the subtotal, rounded half-up to 2 dp (TC-M4-002 cap,
TC-M4-012 rounding). A second coupon replaces the first (TC-M4-009).

Coverage of the table: 7 of 7 rules have a case. D5 and D7 need a controllable clock or
a specific customer state and are verified at unit level.

## 2. Payment validity (R5.3)

| Rule | Method | Total <= 5000 | UPI format ok | Card not declined | Luhn ok | Expiry ok | Outcome | TC |
|---|---|---|---|---|---|---|---|---|
| P1 | COD | Y | - | - | - | - | Accept | TC-M5-001, TC-M5-016 |
| P2 | COD | N | - | - | - | - | Reject (limit) | TC-M5-007 |
| P3 | UPI | - | Y | - | - | - | Accept | TC-M5-017 |
| P4 | UPI | - | N | - | - | - | Reject | TC-M5-008 |
| P5 | CARD | - | - | N | - | - | Reject (declined) | TC-M5-010 |
| P6 | CARD | - | - | Y | N | - | Reject (invalid number) | TC-M5-018 |
| P7 | CARD | - | - | Y | Y | N | Reject (expired) | TC-M5-011 |
| P8 | CARD | - | - | Y | Y | Y | Accept | TC-M5-009 |

UPI format is checked by the request schema before `_validate_payment` runs, so P4 returns
422 at the API and an inline error in the UI.
