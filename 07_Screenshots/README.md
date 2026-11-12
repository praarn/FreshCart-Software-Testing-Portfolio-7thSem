# 07 - Screenshots

Evidence from the running application and from the test runs.

## Application (captured earlier, `APP_ENV=test`, `FIXED_NOW=2026-11-10T09:00:00`)

| File | Shows |
|---|---|
| `01_homepage_catalog.png` | Homepage: banner carousel, category showcase, special offers, product grid |
| `02_navbar_logged_in.png` | Navbar in the logged-in customer state |
| `03_cart_page.png` | Cart page with items, coupon and recalculated totals |
| `04_wishlist_page.png` | Wishlist page (R9.1) |
| `05_mobile_bottom_nav.png` | Mobile viewport with the bottom navigation bar |
| `06_admin_products.png` | Admin product management table (R8.1) |
| `07_order_detail_with_otp.png` | Order detail: order number, delivery OTP, status timeline (R5.4, R6.5) |
| `08_live_websocket_status_update.png` | Order page updating live over WebSocket after an admin status change (R6.7) |
| `09_delivery_partner_assigned_orders.png` | Delivery partner's assigned orders (R6.4) |
| `10_docker_verified_wishlist.png` | Wishlist rendering through the Docker Compose stack |

## Test runs (captured 2026-11-14 from the runs recorded in `03_Test_Execution`)

| File | Shows | Source |
|---|---|---|
| `11_pytest_selenium_run.png` | Terminal output of the final Selenium run, 86 passed | rendered from the saved pytest log by `tools/render_terminal_png.py` (text unchanged) |
| `12_pytest_cov_unit_run.png` | Backend unit tests with the coverage table, 136 passed | rendered from `08_White_Box_Testing/coverage_term_unit.txt` |
| `13_pytest_html_report.png` | The pytest-html report (`03_Test_Execution/selenium_report.html`), 86 passed | headless Chrome |
| `14_coverage_html_report.png` | The coverage.py HTML report (unit tests) | headless Chrome |
| `15_newman_cli_summary.png` | End of the Newman run: 291 HTTP requests sent (245 defined plus helper calls), 475 assertions, 0 failed | rendered from the saved Newman log |
| `16_newman_html_report.png` | The Newman htmlextra report | headless Chrome |
| `17_swagger_ui.png` | Swagger UI at `/docs` | headless Chrome against the running backend |

The terminal images are renderings of saved log text, not photographs of a terminal window.

## Not captured

| Item | Reason | How to capture |
|---|---|---|
| Green GitHub Actions run | Nothing has been pushed, so the workflow has not run | Push the branch, open the Actions tab, screenshot the run and save as `18_github_actions_green.png` |
| GitHub contribution graph and pull requests | Depends on each member's account | Screenshot the repository's Insights, Contributors page as `19_github_contributors.png` |

## Adding a screenshot

Name it `NN_short_description.png` with the next free number and add a row above.
