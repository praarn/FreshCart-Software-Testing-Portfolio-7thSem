# Demo Script (8 to 10 minutes)

Seed accounts: admin `admin@freshcart.test / Admin@1234`, driver `driver1@freshcart.test / Driver@1234`,
customer `customer2@freshcart.test / Customer@1234` (first-order eligible), customer1 `customer1@freshcart.test / Customer@1234`.

## Terminals to open before starting

| # | Directory | Command | Purpose |
|---|---|---|---|
| T1 | `00_Application/backend` | `APP_ENV=test FIXED_NOW=2026-11-10T09:00:00 uvicorn app.main:app --port 8000` | API (PowerShell: `$env:APP_ENV="test"; $env:FIXED_NOW="2026-11-10T09:00:00"; uvicorn app.main:app --port 8000`) |
| T2 | `00_Application/frontend` | `npm run build` once, then `npm start` | UI on :3000 (production build; faster and steadier than `npm run dev`) |
| T3 | `05_Test_Automation` | idle, for Selenium | |
| T4 | `00_Application/backend` | idle, for pytest-cov | |
| T5 | `09_API_Testing` | idle, for Newman | |

Browser tabs: GitHub repo, `localhost:3000`, `localhost:8000/docs`, `08_White_Box_Testing/coverage_html/index.html`.

## Timeline

| Min | Segment | What to show and say | Fallback |
|---|---|---|---|
| 0:00-1:00 | Repo and README | Folder layout 00-10; requirement-to-folder table in `README.md`; team table; numbers at a glance | Screenshot of the README in `07_Screenshots/` |
| 1:00-3:00 | Application | Log in as customer2: catalog, add Apple x2, coupon `WELCOME10`, checkout (COD, slot 12:00). Open `/orders/<id>` in one tab; in a second window log in as admin, confirm and pack the order: the first tab updates without refresh (WebSocket). Then driver1: dispatch, deliver with the OTP shown on the customer page | Pre-recorded clip, or show `07_Screenshots/08_live_websocket_status_update.png` and `09_delivery_partner_assigned_orders.png` |
| 3:00-5:00 | Test design techniques | Open `Functional_Test_Cases.xlsx` (filter by Type: `Black-box EP`, `Black-box BVA`, `White-box basis path`, `White-box coverage`). Then `Boundary_Value_Analysis.md` (password 7/8/20/21), `11_Black_Box_Testing/Black_Box_Results.md` (the two black-box methods executed; to run a slice live: `pytest tests/test_bva_accounts.py -k password`, about 20 s), `Decision_Table.md` (coupon rules D1-D7), `State_Transition.md` (diagram, illegal transitions give 409). Show `Traceability_Matrix.md`: 42 of 42 rules covered | Open the same files on GitHub |
| 5:00-6:30 | Selenium plus report | T3: `pytest tests/test_m4_coupons.py --html=report_demo.html --self-contained-html` (10 tests took 273 s in the recorded run: start it first and talk over the design segment, or run a single test with `-k welcome10`, about 20 s). Open the HTML report | Show `03_Test_Execution/selenium_report.html` from the committed full run and `07_Screenshots/` pytest screenshot |
| 6:30-8:00 | White-box | `08_White_Box_Testing/Control_Flow_Graphs/validate_coupon.md`: 9 predicates, V(G)=10 three ways. Basis path table, one test per path. T4: `pytest --cov=app --cov-branch --cov-report=term-missing` then open `coverage_html`. Mention the complete_delivery finding (redundant C6, 6 feasible paths) | `Coverage_Report.md` and its screenshot |
| 8:00-9:00 | API with Newman | T5: `npx newman run FreshCart.postman_collection.json -e FreshCart.postman_environment.json` (about 6 minutes: start it before the white-box segment; the rate-limit pauses are deliberate). Show the summary: 245 requests, 475 assertions, 0 failed | `reports/newman_report.html`, `API_Test_Results.md` |
| 9:00-9:30 | Defects | DEF-003 (token expiry vs injected clock; found by the Selenium re-run), DEF-004 (slots endpoint without auth, found by Newman), DEF-005 (trailing newline accepted, found by reading the regexes). Each has a regression test | `04_Defect_Reports/README.md` |
| 9:30-10:00 | CI and contribution | GitHub Actions run (backend, unit tests with coverage, Newman, frontend build). Contribution graph and `Team_Learning_Reflection.md` | Screenshot in `07_Screenshots/` |

## Reset between takes

`curl -X POST http://localhost:8000/api/test/reset` restores the seed data. Restart T1 if the rate limiter
has been exhausted (10 login or register calls per minute).

## If something breaks live

| Symptom | Action |
|---|---|
| Selenium times out on a page | Re-run that test; confirm T2 is the production build (`npm start`), not `npm run dev` |
| All logins return 401 | Backend not started with `FIXED_NOW`, or an old build without the DEF-003 fix |
| Port in use | `netstat -ano | findstr :8000`, then stop that process |
| Chrome driver mismatch | Selenium Manager downloads a matching driver; check network access |
