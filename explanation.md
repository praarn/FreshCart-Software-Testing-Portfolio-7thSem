# Software-Testing-Portfolio — what's in this repo

This repo has two kinds of content: **FreshCart**, a working grocery-delivery application
(the thing being tested), and a set of numbered folders that hold the **testing
deliverables** produced against it. This file is a map; for run commands see
[`commands.md`](commands.md), and for FreshCart's own architecture see
[`0. application/explanation.md`](0.%20application/explanation.md).

## Layout

```
"0. application/"            FreshCart itself: backend (FastAPI) + frontend (Next.js)
"1. introduction/"           "1. Introduction" to the application
"2. requirements/"           "2. Requirements" analysis
"3. test-plan/"              "3. Scope", strategy, schedule, resources
"4. test-cases/"             "4. Test" scenarios and cases, traceability matrix
"5. black-box-testing/"      "5. EP", BVA, decision table, state transition, plus the executable suite
"6. white-box-testing/"      "6. CFGs", basis path testing, statement/branch/condition coverage
"7. api-testing/"            "7. Postman" collection, Newman reports
"8. automation-testing/"     "8. Selenium" + pytest suite
"9. defect-reports/"         "9. Logged" defects
"10. test-execution/"         "10. Run" logs and actual results
"11. evidence/"               "11. screenshots/" and videos/
"12. final-test-report/"      "12. Summary" report, metrics, conclusion
"13. reflections/"            "13. Individual" contribution and reflection
"14. tools/"                  Consistency check, coverage and screenshot helpers
.github/workflows/      CI
docker-compose.yml      Postgres + backend + frontend
```

`0. application/docs/REQUIREMENTS.md` is the authoritative list of every business rule (by
ID), every frontend route, and every REST/WebSocket endpoint — that's the document to work
from when writing test cases in `4. test-cases/`.

## Why FreshCart looks the way it does

The application was built to an initial fixed specification (tech stack, business rules
R1.1-R8.5, Selenium-friendly `id`/`data-testid` conventions — see
`0. application/docs/REQUIREMENTS.md`), then extended twice at the project owner's request:

1. **Wishlist, promotional banners, and a public "special offers" section** (rules
   `R9.1`-`R9.3`) — inspired by a reference grocery app, but built as ordinary FreshCart
   modules on the existing stack, not ported from that app's different tech stack.
2. **Visual redesign**, twice — first toward that reference app's bold quick-commerce look,
   then deliberately toned down (flatter cards, structured buttons, no emoji — real SVG
   icons instead) after it read as too playful for a professional app. See
   [`0. application/frontend/explanation.md`](0.%20application/frontend/explanation.md) for
   what that settled on.

None of this changed the original business rules or the API's auth/role model — it's purely
additive (new endpoints, new pages) and cosmetic.

## For testers

- Seed credentials, test-mode env vars (`APP_ENV=test`, `FIXED_NOW=...`), and the
  `POST /api/test/reset` endpoint are documented in
  [`0. application/README.md`](0.%20application/README.md) — use them to get a known,
  repeatable starting state before a test run.
- Swagger UI (`/docs` on the running backend) has request/response examples for every
  endpoint and is the fastest way to confirm an API contract before automating against it.
