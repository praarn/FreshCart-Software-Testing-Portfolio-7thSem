"""M8 — Admin (R8.1-R8.5)."""
from conftest import login_as
from pages.admin_pages import (
    AdminAuditLogPage,
    AdminDashboardPage,
    AdminOrdersPage,
    AdminProductsPage,
    AdminUsersPage,
)
from pages.auth_pages import LoginPage
from utils import api_client
from utils.config import ADMIN, CUSTOMER2, SERVICEABLE_PINCODE


def test_admin_creates_product(driver):
    """TC-M8-001 (R8.1/R2.2): admin creates a new product via the UI form."""
    categories = api_client.get("/catalog/categories").json()
    login_as(driver, ADMIN["email"], ADMIN["password"])
    page = AdminProductsPage(driver).open()
    page.wait_visible("admin-product-create-form")
    page.create_product("Kiwi", "90.00", "50", "pc", categories[0]["id"])
    page.wait_visible("admin-products-table")
    r = api_client.get("/admin/products?search=Kiwi", token=api_client.login(ADMIN["email"], ADMIN["password"]))
    assert any(p["name"] == "Kiwi" for p in r.json())


def test_admin_product_price_below_minimum_rejected(driver):
    """TC-M8-002 (R2.2, boundary): price 0.00 is below the 0.01 minimum and is rejected."""
    categories = api_client.get("/catalog/categories").json()
    login_as(driver, ADMIN["email"], ADMIN["password"])
    page = AdminProductsPage(driver).open()
    page.wait_visible("admin-product-create-form")
    page.create_product("Bad Price Item", "0.00", "10", "pc", categories[0]["id"])
    assert page.field_error("price") != ""


def test_admin_updates_product_stock(driver):
    """TC-M8-003 (R8.1): admin updates a product's stock from the table."""
    apple_id = api_client.product_id_by_name("Apple")
    login_as(driver, ADMIN["email"], ADMIN["password"])
    page = AdminProductsPage(driver).open()
    page.wait_visible("admin-products-table")
    page.set_stock(apple_id, "5")
    import time

    time.sleep(0.5)
    product = api_client.get(f"/catalog/products/{apple_id}").json()
    assert product["stock"] == 5


def test_admin_deactivates_product(driver):
    """TC-M8-004 (R8.1): deactivating a product hides it from the customer catalog."""
    apple_id = api_client.product_id_by_name("Apple")
    login_as(driver, ADMIN["email"], ADMIN["password"])
    page = AdminProductsPage(driver).open()
    page.wait_visible("admin-products-table")
    page.toggle_active(apple_id)
    page.wait_text_contains(f"admin-product-active-toggle-{apple_id}", "Inactive")
    detail = api_client.get(f"/catalog/products/{apple_id}")
    assert detail.status_code == 404


def test_admin_filters_orders_by_status(driver):
    """TC-M8-005 (R8.2): the admin order list can be filtered by status."""
    cust_token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    apple_id = api_client.product_id_by_name("Apple")
    api_client.post("/cart/items", token=cust_token, json={"product_id": apple_id, "quantity": 1})
    order = api_client.post(
        "/checkout",
        token=cust_token,
        json={
            "address": {"line1": "123 MG Road", "city": "Bengaluru", "pincode": SERVICEABLE_PINCODE},
            "slot_start": "2026-11-10T12:00:00",
            "payment": {"method": "COD"},
        },
    ).json()

    login_as(driver, ADMIN["email"], ADMIN["password"])
    page = AdminOrdersPage(driver).open()
    page.wait_visible("admin-orders-list")
    page.filter_by_status("PLACED")
    page.wait_visible(f"admin-order-row-{order['id']}", timeout=10)
    assert page.has_row(order["id"])


def test_admin_disables_coupon_blocks_further_use(driver):
    """TC-M8-006 (R8.3): disabling a coupon makes it rejected on the next customer use."""
    from pages.admin_pages import AdminCouponsPage

    coupons = api_client.get("/admin/coupons", token=api_client.login(ADMIN["email"], ADMIN["password"])).json()
    flat50 = next(c for c in coupons if c["code"] == "FLAT50")

    login_as(driver, ADMIN["email"], ADMIN["password"])
    page = AdminCouponsPage(driver).open()
    page.wait_visible("admin-coupons-table")
    page.toggle(flat50["id"])
    page.wait_text_contains(f"admin-coupon-toggle-{flat50['id']}", "Disabled")

    cust_token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    cake_id = api_client.product_id_by_name("Chocolate Cake")
    api_client.post("/cart/items", token=cust_token, json={"product_id": cake_id, "quantity": 2})
    r = api_client.post("/cart/coupon", token=cust_token, json={"code": "FLAT50"})
    assert r.status_code == 400


def test_admin_locks_and_unlocks_user(driver):
    """TC-M8-007 (R8.3/R1.5, critical): a locked user's login is rejected until unlocked."""
    users = api_client.get("/admin/users", token=api_client.login(ADMIN["email"], ADMIN["password"])).json()
    cust = next(u for u in users if u["email"] == CUSTOMER2["email"])

    login_as(driver, ADMIN["email"], ADMIN["password"])
    page = AdminUsersPage(driver).open()
    page.wait_visible("admin-users-table")
    page.lock(cust["id"])
    page.wait_text_contains(f"admin-user-status-{cust['id']}", "LOCKED")

    login_page = LoginPage(driver).open()
    login_page.login(CUSTOMER2["email"], CUSTOMER2["password"])
    assert "locked" in login_page.error_text().lower()

    page.open()
    page.wait_visible("admin-users-table")
    page.unlock(cust["id"])
    page.wait_text_contains(f"admin-user-status-{cust['id']}", "ACTIVE")

    resp = api_client.post("/auth/login", json={"email": CUSTOMER2["email"], "password": CUSTOMER2["password"]})
    assert resp.status_code == 200


def test_admin_dashboard_shows_todays_metrics(driver):
    """TC-M8-008 (R8.4): the dashboard shows non-zero orders/revenue after an order today."""
    cust_token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    apple_id = api_client.product_id_by_name("Apple")
    api_client.post("/cart/items", token=cust_token, json={"product_id": apple_id, "quantity": 1})
    api_client.post(
        "/checkout",
        token=cust_token,
        json={
            "address": {"line1": "123 MG Road", "city": "Bengaluru", "pincode": SERVICEABLE_PINCODE},
            "slot_start": "2026-11-10T12:00:00",
            "payment": {"method": "COD"},
        },
    )

    login_as(driver, ADMIN["email"], ADMIN["password"])
    page = AdminDashboardPage(driver).open()
    page.wait_visible("admin-dashboard")
    assert page.orders_today().strip() != "0"


def test_admin_dashboard_lists_low_stock(driver):
    """TC-M8-009 (R8.4): seeded low-stock products (<10) appear on the dashboard."""
    login_as(driver, ADMIN["email"], ADMIN["password"])
    page = AdminDashboardPage(driver).open()
    page.wait_visible("admin-dashboard")
    low_stock_ids = page.low_stock_ids()
    assert len(low_stock_ids) > 0


def test_admin_audit_log_filters_by_order(driver):
    """TC-M8-010 (R8.5): the audit log can be filtered to a single order's rows."""
    cust_token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    apple_id = api_client.product_id_by_name("Apple")
    api_client.post("/cart/items", token=cust_token, json={"product_id": apple_id, "quantity": 1})
    order = api_client.post(
        "/checkout",
        token=cust_token,
        json={
            "address": {"line1": "123 MG Road", "city": "Bengaluru", "pincode": SERVICEABLE_PINCODE},
            "slot_start": "2026-11-10T12:00:00",
            "payment": {"method": "COD"},
        },
    ).json()
    admin_token = api_client.login(ADMIN["email"], ADMIN["password"])
    api_client.patch(f"/admin/orders/{order['id']}/status", token=admin_token, json={"to_status": "CONFIRMED"})

    login_as(driver, ADMIN["email"], ADMIN["password"])
    page = AdminAuditLogPage(driver).open()
    page.wait_visible("admin-audit-log-table")
    page.filter_by_order(order["id"])
    import time

    time.sleep(0.5)
    assert page.row_count() == 2  # PLACED, CONFIRMED
