# 07 — Screenshots

Evidence captured during development/verification and test execution against the running
application (`APP_ENV=test`, `FIXED_NOW=2026-11-10T09:00:00`).

## Index

| File | Shows |
|---|---|
| `01_homepage_catalog.png` | Homepage: banner carousel, category showcase, special offers, product grid |
| `02_navbar_logged_in.png` | Navbar in the logged-in customer state (search, wishlist/orders links, cart) |
| `03_cart_page.png` | Cart page with items, coupon, and recalculated totals |
| `04_wishlist_page.png` | Wishlist page (R9.1) |
| `05_mobile_bottom_nav.png` | Mobile viewport with the fixed bottom navigation bar |
| `06_admin_products.png` | Admin product management table (R8.1) |
| `07_order_detail_with_otp.png` | Customer order detail: order number, delivery OTP, status timeline (R5.4, R6.5) |
| `08_live_websocket_status_update.png` | Order detail page updating live via WebSocket after an admin status change, without a refresh (R6.7) |
| `09_delivery_partner_assigned_orders.png` | Delivery partner's assigned-orders view, both DELIVERED (R6.4) |
| `10_docker_verified_wishlist.png` | Wishlist page rendering correctly through the full Docker Compose stack |

See [`../03_Test_Execution/Execution_Log.md`](../03_Test_Execution/Execution_Log.md) for the
test run these relate to, and [`../06_Test_Reports`](../06_Test_Reports) for the summary report.

## How they were captured

All ten were taken against the running application in test mode, using the seeded accounts
listed in [`../00_Application/README.md`](../00_Application/README.md). They show working
behavior. The six failing automated cases are covered in the Execution Log, not here.

## Coverage

| Area | Screenshots |
|---|---|
| Customer storefront | 01, 02, 03, 04, 05 |
| Admin | 06 |
| Order tracking and live updates | 07, 08 |
| Delivery partner | 09 |
| Docker Compose verification | 10 |

## Adding a screenshot

Name it `NN_short_description.png` with the next free number, add a row to the index, and
cite the rule ID it demonstrates where there is one.
