# 5 - Black-Box Testing

Black-box testing treats FreshCart as a closed box: every test sends HTTP requests to the running API and checks
the status code and response body against the rules in
[`REQUIREMENTS.md`](../0.%20application/docs/REQUIREMENTS.md). Nothing here imports application code or looks at the
database. Two methods are used, each run as a data-driven pytest suite:

| Method | Idea | Suite | Cases |
|---|---|---|---|
| 1. Equivalence partitioning (EP) | Split each input into classes the application should treat alike; send one representative per valid and invalid class | `tests/test_ep_*.py` | 19 cases (`Black-box EP` in the CSV) |
| 2. Boundary value analysis (BVA) | Probe each limit at min-1, min, min+1, max-1, max, max+1 | `tests/test_bva_*.py` | 26 cases (`Black-box BVA` in the CSV) |

Together: 45 cases, 288 parametrized tests (one per class or boundary value), covering all of modules M1-M9.
Results: [`Black_Box_Results.md`](Black_Box_Results.md). The white-box counterpart (basis path testing and
statement/branch/condition coverage) is in [`../6. white-box-testing/`](../6.%20white-box-testing/README.md).

## How it relates to the other suites

The Selenium and Newman suites are black-box too, but they are organised by feature and user flow. This suite is
organised by technique, so each rule's classes and boundaries are visible and each one is a separate test id. It
also reaches values the UI cannot: exact money amounts (298.99, 299.00, 5000.01) are built by creating a product at
that price through the admin API, and the clock is frozen, so slot lead time and window edges are exact.

| Design document | Executed here |
|---|---|
| [`Equivalence_Partitioning.md`](../5.%20black-box-testing/Equivalence_Partitioning.md) | every class, including the four that had no case before (password without a letter, phone with non-digits, pincode below the range, pincode of the wrong length) |
| [`Boundary_Value_Analysis.md`](../5.%20black-box-testing/Boundary_Value_Analysis.md) | every limit on both sides; the old R4.3 reachability note no longer applies |

Decision tables and state transition testing stay as supporting design techniques
([`Decision_Table.md`](../5.%20black-box-testing/Decision_Table.md), [`State_Transition.md`](../5.%20black-box-testing/State_Transition.md));
the Newman suite executes them.

## Test case map

Case IDs are rows in [`Test_Cases.csv`](../4.%20test-cases/Test_Cases.csv) with `Automated = B`. Every pytest id
starts with its case ID and ends with the class or boundary position, for example
`test_password_length[TC-M1-035-len21-max+1]` or `test_card_boundaries[TC-M5-026-expiry-10/26-month-before-now]`.

| Module | Equivalence partitioning | Boundary value analysis |
|---|---|---|
| M1 registration, login, roles | TC-M1-027 name, 028 email, 029 password, 030 phone, 031 login, 032 role and token | TC-M1-033 name, 034 email, 035 password, 036 phone, 037 lockout threshold |
| M2 catalog | TC-M2-008 search, filter, sort; 009 visibility | TC-M2-010 pagination |
| M3 cart | TC-M3-013 quantity and item classes | TC-M3-014 quantity, 015 stock, 016 re-add, 017 distinct items |
| M4 coupons and pricing | TC-M4-017 coupon classes | TC-M4-018 minimums, 019 discount cap, 020 delivery fee, 021 fee after discount and rounding |
| M5 checkout | TC-M5-019 pincode, 022 slot, 024 payment, 027 preconditions and effects | TC-M5-020 pincode range, 021 address lengths, 023 slot lead, window, capacity, 025 COD limit, 026 card number, CVV, expiry |
| M6 delivery | TC-M6-018 OTP | TC-M6-019 OTP attempts |
| M7 reviews | TC-M7-005 eligibility | TC-M7-006 rating, 007 comment length |
| M8 admin | TC-M8-014 product field classes | TC-M8-011 name, 012 price, 013 stock |
| M9 wishlist, banners, offers | TC-M9-007 wishlist, 008 banners and offers | TC-M9-009 banner field lengths |

## Run it

The backend must run in test mode with the frozen clock (a Tuesday; the weekday coupon and the slot edges depend on it):

```bash
# terminal 1
cd "0. application/backend"
APP_ENV=test FIXED_NOW=2026-11-10T09:00:00 uvicorn app.main:app --port 8000

# terminal 2
cd black-box-testing
pip install -r requirements.txt
pytest --junitxml=results/black_box_junit.xml
python make_results.py                  # rewrites Black_Box_Results.md from the JUnit file
```

About 3 minutes. `FRESHCART_API_URL` points the suite at another address (default `http://127.0.0.1:8000/api`;
the numeric address avoids a multi-second IPv6 fallback per request on Windows). CI runs it as the `black-box` job.

How the suite keeps itself repeatable: `POST /api/test/reset` before the run, before modules that place many orders
and around tests that change shared state (lockout, first-order status, slot capacity); products are created per
test with unique names; login and register calls reset the database every 8 requests so the 10 per minute rate limit
(R1.7) is never reached by accident.

## Files

| File | Purpose |
|---|---|
| `tests/test_ep_accounts.py`, `test_ep_shopping.py`, `test_ep_checkout.py` | Equivalence partitioning: M1; M2, M3, M4; M5, M6 |
| `tests/test_bva_accounts.py`, `test_bva_shopping.py`, `test_bva_checkout.py` | Boundary value analysis: M1; M2, M3, M4; M5, M6 |
| `tests/test_ep_bva_reviews_admin_extras.py` | Both methods for M7, M8, M9 (smaller modules) |
| `helpers.py`, `conftest.py` | HTTP helpers, fixtures, and the hook that ties each test to its case ID |
| `make_results.py` | Builds `Black_Box_Results.md` from the JUnit file |
| `results/` | `black_box_junit.xml` and `black_box_run.log` of the recorded run |

## Findings

The suite found no defect in the application: every class and boundary behaved as `REQUIREMENTS.md` specifies
(288 of 288 passed). While building it, one of its own tests was wrong and was corrected, not the application: the
wishlist list nests the product under `product`. Two environment points are handled in the code and documented above:
`localhost` on Windows stalls on an IPv6 fallback, and two copies of the suite must never share one backend (the
reset of one drops the tables under the other).

Limits of the method: black-box testing only sees what the API exposes. It cannot show that every branch ran (that is
what [`../6. white-box-testing/Coverage_Report.md`](../6.%20white-box-testing/Coverage_Report.md) measures), and some
edges cannot be hit exactly: no delivery slot starts exactly 2 hours after the frozen 09:00 clock (slots begin on
even hours, so 11:00 is not a slot), so the lead-time boundary is probed at 10:00 (1 h, rejected) and 12:00 (3 h,
accepted); the weekday rule of `FRESH15` is only checked on the frozen Tuesday (the Saturday rejection is a unit test).
