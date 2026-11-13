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
