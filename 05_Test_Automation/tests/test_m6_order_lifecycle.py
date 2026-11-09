"""M6 — Orders and lifecycle (R6.1-R6.7)."""
from conftest import login_as
from pages.admin_pages import AdminOrdersPage
from pages.delivery_page import DeliveryPage
from pages.orders_pages import OrderDetailPage
from utils import api_client
from utils.config import ADMIN, CUSTOMER2, DRIVER1, DRIVER2, SERVICEABLE_PINCODE


def _place_order(token, slot="2026-11-10T12:00:00", product="Apple", qty=1):
    product_id = api_client.product_id_by_name(product)
    api_client.post("/cart/items", token=token, json={"product_id": product_id, "quantity": qty})
    r = api_client.post(
        "/checkout",
        token=token,
        json={
            "address": {"line1": "123 MG Road", "city": "Bengaluru", "pincode": SERVICEABLE_PINCODE},
            "slot_start": slot,
            "payment": {"method": "COD"},
        },
    )
    assert r.status_code == 201
    return r.json()


def test_illegal_transition_rejected(driver):
    """TC-M6-001 (R6.1): PLACED -> PACKED directly (skipping CONFIRMED) is rejected."""
    cust_token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    order = _place_order(cust_token)
    admin_token = api_client.login(ADMIN["email"], ADMIN["password"])
    r = api_client.patch(f"/admin/orders/{order['id']}/status", token=admin_token, json={"to_status": "PACKED"})
    assert r.status_code == 409


def test_customer_cancels_placed_order(driver):
    """TC-M6-003 (R6.2): a customer can cancel an order while it's PLACED; stock restores."""
    cust_token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    apple_id = api_client.product_id_by_name("Apple")
    before = api_client.get(f"/catalog/products/{apple_id}").json()["stock"]
    order = _place_order(cust_token, product="Apple", qty=1)

    login_as(driver, CUSTOMER2["email"], CUSTOMER2["password"])
    page = OrderDetailPage(driver).open(order["id"])
    page.wait_visible("order-detail-status")
    assert page.can_cancel()
    page.cancel()
    page.wait_text_contains("order-detail-status", "CANCELLED")

    after = api_client.get(f"/catalog/products/{apple_id}").json()["stock"]
    assert after == before


def test_customer_cannot_cancel_packed_order(driver):
    """TC-M6-004 (R6.2): once PACKED, the customer's cancel control is no longer offered."""
    cust_token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    order = _place_order(cust_token)
    admin_token = api_client.login(ADMIN["email"], ADMIN["password"])
    api_client.patch(f"/admin/orders/{order['id']}/status", token=admin_token, json={"to_status": "CONFIRMED"})
    api_client.patch(f"/admin/orders/{order['id']}/status", token=admin_token, json={"to_status": "PACKED"})

    login_as(driver, CUSTOMER2["email"], CUSTOMER2["password"])
    page = OrderDetailPage(driver).open(order["id"])
    page.wait_visible("order-detail-status")
    assert not page.can_cancel()


def test_admin_confirms_then_packs(driver):
    """TC-M6-005 (R6.3): admin can move PLACED -> CONFIRMED -> PACKED in sequence via the UI."""
    cust_token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    order = _place_order(cust_token)

    login_as(driver, ADMIN["email"], ADMIN["password"])
    page = AdminOrdersPage(driver).open()
    page.wait_visible("admin-orders-list")
    page.confirm(order["id"])
    page.wait_text_contains(f"admin-order-status-{order['id']}", "CONFIRMED")
    page.pack(order["id"])
    page.wait_text_contains(f"admin-order-status-{order['id']}", "PACKED")


def test_partner_assignment_requires_packed(driver):
    """TC-M6-006 (R6.3): assigning a delivery partner before PACKED is rejected."""
    cust_token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    order = _place_order(cust_token)
    admin_token = api_client.login(ADMIN["email"], ADMIN["password"])
    api_client.patch(f"/admin/orders/{order['id']}/status", token=admin_token, json={"to_status": "CONFIRMED"})
    driver1_id = api_client.get("/auth/me", token=api_client.login(DRIVER1["email"], DRIVER1["password"])).json()["id"]
    r = api_client.post(f"/admin/orders/{order['id']}/assign-partner", token=admin_token, json={"delivery_partner_id": driver1_id})
    assert r.status_code == 409


def test_delivery_partner_sees_only_assigned_orders(driver):
    """TC-M6-007 (R6.4): an order assigned to driver1 does not appear for driver2."""
    cust_token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    order = _place_order(cust_token)
    admin_token = api_client.login(ADMIN["email"], ADMIN["password"])
    api_client.patch(f"/admin/orders/{order['id']}/status", token=admin_token, json={"to_status": "CONFIRMED"})
    api_client.patch(f"/admin/orders/{order['id']}/status", token=admin_token, json={"to_status": "PACKED"})
    driver1_id = api_client.get("/auth/me", token=api_client.login(DRIVER1["email"], DRIVER1["password"])).json()["id"]
    api_client.post(f"/admin/orders/{order['id']}/assign-partner", token=admin_token, json={"delivery_partner_id": driver1_id})

    login_as(driver, DRIVER2["email"], DRIVER2["password"])
    page = DeliveryPage(driver).open()
    page.wait_visible("delivery-empty", timeout=10)
    assert not page.has_order(order["id"])


def _place_and_pack_assigned_to_driver1(cust_email, cust_password):
    cust_token = api_client.login(cust_email, cust_password)
    order = _place_order(cust_token)
    admin_token = api_client.login(ADMIN["email"], ADMIN["password"])
    api_client.patch(f"/admin/orders/{order['id']}/status", token=admin_token, json={"to_status": "CONFIRMED"})
    api_client.patch(f"/admin/orders/{order['id']}/status", token=admin_token, json={"to_status": "PACKED"})
    driver1_id = api_client.get("/auth/me", token=api_client.login(DRIVER1["email"], DRIVER1["password"])).json()["id"]
    api_client.post(f"/admin/orders/{order['id']}/assign-partner", token=admin_token, json={"delivery_partner_id": driver1_id})
    return order


def test_dispatch_then_deliver_with_correct_otp(driver):
    """TC-M6-008 (R6.4, critical): driver dispatches then delivers with the correct OTP."""
    order = _place_and_pack_assigned_to_driver1(CUSTOMER2["email"], CUSTOMER2["password"])

    login_as(driver, DRIVER1["email"], DRIVER1["password"])
    page = DeliveryPage(driver).open()
    page.wait_visible("delivery-orders-list")
    page.dispatch(order["id"])
    page.wait_text_contains(f"delivery-order-status-{order['id']}", "OUT_FOR_DELIVERY")
    page.deliver(order["id"], order["delivery_otp"])
    page.wait_text_contains(f"delivery-order-status-{order['id']}", "DELIVERED")


def test_three_wrong_otps_block_further_attempts(driver):
    """TC-M6-009 (R6.4, critical boundary): 3 wrong OTP entries block the order until an
    admin resets it, even if the correct OTP is then supplied."""
    order = _place_and_pack_assigned_to_driver1(CUSTOMER2["email"], CUSTOMER2["password"])
    driver1_token = api_client.login(DRIVER1["email"], DRIVER1["password"])
    api_client.post(f"/delivery/orders/{order['id']}/dispatch", token=driver1_token)

    login_as(driver, DRIVER1["email"], DRIVER1["password"])
    page = DeliveryPage(driver).open()
    page.wait_visible("delivery-orders-list")
    for _ in range(3):
        page.deliver(order["id"], "0000")
        page.wait_visible(f"delivery-order-error-{order['id']}")
    page.deliver(order["id"], order["delivery_otp"])
    assert "reset" in page.error_for(order["id"]).lower() or "blocked" in page.error_for(order["id"]).lower() or "attempt" in page.error_for(order["id"]).lower()


def test_admin_otp_reset_unblocks_delivery(driver):
    """TC-M6-010 (R6.4): admin resetting OTP attempts lets delivery complete afterward."""
    order = _place_and_pack_assigned_to_driver1(CUSTOMER2["email"], CUSTOMER2["password"])
    driver1_token = api_client.login(DRIVER1["email"], DRIVER1["password"])
    api_client.post(f"/delivery/orders/{order['id']}/dispatch", token=driver1_token)
    for _ in range(3):
        api_client.post(f"/delivery/orders/{order['id']}/deliver", token=driver1_token, json={"otp": "0000"})

    admin_token = api_client.login(ADMIN["email"], ADMIN["password"])
    r = api_client.post(f"/admin/orders/{order['id']}/reset-otp", token=admin_token)
    assert r.status_code == 200

    login_as(driver, DRIVER1["email"], DRIVER1["password"])
    page = DeliveryPage(driver).open()
    page.wait_visible("delivery-orders-list")
    page.deliver(order["id"], order["delivery_otp"])
    page.wait_text_contains(f"delivery-order-status-{order['id']}", "DELIVERED")


def test_status_timeline_shows_every_change(driver):
    """TC-M6-011 (R6.5): the order detail status timeline lists every transition."""
    cust_token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    order = _place_order(cust_token)
    admin_token = api_client.login(ADMIN["email"], ADMIN["password"])
    api_client.patch(f"/admin/orders/{order['id']}/status", token=admin_token, json={"to_status": "CONFIRMED"})
    api_client.patch(f"/admin/orders/{order['id']}/status", token=admin_token, json={"to_status": "PACKED"})

    login_as(driver, CUSTOMER2["email"], CUSTOMER2["password"])
    page = OrderDetailPage(driver).open(order["id"])
    page.wait_visible("order-timeline")
    entries = page.timeline_entries()
    assert len(entries) == 3  # PLACED, ->CONFIRMED, ->PACKED


def test_customer_cannot_view_another_customers_order(driver):
    """TC-M6-012 (R6.6, critical): viewing another customer's order returns 403."""
    from utils.config import CUSTOMER1

    cust2_token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    order = _place_order(cust2_token)

    login_as(driver, CUSTOMER1["email"], CUSTOMER1["password"])
    page = OrderDetailPage(driver).open(order["id"])
    page.wait_visible("order-detail-error", timeout=10)


def test_live_websocket_status_update(driver):
    """TC-M6-013 (R6.7): the order detail page updates live via WebSocket when an admin
    changes status in a separate session, without a manual refresh."""
    cust_token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    order = _place_order(cust_token)

    login_as(driver, CUSTOMER2["email"], CUSTOMER2["password"])
    page = OrderDetailPage(driver).open(order["id"])
    page.wait_visible("order-detail-status")

    admin_token = api_client.login(ADMIN["email"], ADMIN["password"])
    api_client.patch(f"/admin/orders/{order['id']}/status", token=admin_token, json={"to_status": "CONFIRMED"})

    page.wait_for_live_update(timeout=10)
    page.wait_text_contains("order-detail-status", "CONFIRMED")
