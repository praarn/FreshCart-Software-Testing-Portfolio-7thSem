# Test Plan — FreshCart

| | |
|---|---|
| Project | FreshCart — online grocery shopping and delivery system |
| Document | Test Plan |
| Reference | [`00_Application/docs/REQUIREMENTS.md`](../00_Application/docs/REQUIREMENTS.md) (authoritative rule list, R1.1–R9.3) |
| Environment under test | Backend FastAPI (`localhost:8000`), Frontend Next.js (`localhost:3000`), `APP_ENV=test`, `FIXED_NOW=2026-11-10T09:00:00` |

## 1. Introduction

FreshCart is a three-role (CUSTOMER, ADMIN, DELIVERY_PARTNER) grocery ordering and delivery
application covering registration/auth, catalog browsing, cart, coupons/pricing, checkout,
order lifecycle with live status updates, reviews, admin management, and (as later additions)
wishlist, banners, and public coupon offers. This plan covers testing it as a whole — API and
UI — against the business rules in `REQUIREMENTS.md`.

## 2. Scope

### 2.1 In scope

- White-box testing of the backend business logic with two methods: basis path testing (control flow graphs,
  V(G), one test per independent path) and statement/branch/condition coverage: `08_White_Box_Testing/`.
- Black-box testing of the running application with two methods, equivalence partitioning and boundary value
  analysis, executed as data-driven tests over HTTP: `11_Black_Box_Testing/`.
- API testing of every endpoint group with Postman/Newman: `09_API_Testing/`.
- All 42 business rules R1.1–R9.3 across modules M1–M9 (auth, catalog, cart, coupons,
  checkout, order lifecycle, reviews, admin, wishlist/banners/offers).
- REST API contract: status codes, the `{status, error, message, field_errors}` error shape,
  role-based access control (401 vs 403).
- UI flows for all three roles, via the `id`/`data-testid` hooks built into the frontend.
- The order-status WebSocket (live update without refresh).
- Cross-cutting behaviors: JWT expiry/denylist, account lockout, rate limiting, the
  injectable clock (`FIXED_NOW`) for slot/weekday determinism.

### 2.2 Out of scope

- Load/performance/security penetration testing (functional correctness only). Mutation testing is not run (see `08_White_Box_Testing/README.md`).
- Payment gateway integration (checkout payment is explicitly mocked — no real gateway).
- SMS/email delivery (the app has none — OTP is shown in-app, not sent externally).
- Visual/pixel-level design regression testing (manual visual sanity only).
- Browser matrix beyond Chrome (Selenium automation targets Chrome via Selenium Manager).

## 3. Test items

| Item | Source |
|---|---|
| Backend REST API | `00_Application/backend` |
| WebSocket `/ws/orders/{id}` | `00_Application/backend/app/routers/ws.py` |
| Frontend web app (all routes) | `00_Application/frontend` |

## 4. Test approach

| Level | Method | Where |
|---|---|---|
| White-box method 1: basis path | CFG and V(G) for `validate_coupon`, `_validate_payment`, `complete_delivery`; one pytest test per independent path | `00_Application/backend/tests/unit`, `08_White_Box_Testing/Basis_Path_Testing.md` |
| White-box method 2: coverage | pytest + pytest-cov on `app/services` and `app/core`, isolated in-memory SQLite, statement and branch coverage, condition coverage by predicate | `00_Application/backend/tests/unit`, `08_White_Box_Testing/Coverage_Report.md` |
| Black-box method 1: equivalence partitioning | One representative per valid and invalid class, every input of M1-M9, sent over HTTP with no knowledge of the code | `11_Black_Box_Testing/tests/test_ep_*.py` |
| Black-box method 2: boundary value analysis | min-1, min, min+1, max-1, max, max+1 for every numeric and length rule, with exact money values built through the admin API | `11_Black_Box_Testing/tests/test_bva_*.py` |
| API-level functional | Postman collection run headless with Newman against the test-mode backend | `09_API_Testing` |
| UI functional / end-to-end | Automated, Selenium + pytest, Page Object Model | `05_Test_Automation` |
| Exploratory / manual | Manual pass for flows not automated (e.g. visual banner carousel, mobile layout) | `03_Test_Execution` |

Equivalence partitioning and boundary value analysis are the two black-box methods the portfolio is graded on, so
each is both designed (`02_Test_Case_Design`) and executed (`11_Black_Box_Testing`); the Selenium and Newman suites
are black-box too but are organised by feature, not by technique. Decision tables and state transition testing
stay as supporting design techniques.

Test cases are designed in `02_Test_Case_Design` with equivalence partitioning, boundary value
analysis, decision tables and state transition testing (one document each), plus explicit
negative cases for every documented error response. Each test case traces to one or more rule
IDs. Requirements were analysed first: [`Requirements_Analysis.md`](Requirements_Analysis.md).

## 5. Test environment

- Backend started with `APP_ENV=test FIXED_NOW=2026-11-10T09:00:00` so delivery-slot and
  `FRESH15` weekday rules are deterministic (2026-11-10 is a Tuesday).
- `POST /api/test/reset` is called before each full test run to restore the seeded baseline
  (see seed data below) — this keeps test cases independent of execution order and prior runs.
- Selenium drives Chrome via Selenium Manager (auto-provisioned driver, no manual setup).
- See [`../commands.md`](../commands.md) for exact run commands on any OS.

### Seed data relied on by test cases

| Account | Role | Notes |
|---|---|---|
| `admin@freshcart.test` / `Admin@1234` | ADMIN | |
| `driver1@freshcart.test` / `Driver@1234` | DELIVERY_PARTNER | |
| `driver2@freshcart.test` / `Driver@1234` | DELIVERY_PARTNER | |
| `customer1@freshcart.test` / `Customer@1234` | CUSTOMER | Has one past DELIVERED order — **not** eligible for first-order coupons |
| `customer2@freshcart.test` / `Customer@1234` | CUSTOMER | No orders yet — eligible for `WELCOME10` |

30+ seeded products across 6 categories, including `Watermelon`/`Cauliflower` (stock 0) and
`Mango`/`Paneer`/`Croissant` (stock 1–3) specifically for stock-boundary test cases. Coupons:
`WELCOME10`, `FLAT50`, `FRESH15`, `OLD20` (expired).

## 6. Entry criteria

- Backend and frontend both build and start cleanly (`npm run build`, `pytest` smoke test green).
- `POST /api/test/reset` succeeds and seed data matches the table above.
- Test Case Design (`02_Test_Case_Design`) is complete and reviewed for the module under test.

## 7. Exit criteria

- All automated test cases executed; pass rate recorded in `06_Test_Reports`.
- Every failure has a corresponding entry in `04_Defect_Reports` (or is marked a known/accepted
  limitation with rationale).
- No open **Critical** or **High** severity defects against in-scope rules.

## 8. Suspension / resumption criteria

- Suspend the run if `POST /api/test/reset` fails, or if the backend/frontend fails its
  startup health check — fix the environment before resuming.
- A single test case's failure does not suspend the run; later cases that depend on the same
  fixture state are allowed to cascade-fail and are noted as such in the execution log.

## 9. Risks

| Risk | Mitigation |
|---|---|
| `FIXED_NOW` not set → slot/weekday-coupon tests become flaky (real-time dependent) | Always start the backend in test mode per §5 before a run |
| Selenium timing vs. React state updates | Explicit waits on `data-testid` elements, never fixed sleeps |
| Shared seeded state between test cases | `POST /api/test/reset` before each full run; order-sensitive cases documented explicitly |
| Chrome/driver version drift | Selenium Manager (built into Selenium 4.6+) auto-resolves a matching driver |

## 10. Deliverables

| Folder | Content |
|---|---|
| `01_Test_Plan` | This document and `Requirements_Analysis.md` |
| `02_Test_Case_Design` | Test case specifications + requirements traceability matrix |
| `03_Test_Execution` | Execution log: actual results of running the cases below |
| `04_Defect_Reports` | Any defect found during execution |
| `05_Test_Automation` | The Selenium/pytest automation suite |
| `06_Test_Reports` | Summary report: pass/fail counts, coverage, defect summary |
| `07_Screenshots` | Evidence captured during execution |
| `08_White_Box_Testing` | CFGs, basis path testing, coverage report |
| `11_Black_Box_Testing` | Equivalence partitioning and boundary value analysis suites, results |
| `09_API_Testing` | Postman collection, Newman reports, API results |

## 11. Schedule

A single-pass university project schedule (not a multi-sprint plan):

1. Test Plan + Test Case Design
2. Automation suite build-out
3. Execution run, defect logging
4. Summary report

## 12. Roles

| Role | Responsibility | Member |
|---|---|---|
| Test Analyst | Requirements analysis, test plan, test design techniques, traceability | TODO: name / roll number |
| Test Engineer | Test execution, defect reports, white-box and unit tests, test reports | TODO: name / roll number |
| Automation and QA Engineer | Selenium suite, Postman/Newman suite, CI, final report | TODO: name / roll number |

Role-to-member assignment is to be filled in by the team; see `../Team_Learning_Reflection.md`.
