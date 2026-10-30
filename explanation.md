# Software-Testing-Portfolio — what's in this repo

This repo has two kinds of content: **FreshCart**, a working grocery-delivery application
(the thing being tested), and a set of numbered folders that hold the **testing
deliverables** produced against it. This file is a map; for run commands see
[`commands.md`](commands.md), and for FreshCart's own architecture see
[`00_Application/explanation.md`](00_Application/explanation.md).

## Layout

```
00_Application/    FreshCart itself — backend (FastAPI) + frontend (Next.js)
01_Test_Plan/       Scope, strategy, schedule, resources
02_Test_Case_Design/ Test case specifications, traceability matrix
03_Test_Execution/   Test run logs and records
04_Defect_Reports/   Logged defects found during testing
05_Test_Automation/  Automated test scripts (e.g. Selenium) — the student's deliverable
06_Test_Reports/     Summary reports and metrics
07_Screenshots/      Screenshots captured during manual/automated testing
.github/workflows/   CI: installs deps, migrates, seeds, smoke-tests the API, builds the frontend
docker-compose.yml   Postgres + backend + frontend, for a from-scratch environment
```

`00_Application/docs/REQUIREMENTS.md` is the authoritative list of every business rule (by
ID), every frontend route, and every REST/WebSocket endpoint — that's the document to work
from when writing test cases in `02_Test_Case_Design/`.

## Why FreshCart looks the way it does

The application was built to an initial fixed specification (tech stack, business rules
R1.1-R8.5, Selenium-friendly `id`/`data-testid` conventions — see
`00_Application/docs/REQUIREMENTS.md`), then extended twice at the project owner's request:

1. **Wishlist, promotional banners, and a public "special offers" section** (rules
   `R9.1`-`R9.3`) — inspired by a reference grocery app, but built as ordinary FreshCart
   modules on the existing stack, not ported from that app's different tech stack.
2. **Visual redesign**, twice — first toward that reference app's bold quick-commerce look,
   then deliberately toned down (flatter cards, structured buttons, no emoji — real SVG
   icons instead) after it read as too playful for a professional app. See
   [`00_Application/frontend/explanation.md`](00_Application/frontend/explanation.md) for
   what that settled on.

None of this changed the original business rules or the API's auth/role model — it's purely
additive (new endpoints, new pages) and cosmetic.

## For testers

- Seed credentials, test-mode env vars (`APP_ENV=test`, `FIXED_NOW=...`), and the
  `POST /api/test/reset` endpoint are documented in
  [`00_Application/README.md`](00_Application/README.md) — use them to get a known,
  repeatable starting state before a test run.
- Swagger UI (`/docs` on the running backend) has request/response examples for every
  endpoint and is the fastest way to confirm an API contract before automating against it.
