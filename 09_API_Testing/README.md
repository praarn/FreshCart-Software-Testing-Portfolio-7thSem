# 09 - API Testing (Postman / Newman)

A Postman collection that exercises every endpoint group in `REQUIREMENTS.md` and is run
headless with Newman against the test-mode backend.

## Contents

| File | Purpose |
|---|---|
| `FreshCart.postman_collection.json` | The collection (11 folders, one per module, run in order) |
| `FreshCart.postman_environment.json` | `base_url` = `http://localhost:8000/api` |
| `build_collection.py` | Generates the collection and environment; edit this, not the JSON |
| `make_results.py` | Builds `API_Test_Results.md` from the Newman JSON report |
| [`API_Test_Results.md`](API_Test_Results.md) | One row per request: expected, actual, result, rule IDs |
| `reports/newman_report.html`, `reports/newman_report.json` | Raw Newman reports of the committed run |

## What each request asserts

- Status code (200/201/204 and 400/401/403/404/409/422/429).
- Response shape (required fields, no `password_hash`, pagination fields).
- For every error response: the contract `{status, error, message, field_errors}` with the right `error` name.
- Business values where the rule defines them (discount 36.00 = 10% of 360.00, fee 40.00 / 0.00, order number format `FC-20261110-NNNN`, 4-digit OTP).
- Role access: 401 without a token, 403 for the wrong role, 404 for unknown ids.

Tokens and ids are collection variables set by earlier requests (login requests store
`token_admin`, `token_c1`, `token_c2`, `token_driver1`, `token_driver2`). Requests depend on the
order of the folders; run the collection as a whole.

## Rate limiting

`/auth/login` and `/auth/register` allow 10 requests per minute per IP (R1.7) and the limiter is
in memory, so a full run needs to pace itself. A collection-level pre-request script counts these
calls and waits when 8 are in the window; the first request probes the limiter and waits out a
leftover window; folder 10 deliberately exceeds the limit to check the 429 and `Retry-After`.
This makes a run take about 6 minutes.

## Reproduce

```bash
# 1. backend in test mode
cd 00_Application/backend
APP_ENV=test FIXED_NOW=2026-11-10T09:00:00 uvicorn app.main:app --port 8000

# 2. Newman (Node 18+)
cd 09_API_Testing
npx newman run FreshCart.postman_collection.json -e FreshCart.postman_environment.json \
  -r cli,json,htmlextra --reporter-json-export reports/newman_report.json \
  --reporter-htmlextra-export reports/newman_report.html
python make_results.py reports/newman_report.json
```

`htmlextra` needs `npm i -g newman-reporter-htmlextra`. Postman can also import the collection and
environment directly.

## Defects found by this suite

| Defect | Request |
|---|---|
| DEF-004 | `[API-CHK] Slots without a token` |
| DEF-005 | `[DEF-005]` requests (trailing newline in name, phone, pincode) |
