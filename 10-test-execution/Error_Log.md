# Error Log: CI failures of 2026-11-23

Record of the errors encountered on `main` between commits `ce8d59b` and `4f33b02`. The three GitHub Actions
runs of that period (`45112869263`, `45113150082`, `45113337506`) failed in two jobs. The cause was a
regression, not a flaky test: the code of two earlier defect fixes had been backed out of the application.
The errors are logged here only for the record. The code is restored and the suites pass again, so the
reports elsewhere in the portfolio describe the passing state.

## Summary

| # | Job | Step | Error | Defect | Cause | Resolution |
|---|---|---|---|---|---|---|
| E-1 | Backend (smoke, unit tests with coverage) | Unit tests with statement and branch coverage | 9 of 136 unit tests failed: `Failed: DID NOT RAISE ValidationError` in `tests/unit/test_input_validation.py` (lines 22, 28, 39) | DEF-005 | The validation regexes in `app/schemas/user.py` and `app/schemas/order.py` were anchored with `$` and had no `re.ASCII`, so a trailing newline and non-ASCII digits were accepted | Restored `\Z` anchors and `re.ASCII` (fix `611d7f4`) |
| E-2 | Backend (smoke, unit tests with coverage) | Start API and health-check | Skipped because E-1 stopped the job | DEF-005 | Knock-on of E-1 | Passes once E-1 is fixed |
| E-3 | API tests (Newman) | Run the Postman collection | `[API-CHK] Slots without a token` expected 401, got 200 (2 assertions) | DEF-004 | `GET /checkout/slots` in `app/routers/checkout.py` had lost `user=Depends(require_customer)` | Restored the dependency (fix `0c58076`) |
| E-4 | API tests (Newman) | Run the Postman collection | The three `[DEF-005]` requests (name, phone, pincode with a trailing newline) returned 201/200 instead of 422 (6 assertions) | DEF-005 | Same regexes as E-1 | Same as E-1 |
| E-5 | API tests (Newman) | Run the Postman collection | 15 further assertions failed in the M5 and M6 requests (card checks, UPI checkout, stock, cancellation) | DEF-005 | Knock-on: the pincode request with a trailing newline placed an order, which emptied the cart the later requests use | Same as E-1 |

Totals of the failing run: 9 unit tests failed (127 passed); 23 Newman assertions failed in 15 requests
(8 direct, 15 knock-on). The Black-box and Frontend build jobs passed.

## Failing unit tests (E-1)

```
FAILED test_register_rejects_trailing_newline_and_non_ascii_digits[name-Jane Doe\n]
FAILED test_register_rejects_trailing_newline_and_non_ascii_digits[phone-9876543210\n]
FAILED test_register_rejects_trailing_newline_and_non_ascii_digits[phone-9\u0968\u0969456789\u0966]
FAILED test_pincode_rejects_non_exact_six_ascii_digits[560050\n]
FAILED test_pincode_rejects_non_exact_six_ascii_digits[\u096b\u096c\u0966\u0966\u096b\u0966]
FAILED test_payment_fields_reject_trailing_newline[kw0..kw3]   (4 cases)
================== 9 failed, 127 passed, 4 warnings in 13.26s ==================
```

## Resolution

The code changes of `ce8d59b` were reverted (`checkout.py`, `order.py`, `user.py`), and the reports, evidence
screenshots, slides and PDF that recorded the failing run were restored to the passing results. After the
revert the application code is identical to commit `7986798`, whose CI run passed all four jobs.
DEF-004 and DEF-005 are Fixed again. See [`../9-defect-reports/`](../9-defect-reports/).
