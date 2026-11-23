**Defect ID:** DEF-004
**Title:** `GET /api/checkout/slots` is reachable without authentication
**Reported by:** QA (API test suite, `7-api-testing`)
**Date found:** 2026-11-13
**Found via:** Newman request "[API-CHK] Slots without a token" (expected 401, got 200)
**Module:** M5 Checkout
**Rule ID(s) affected:** R1.6 (customer endpoints need a valid token), R5.2
**Severity:** Low (information disclosure: slot occupancy)
**Priority:** P3
**Environment:** `APP_ENV=test FIXED_NOW=2026-11-10T09:00:00`

## Summary

`REQUIREMENTS.md` lists `GET /checkout/slots` as `CUSTOMER` only. The route has no auth dependency, so an
anonymous caller receives every slot with its remaining capacity.

## Steps to reproduce

`curl -i http://localhost:8001/api/checkout/slots` with no `Authorization` header.

## Expected result

401 `{"status":401,"error":"UNAUTHORIZED",...}`.

## Actual result

200 with the slot list (`slot_start`, `slot_end`, `available`, `remaining_capacity`).

## Root cause

`routers/checkout.py::list_slots` declares `db` and `now` dependencies only. `place_order`, on the same
router, declares `require_customer`.

## Fix

Proposed (and previously applied in `0c58076`): add `user=Depends(require_customer)` to `list_slots`. The only client is `/checkout` in the frontend, which is
behind `RoleGuard` for CUSTOMER and already sends the token. Verified by the Newman request above (401
without a token, 200 for a customer).

## Status

Open. Reopened on 2026-11-23 for the demo: the fix commit (`0c58076`) was backed out of the application code so the regression checks fail on purpose and the defect workflow can be shown. Re-applying that commit's code change closes it.

## Verification evidence

- Failing check: Newman request `[API-CHK] Slots without a token` (expected 401, got 200; 2 assertions fail), run of 2026-11-23.
- Run report: [`newman_report.html`](../7-api-testing/reports/newman_report.html) (23 assertions failed in the run, 2 of them for this defect)
- Screenshot: ![DEF-004 evidence](../11-evidence/screenshots/16_newman_html_report.png)
