# Test Plan — FreshCart

| | |
|---|---|
| Project | FreshCart — online grocery shopping and delivery system |
| Document | Test Plan |
| Reference | [`application/docs/REQUIREMENTS.md`](../application/docs/REQUIREMENTS.md) (authoritative rule list, R1.1–R9.3) |
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
  V(G), one test per independent path) and statement/branch/condition coverage: `white-box-testing/`.
- Black-box testing of the running application with two methods, equivalence partitioning and boundary value
  analysis, executed as data-driven tests over HTTP: `black-box-testing/`.
- API testing of every endpoint group with Postman/Newman: `api-testing/`.
- All 42 business rules R1.1–R9.3 across modules M1–M9 (auth, catalog, cart, coupons,
  checkout, order lifecycle, reviews, admin, wishlist/banners/offers).
- REST API contract: status codes, the `{status, error, message, field_errors}` error shape,
  role-based access control (401 vs 403).
- UI flows for all three roles, via the `id`/`data-testid` hooks built into the frontend.
- The order-status WebSocket (live update without refresh).
- Cross-cutting behaviors: JWT expiry/denylist, account lockout, rate limiting, the
  injectable clock (`FIXED_NOW`) for slot/weekday determinism.

### 2.2 Out of scope

- Load/performance/security penetration testing (functional correctness only). Mutation testing is not run (see `white-box-testing/README.md`).
- Payment gateway integration (checkout payment is explicitly mocked — no real gateway).
- SMS/email delivery (the app has none — OTP is shown in-app, not sent externally).
- Visual/pixel-level design regression testing (manual visual sanity only).
- Browser matrix beyond Chrome (Selenium automation targets Chrome via Selenium Manager).

## 3. Test items

| Item | Source |
|---|---|
| Backend REST API | `application/backend` |
| WebSocket `/ws/orders/{id}` | `application/backend/app/routers/ws.py` |
| Frontend web app (all routes) | `application/frontend` |

## 4. Test approach

| Level | Method | Where |
|---|---|---|
| White-box method 1: basis path | CFG and V(G) for `validate_coupon`, `_validate_payment`, `complete_delivery`; one pytest test per independent path | `application/backend/tests/unit`, `white-box-testing/Basis_Path_Testing.md` |
| White-box method 2: coverage | pytest + pytest-cov on `app/services` and `app/core`, isolated in-memory SQLite, statement and branch coverage, condition coverage by predicate | `application/backend/tests/unit`, `white-box-testing/Coverage_Report.md` |
| Black-box method 1: equivalence partitioning | One representative per valid and invalid class, every input of M1-M9, sent over HTTP with no knowledge of the code | `black-box-testing/tests/test_ep_*.py` |
| Black-box method 2: boundary value analysis | min-1, min, min+1, max-1, max, max+1 for every numeric and length rule, with exact money values built through the admin API | `black-box-testing/tests/test_bva_*.py` |
| API-level functional | Postman collection run headless with Newman against the test-mode backend | `api-testing` |
| UI functional / end-to-end | Automated, Selenium + pytest, Page Object Model | `automation-testing/selenium-or-playwright` |
| Exploratory / manual | Manual pass for flows not automated (e.g. visual banner carousel, mobile layout) | `test-execution` |

Equivalence partitioning and boundary value analysis are the two black-box methods the portfolio is graded on, so
each is both designed (`test-cases`) and executed (`black-box-testing`); the Selenium and Newman suites
are black-box too but are organised by feature, not by technique. Decision tables and state transition testing
stay as supporting design techniques.

Test cases are designed in `test-cases` with equivalence partitioning, boundary value
analysis, decision tables and state transition testing (one document each), plus explicit
negative cases for every documented error response. Each test case traces to one or more rule
IDs. Requirements were analysed first: [`Requirements_Analysis.md`](../requirements/Requirements_Analysis.md).

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
- Test Case Design (`test-cases`) is complete and reviewed for the module under test.

## 7. Exit criteria

- All automated test cases executed; pass rate recorded in `final-test-report`.
- Every failure has a corresponding entry in `defect-reports` (or is marked a known/accepted
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
| `requirements` | Requirements analysis |
| `test-plan` | This document |
| `test-cases` | Test case specifications + requirements traceability matrix |
| `test-execution` | Execution log: actual results of running the cases below |
| `defect-reports` | Any defect found during execution |
| `automation-testing/selenium-or-playwright` | The Selenium/pytest automation suite |
| `final-test-report` | Summary report: pass/fail counts, coverage, defect summary |
| `evidence/screenshots` | Evidence captured during execution |
| `white-box-testing` | CFGs, basis path testing, coverage report |
| `black-box-testing` | Equivalence partitioning and boundary value analysis suites, results |
| `api-testing` | Postman collection, Newman reports, API results |

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

Role-to-member assignment is to be filled in by the team; see `../reflections/Team_Learning_Reflection.md`.
