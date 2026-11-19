# Equivalence Partitioning

Each input domain is split into classes the application should treat identically. One
representative per class is enough. Rule IDs are from
[`REQUIREMENTS.md`](../application/docs/REQUIREMENTS.md); TC IDs from
[`Test_Cases.csv`](../test-cases/Test_Cases.csv). Boundaries inside these classes are in
[`Boundary_Value_Analysis.md`](Boundary_Value_Analysis.md).

## Name (R1.1): 2-50 chars, letters and spaces

| Class | Kind | Representative | Expected | TC |
|---|---|---|---|---|
| EP1 length 2-50, letters/spaces | Valid | `Jane Doe` | 201 | TC-M1-001 |
| EP2 length < 2 | Invalid | `A` | 422 | TC-M1-002 |
| EP3 length > 50 | Invalid | 51 letters | 422 | TC-M1-022 |
| EP4 contains digits/symbols | Invalid | `Jane2` | 422 | TC-M1-003 |

## Email (R1.2): valid format, unique case-insensitive, max 100

| Class | Kind | Representative | Expected | TC |
|---|---|---|---|---|
| EP1 well-formed, unused | Valid | `new.user@freshcart.test` | 201 | TC-M1-001 |
| EP2 malformed | Invalid | `not-an-email` | 422 | TC-M1-005 |
| EP3 already registered (any case) | Invalid | `CUSTOMER2@FRESHCART.TEST` | 409 | TC-M1-004 |
| EP4 longer than 100 | Invalid | 101-char email | 422 | TC-M1-025 |

## Password (R1.3): 8-20 chars, at least one letter and one digit

| Class | Kind | Representative | Expected | TC |
|---|---|---|---|---|
| EP1 length 8-20, letter + digit | Valid | `Pasw0rd1` | 201 | TC-M1-007 |
| EP2 too short | Invalid | `Pas1abc` (7) | 422 | TC-M1-006 |
| EP3 too long | Invalid | 21 chars | 422 | TC-M1-008 |
| EP4 no digit | Invalid | `Passwordonly` | 422 | TC-M1-009 |
| EP5 no letter | Invalid | `12345678` | 422 | TC-M1-029 (black-box suite) |

## Phone (R1.4): 10 digits, first digit 6-9

| Class | Kind | Representative | Expected | TC |
|---|---|---|---|---|
| EP1 10 digits, first 6-9 | Valid | `9123456780` | 201 | TC-M1-001 |
| EP2 10 digits, first 0-5 | Invalid | `5123456789` | 422 | TC-M1-010 |
| EP3 fewer than 10 digits | Invalid | `912345678` | 422 | TC-M1-011 |
| EP4 non-digits | Invalid | `91234abcde` | 422 | TC-M1-030 (black-box suite) |

## Pincode (R5.1): 6 digits, serviceable 560001-560100

| Class | Kind | Representative | Expected | TC |
|---|---|---|---|---|
| EP1 serviceable range | Valid | `560050` | 201 | TC-M5-001 |
| EP2 6 digits, outside range (above) | Invalid | `560101` | 400 "Delivery not available" | TC-M5-002 |
| EP3 6 digits, outside range (below) | Invalid | `560000` | 400 | TC-M5-019 (black-box suite) |
| EP4 not 6 digits | Invalid | `5600` | 422 | TC-M5-019 (black-box suite) |

## Payment method (R5.3)

| Class | Kind | Representative | Expected | TC |
|---|---|---|---|---|
| COD, total <= 5000 | Valid | total 220 | 201 | TC-M5-001 |
| COD, total > 5000 | Invalid | total 6000 | 400 | TC-M5-007 |
| UPI, `name@bank` | Valid | `jane@okbank` | 201 | TC-M5-017 |
| UPI, bad format | Invalid | `notanupi` | 400/422 | TC-M5-008 |
| CARD, Luhn-valid, future expiry | Valid | `4111111111111111`, 12/30, 123 | 201 | TC-M5-009 |
| CARD, always-declined number | Invalid | `4000000000000002` | 400 declined | TC-M5-010 |
| CARD, expired | Invalid | 01/20 | 400 | TC-M5-011 |
| CARD, Luhn-invalid number | Invalid | `4111111111111112` | 400 "Invalid card number" | TC-M5-018 |

## Executed as a suite

Equivalence partitioning is one of the two black-box methods of the portfolio. The classes above are the ones the
UI and API suites touch; [`black-box-testing/`](../black-box-testing/README.md) runs **every** class, plus the
classes added there, as one parametrized pytest case per class, with the class number in the test id (for example
`TC-M1-029-EP5-no-letter`). Case IDs by domain:

| Domain | Rule | Black-box suite case |
|---|---|---|
| Name, email, password, phone | R1.1-R1.4 | TC-M1-027, TC-M1-028, TC-M1-029, TC-M1-030 |
| Login credentials, caller role and token | R1.5, R1.6 | TC-M1-031, TC-M1-032 |
| Catalog search, filter, sort, visibility | R2.3, R2.4 | TC-M2-008, TC-M2-009 |
| Cart quantity and item operations | R3.1, R3.4 | TC-M3-013 |
| Coupon classes | R4.1, R4.2 | TC-M4-017 |
| Pincode, delivery slot, payment, checkout effects | R5.1-R5.5 | TC-M5-019, TC-M5-022, TC-M5-024, TC-M5-027 |
| Delivery OTP | R6.4 | TC-M6-018 |
| Review eligibility | R7.1 | TC-M7-005 |
| Product fields | R2.2, R8.1 | TC-M8-014 |
| Wishlist, banners and offers | R9.1-R9.3 | TC-M9-007, TC-M9-008 |

## Summary

6 domains in the original analysis, 29 classes; all 29 now map to a test case (the four that were gaps are closed by
TC-M1-029, TC-M1-030 and TC-M5-019). The suite adds classes for login, roles, catalog, cart, coupons, slots, OTP,
reviews, product fields, wishlist and banners: 83 parametrized classes carry an `EP<n>` number in their test id, and further classes are checked by tests that run several steps in one case.
