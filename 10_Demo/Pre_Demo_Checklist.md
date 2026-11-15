# Pre-Demo Checklist

## Environment used for the committed results

| Item | Version |
|---|---|
| OS | Windows 11 |
| Python | 3.12.10 (3.14 is also installed; the pinned requirements are for 3.12) |
| Node | 24.x (CI uses 20) |
| Chrome | 157.0.8103.51, chromedriver via Selenium Manager |
| Selenium / pytest / pytest-html | 4.27.1 / 8.3.4 / 4.1.1 |
| pytest-cov / pytest-asyncio | 7.1.0 / 1.3.0 |
| Newman / htmlextra reporter | 6.x / 1.x |

## Start-up (do these in order)

1. Backend: `cd 00_Application/backend; pip install -r requirements.txt; alembic upgrade head; python -m app.seed`
2. Start it in test mode: `APP_ENV=test FIXED_NOW=2026-11-10T09:00:00 uvicorn app.main:app --port 8000`
3. Frontend: `cd 00_Application/frontend; npm ci; npm run build; npm start`
4. Automation deps: `pip install -r 05_Test_Automation/requirements.txt`
5. Newman: `npm i -g newman newman-reporter-htmlextra`

## Dry run

- [ ] `curl localhost:8000/api/health` returns `{"status":"ok"}`; `localhost:3000` loads
- [ ] `POST /api/test/reset` returns ok
- [ ] `pytest tests/test_m4_coupons.py -k welcome10` passes (login works: DEF-003 fix present)
- [ ] `pytest` in `00_Application/backend` shows all tests passing and the coverage table
- [ ] Newman run finishes with 0 failed assertions (allow 6 minutes)
- [ ] Black-box suite (`11_Black_Box_Testing`, backend in test mode) finishes with 0 failed (allow 3 minutes), or at least one slice: `pytest tests/test_bva_accounts.py -k password`
- [ ] The HTML reports open: `03_Test_Execution/selenium_report.html`, `09_API_Testing/reports/newman_report.html`, `08_White_Box_Testing/coverage_html/index.html`
- [ ] The README table and counts match the reports (`python tools/consistency_check.py`)
- [ ] TODO fields in the README, Test Plan and `Team_Learning_Reflection.md` are filled in
- [ ] Each member has commits, pull requests or reviews in the GitHub history (the demo asks for all three)

## Recording the demo video

- [ ] Screen 1920x1080, browser zoom 110-125%, terminal font 16 pt or larger
- [ ] Close notifications; hide bookmarks and personal tabs
- [ ] Start all five terminals and the browser tabs first (see `Demo_Script.md`)
- [ ] Record one segment at a time if a run is slow; Newman and the Selenium module take minutes
- [ ] Show the result lines, not only the progress output
- [ ] Each member speaks about their own part
- [ ] Keep it under 10 minutes; export as MP4
- [ ] Upload outside the repository (YouTube unlisted or Drive) and paste the link into `README.md` (the `TODO` under "Demo")
- [ ] Do not commit the video file to the repository
