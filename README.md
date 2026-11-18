# Software Testing Portfolio - FreshCart

[![CI](https://github.com/praarn/Software-Testing-Portfolio-7thSem/actions/workflows/ci.yml/badge.svg)](https://github.com/praarn/Software-Testing-Portfolio-7thSem/actions/workflows/ci.yml)

Online portfolio for the Software Testing course. The application under test is **FreshCart**, an online grocery shopping
and delivery system (FastAPI backend, Next.js frontend). Around it sits the testing work: plan, requirements analysis,
black-box and white-box design, API and UI automation, execution results, defects, reports and a demo.

## Student details

| | |
|---|---|
| Subject / course code / semester | TODO: subject name, course code, semester |
| Faculty | TODO: faculty name |
| Demo | TODO: date and format; video link (upload outside the repository and paste it here) |

| Member | Roll number | Role |
|---|---|---|
| TODO: name | TODO | Test Analyst |
| TODO: name | TODO | Test Engineer |
| TODO: name | TODO | Automation and QA Engineer |

Contributions and reflections: [`Team_Learning_Reflection.md`](Team_Learning_Reflection.md).

## Objectives

1. Analyse the requirements of a real application and plan its testing.
2. Black-box testing with two methods, equivalence partitioning and boundary value analysis, designed (with decision
   tables and state transition testing as support) and executed as a data-driven suite over HTTP.
3. White-box testing with two methods: basis path testing (control flow graphs, V(G), one test per path) and
   statement, branch and condition coverage.
4. Test the REST API (Postman/Newman) and the UI (Selenium) and run all suites in CI.
5. Execute, record actual results, report defects and give a final test report.

## The application

FreshCart has three roles: customer, admin and delivery partner. Customers browse and search a catalog, keep a cart and
wishlist, apply coupons, check out with a delivery slot and COD, UPI or card payment, and follow the order live over a
WebSocket. Admins manage products, orders, coupons, users, banners and read the audit log. Delivery partners dispatch
orders and confirm delivery with the customer's OTP. 42 business rules (R1.1-R9.3) are listed in
[`Application/docs/REQUIREMENTS.md`](Application/docs/REQUIREMENTS.md).

```mermaid
flowchart LR
    B["Browser: Next.js 16 UI"] -- "REST /api" --> A["FastAPI app"]
    B -- "WebSocket /ws/orders/id" --> A
    A --> S["Services: auth, cart, pricing, checkout, orders, admin"]
    S --> D[("SQLite / PostgreSQL")]
    T["Selenium + pytest"] --> B
    N["Newman (Postman)"] --> A
    U["pytest unit tests + coverage"] --> S
    K["Black-box EP/BVA suite (pytest)"] --> A
```

## At a glance

| | |
|---|---|
| Business rules | 42, all traced to test cases |
| Test cases designed | 169 (86 Selenium, 22 API, 45 black-box EP/BVA, 16 unit) |
| Black-box suite (EP and BVA) | 288 passed, 0 failed |
| Selenium suite | 86 passed, 0 failed |
| API suite (Newman) | 245 requests, 475 assertions, 0 failed |
| Unit tests | 136 passed; 65.2% statement and 38.2% branch coverage alone, 95.0% and 86.8% combined with the API suite |
| Defects | 8 found (DEF-001 to DEF-008), 0 open |
| CI | GitHub Actions: backend with coverage, Newman, frontend build, Selenium (all four green on a hosted runner, 2026-11-14) and the new black-box job (added after that run, not yet seen green on a hosted runner) |

## Test evidence

Every number above comes from a saved tool report, not from the Markdown. Open the report to check it.

| Test type | Result | Open the report | Screenshot |
|---|---|---|---|
| Selenium UI (pytest) | 86 passed, 0 failed | [`selenium_report.html`](Test_Execution/selenium_report.html), [`selenium_junit.xml`](Test_Execution/selenium_junit.xml) | [`13`](Screenshots/13_pytest_html_report.png), [`11`](Screenshots/11_pytest_selenium_run.png) |
| Black-box EP and BVA (pytest) | 288 passed, 0 failed | [`Black_Box_Results.md`](Black_Box_Testing/Black_Box_Results.md), [`black_box_junit.xml`](Black_Box_Testing/results/black_box_junit.xml) | |
| API (Newman) | 245 requests, 475 assertions, 0 failed | [`newman_report.html`](API_Testing/reports/newman_report.html), [`newman_report.json`](API_Testing/reports/newman_report.json) | [`16`](Screenshots/16_newman_html_report.png), [`15`](Screenshots/15_newman_cli_summary.png) |
| Unit and coverage (pytest-cov) | 136 passed | [`coverage_html/index.html`](White_Box_Testing/coverage_html/index.html), [`Coverage_Report.md`](White_Box_Testing/Coverage_Report.md) | [`14`](Screenshots/14_coverage_html_report.png), [`12`](Screenshots/12_pytest_cov_unit_run.png) |
| CI (GitHub Actions) | 4 of 4 jobs green on 2026-11-14, before the black-box job was added | [Actions tab](https://github.com/praarn/Software-Testing-Portfolio-7thSem/actions), reports kept as run artifacts | badge above |
| Defects | 8 found, 0 open | [`Defect_Reports/`](Defect_Reports/), each with its regression test and screenshot | |

HTML reports show as source code on GitHub. Download the file and open it in a browser, or use the screenshots.

![Selenium report: 86 passed](Screenshots/13_pytest_html_report.png)

![Newman report: 0 failed](Screenshots/16_newman_html_report.png)

![Coverage report](Screenshots/14_coverage_html_report.png)

Printable summary: [`Test_Reports/Test_Summary_Report.pdf`](Test_Reports/Test_Summary_Report.pdf).
Screenshots of every testing activity and metric charts: [`Screenshots/`](Screenshots/), figures in [`Test_Reports/Test_Metrics.md`](Test_Reports/Test_Metrics.md).

## Assignment requirement to folder

| Requirement | Where |
|---|---|
| README: student details, subject, objectives, project description | this file |
| Introduction to the application | this file, [`Application/`](Application/) |
| Requirements analysis | [`Test_Plan/Requirements_Analysis.md`](Test_Plan/Requirements_Analysis.md) |
| Test plan | [`Test_Plan/Test_Plan.md`](Test_Plan/Test_Plan.md) |
| Test scenarios and cases (`.xlsx`) | [`Test_Case_Design/Functional_Test_Cases.xlsx`](Test_Case_Design/Functional_Test_Cases.xlsx), `Test_Cases.csv`, `Traceability_Matrix.md` |
| Black box, method 1 and 2: equivalence partitioning, boundary value analysis (plus decision table, state transition) | design in [`Test_Case_Design/`](Test_Case_Design/) (one document each), execution in [`Black_Box_Testing/`](Black_Box_Testing/) |
| White box, method 1 and 2: basis path (CFG, V(G)); statement/branch/condition coverage and report | [`White_Box_Testing/`](White_Box_Testing/) |
| API testing | [`API_Testing/`](API_Testing/) |
| Automation testing (Selenium; additional activity) | [`Test_Automation/`](Test_Automation/) |
| Test execution with actual results | [`Test_Execution/`](Test_Execution/) |
| Defect and bug reports | [`Defect_Reports/`](Defect_Reports/) |
| Execution summary and final test report | [`Test_Reports/Test_Summary_Report.md`](Test_Reports/Test_Summary_Report.md), [`Conclusion.md`](Conclusion.md) |
| Screenshots, diagrams, scripts, video evidence | [`Screenshots/`](Screenshots/), Mermaid diagrams in this file, `Test_Case_Design/State_Transition.md` and `White_Box_Testing/Control_Flow_Graphs/`, scripts in `Test_Automation/` and `tools/` |
| Short demo video, demonstration and viva | Video link above (TODO); demo material is kept outside the repository |
| Individual contribution and reflection, GitHub activity | [`Team_Learning_Reflection.md`](Team_Learning_Reflection.md) |
| CI | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) |

## Repository layout

| Folder / file | Contents |
|---|---|
| [`Application/`](Application/) | FreshCart: `backend/` (FastAPI, with `tests/unit/`), `frontend/` (Next.js), `docs/REQUIREMENTS.md` |
| [`Test_Plan/`](Test_Plan/) | Test plan, requirements analysis |
| [`Test_Case_Design/`](Test_Case_Design/) | Cases (CSV, xlsx), traceability matrix, EP, BVA, decision table, state transition |
| [`Test_Execution/`](Test_Execution/) | Execution log, per-case results, formerly manual cases |
| [`Defect_Reports/`](Defect_Reports/) | DEF-001 to DEF-008 and a template |
| [`Test_Automation/`](Test_Automation/) | Selenium + pytest suite, `diagnostics/`, `tools/` |
| [`Test_Reports/`](Test_Reports/) | Test summary report |
| [`Screenshots/`](Screenshots/) | Application and test-run screenshots |
| [`White_Box_Testing/`](White_Box_Testing/) | CFGs, basis path testing, coverage report and HTML |
| [`API_Testing/`](API_Testing/) | Postman collection, Newman reports, results |
| [`Black_Box_Testing/`](Black_Box_Testing/) | Equivalence partitioning and boundary value analysis suites, results |
| `tools/` | `consistency_check.py`, coverage and screenshot helpers |
| `Conclusion.md`, `Team_Learning_Reflection.md` | Results and lessons; contributions and reflections |
| `docker-compose.yml`, `commands.md`, `explanation.md` | Docker stack, run commands per OS, repo map |

## Quick start

Local, with SQLite (two terminals):

```bash
# Terminal 1: backend
cd Application/backend
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload      # http://localhost:8000  (Swagger UI at /docs)

# Terminal 2: frontend
cd Application/frontend
npm install
npm run dev                        # http://localhost:3000
```

Or `docker compose up --build` (PostgreSQL included). Prerequisites: Python 3.12, Node 20 or newer, Chrome for Selenium.
Per-OS commands, including PowerShell, are in [`commands.md`](commands.md).

## Running the tests

```bash
# Backend in test mode (resettable database, frozen clock)
cd Application/backend
APP_ENV=test FIXED_NOW=2026-11-10T09:00:00 uvicorn app.main:app --port 8000

# Unit tests with coverage (no server needed): white-box basis path and coverage cases
pytest --cov=app --cov-branch --cov-report=term-missing

# Black-box suite, equivalence partitioning and boundary value analysis (backend in test mode, about 3 minutes)
cd ../../Black_Box_Testing && pip install -r requirements.txt && pytest
cd ../Application/backend

# Selenium (use a production build of the frontend: npm run build && npm start)
cd Test_Automation && pip install -r requirements.txt && pytest

# API (about 6 minutes: the login rate limit is paced on purpose)
cd API_Testing && npx newman run FreshCart.postman_collection.json -e FreshCart.postman_environment.json

# Check that every count quoted in the docs matches the tools' output
python tools/consistency_check.py
```

## Seed accounts

| Role | Email | Password |
|---|---|---|
| Admin | admin@freshcart.test | Admin@1234 |
| Delivery partner | driver1@freshcart.test | Driver@1234 |
| Customer (has an order) | customer1@freshcart.test | Customer@1234 |
| Customer (no orders, eligible for `WELCOME10`) | customer2@freshcart.test | Customer@1234 |

More accounts, coupons and test-mode variables: [`Application/README.md`](Application/README.md).
