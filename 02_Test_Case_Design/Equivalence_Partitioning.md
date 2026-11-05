# Equivalence Partitioning

Each input domain is split into classes the application should treat identically. One
representative per class is enough. Rule IDs are from
[`REQUIREMENTS.md`](../00_Application/docs/REQUIREMENTS.md); TC IDs from
[`Test_Cases.csv`](Test_Cases.csv). Boundaries inside these classes are in
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
| EP5 no letter | Invalid | `12345678` | 422 | not designed (gap, low risk: symmetric with EP4) |

## Phone (R1.4): 10 digits, first digit 6-9

| Class | Kind | Representative | Expected | TC |
|---|---|---|---|---|
| EP1 10 digits, first 6-9 | Valid | `9123456780` | 201 | TC-M1-001 |
| EP2 10 digits, first 0-5 | Invalid | `5123456789` | 422 | TC-M1-010 |
| EP3 fewer than 10 digits | Invalid | `912345678` | 422 | TC-M1-011 |
| EP4 non-digits | Invalid | `91234abcde` | 422 | not designed (gap) |

## Pincode (R5.1): 6 digits, serviceable 560001-560100

| Class | Kind | Representative | Expected | TC |
|---|---|---|---|---|
| EP1 serviceable range | Valid | `560050` | 201 | TC-M5-001 |
| EP2 6 digits, outside range (above) | Invalid | `560101` | 400 "Delivery not available" | TC-M5-002 |
| EP3 6 digits, outside range (below) | Invalid | `560000` | 400 | not designed |
| EP4 not 6 digits | Invalid | `5600` | 422 | not designed (gap) |

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

## Summary

6 domains, 29 classes (valid + invalid). 25 map to a test case; 4 do not (marked "not designed"): password without a letter, phone with non-digits, pincode below range, pincode of the wrong length. The first three are symmetric with a tested class; the wrong-length pincode is a genuine gap that the Pydantic schema is expected to reject with 422.
