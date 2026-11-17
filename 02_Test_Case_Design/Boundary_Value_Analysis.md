# Boundary Value Analysis

Two-sided boundaries (min-1, min, max, max+1) for each numeric/length rule. "Level" is where
the case runs: UI (Selenium), API (Newman, `09_API_Testing/`), Unit (pytest,
`00_Application/backend/tests/unit/`).

| Rule | Boundary | Values | Expected | TC | Level |
|---|---|---|---|---|---|
| R1.1 name length | 2..50 | 1 | reject | TC-M1-002 | UI |
| | | 50 | accept | TC-M1-021 | API |
| | | 51 | reject | TC-M1-022 | API |
| R1.2 email length | max 100 | 101 | reject | TC-M1-025 | API |
| R1.3 password length | 8..20 | 7 | reject | TC-M1-006 | UI |
| | | 8 | accept | TC-M1-007 | UI |
| | | 20 | accept | TC-M1-023 | API |
| | | 21 | reject | TC-M1-008 | UI |
| R1.4 phone | 10 digits, first 6-9 | 9 digits | reject | TC-M1-011 | UI |
| | | first digit 5 | reject | TC-M1-010 | UI |
| | | first digit 6 | accept | TC-M1-024 | API |
| R1.5 failed logins | lock at 5 | 4 then success | not locked | TC-M1-026 | API |
| | | 5 | locked | TC-M1-014 | UI |
| R1.5 lock duration | 15 min | 14:59 / 15:00 | locked / active | TC-M1-020 | Unit |
| R3.1 quantity | 1..10 | 0 | reject | TC-M3-010 | API |
| | | 10 | accept | TC-M3-011 | API |
| | | 11 | reject | TC-M3-012 | API |
| R3.1 stock edge | qty vs stock | qty = stock+1 | reject | TC-M3-002 | UI |
| R3.3 re-add cap | 8 + 5 = 13 | reject, not clamped | TC-M3-005 | UI |
| R3.2 distinct items | max 20 | 21st item | reject | TC-M3-003 | API (was manual) |
| R4.3 delivery fee | 299.00 | 298.99 | 40.00 | TC-M4-013 | Unit |
| | | 299.00 | 0.00 | TC-M4-014 | Unit |
| | | 295.00 / 300.00 | 40.00 / 0.00 | TC-M4-011 / TC-M4-010 | UI |
| R4.1 WELCOME10 cap | 100 | subtotal 2000 | discount 100.00 | TC-M4-002 | UI |
| R5.1 pincode | 560001..560100 | 560101 | reject | TC-M5-002 | UI |
| R5.2 slot lead time | >= 2 h | 1 h ahead | reject | TC-M5-004 | UI |
| R5.2 slot window | <= 3 days | day 4 | reject | TC-M5-005 | API (was manual) |
| R5.2 slot capacity | 5 | 5 existing orders -> 6th | reject | TC-M5-006 | UI |
| R5.3 COD limit | 5000 | 5000.00 | accept | TC-M5-016 | Unit |
| | | > 5000 | reject | TC-M5-007 | UI |
| R7.1 comment length | 300 | 301 | reject | TC-M7-004 | API (was manual) |

## Note on R4.3 reachability

Every seeded product price is a multiple of 5 (see `Execution_Log.md`), so exactly 299.00 and
298.99 cannot be built in the UI. The UI cases use the nearest reachable values 295.00 and
300.00; the exact boundary is verified at unit level against `compute_delivery_fee`
(TC-M4-013/014).

## Executed as a suite

Boundary value analysis is the second black-box method of the portfolio. The table above lists the boundaries the UI,
API and unit suites already hit; [`11_Black_Box_Testing/`](../11_Black_Box_Testing/README.md) probes **every** limit on
both sides (min-1, min, min+1, max-1, max, max+1) as one parametrized pytest case per value, with the position in the
test id (for example `TC-M4-020-299.00-min`). Exact money values such as 298.99 or 5000.01 are reachable because the
suite creates products at any price through the admin API, which the UI cases could not do (see the note below).

| Limit | Rule | Black-box suite case |
|---|---|---|
| Name 2-50, email 100, password 8-20, phone 10 digits and first digit 6-9 | R1.1-R1.4 | TC-M1-033 to TC-M1-036 |
| 5 failed logins | R1.5 | TC-M1-037 |
| Page size 10, page 1 and last page | R2.3 | TC-M2-010 |
| Quantity 1-10, quantity vs stock, re-add cap, 20 distinct items | R3.1-R3.3 | TC-M3-014 to TC-M3-017 |
| Coupon minimums 200 / 500 / 800, discount caps 100 / 150, fee threshold 299.00, rounding | R4.1, R4.3, R4.4 | TC-M4-018 to TC-M4-021 |
| Pincode 560001-560100, address line 5-100, city 2-50 | R5.1 | TC-M5-020, TC-M5-021 |
| Slot lead time 2 h, window 3 days, capacity 5 | R5.2 | TC-M5-023 |
| COD limit 5000.00, card number, CVV, expiry month | R5.3 | TC-M5-025, TC-M5-026 |
| OTP attempts 3 | R6.4 | TC-M6-019 |
| Rating 1-5, comment 300 | R7.1 | TC-M7-006, TC-M7-007 |
| Product name 2-80, price 0.01-10000.00, stock 0-1000 | R2.2, R8.1 | TC-M8-011 to TC-M8-013 |
| Banner title 2-100, image URL 5-500 | R9.2 | TC-M9-009 |

The "R4.3 reachability" note above no longer limits the exact check: TC-M4-020 and TC-M4-021 run 298.99, 299.00 and
299.01 through the real cart API.
