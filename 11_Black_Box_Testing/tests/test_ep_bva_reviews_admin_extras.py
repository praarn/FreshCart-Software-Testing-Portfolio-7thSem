"""Equivalence partitioning and boundary value analysis for M7 reviews, M8 admin product fields and
M9 wishlist, banners and offers.

TC-M7-005 review eligibility classes (R7.1)    TC-M7-006 rating 1..5 (R7.1)    TC-M7-007 comment length 300 (R7.1)
TC-M8-011 product name 2..80 (R2.2, R8.1)      TC-M8-012 product price 0.01..10000.00 (R2.2, R8.1)
TC-M8-013 product stock 0..1000 (R2.2, R8.1)   TC-M8-014 product field classes (R2.2, R8.1)
TC-M9-007 wishlist classes (R9.1)              TC-M9-008 banner and offer visibility classes (R9.2, R9.3)
TC-M9-009 banner title and image length (R9.2)
"""
import pytest

import helpers
from helpers import add_to_cart, advance_to_out_for_delivery, call, checkout, clear_cart, make_product

pytestmark = pytest.mark.usefixtures("clean_module")


def P(tc, label, *values):
    return pytest.param(*values, id=f"{tc}-{label}")


# ---- reviews: one delivered order holding the products the cases review ---------------------
@pytest.fixture(scope="module")
def delivered(admin, driver, customer1):
    """Returns ({label: product_id}, undelivered_product_id) after delivering one multi-line order."""
    labels = ["r1", "r2", "r4", "r5", "c299", "c300", "dup", "plain"]
    ids = {label: make_product(admin, price="100.00", stock=20) for label in labels}
    clear_cart(customer1)
    for pid in ids.values():
        assert add_to_cart(customer1, pid).status_code == 200
    r = checkout(customer1)
    assert r.status_code == 201, r.text
    order = r.json()
    advance_to_out_for_delivery(admin, driver, order["id"])
    done = call("POST", f"/delivery/orders/{order['id']}/deliver", driver, json={"otp": order["delivery_otp"]})
    assert done.status_code == 200, done.text
    return ids, make_product(admin, price="100.00", stock=20)


def review(token, product_id, rating=5, comment=None):
    return call("POST", "/reviews", token, json={"product_id": product_id, "rating": rating, "comment": comment})


# TC-M7-005
def test_review_of_a_delivered_product_is_accepted(customer1, delivered):
    # TC-M7-005
    ids, _ = delivered
    r = review(customer1, ids["plain"], 4, "Fresh")
    assert r.status_code == 201 and r.json()["rating"] == 4                                     # EP1


def test_review_of_a_product_never_delivered_is_refused(customer1, delivered):
    # TC-M7-005
    _, undelivered = delivered
    r = review(customer1, undelivered)
    assert r.status_code == 400 and "delivered" in r.json()["message"].lower()                  # EP2


def test_second_review_of_the_same_product_is_a_conflict(customer1, delivered):
    # TC-M7-005
    ids, _ = delivered
    assert review(customer1, ids["dup"]).status_code == 201
    assert review(customer1, ids["dup"], 2).status_code == 409                                  # EP3


def test_customer_who_did_not_buy_the_product_is_refused(customer2, delivered):
    # TC-M7-005
    ids, _ = delivered
    assert review(customer2, ids["plain"]).status_code == 400                                   # EP4


def test_review_needs_a_customer_token_and_a_known_product(customer1, admin, delivered):
    # TC-M7-005
    ids, _ = delivered
    assert call("POST", "/reviews", json={"product_id": ids["plain"], "rating": 5}).status_code == 401   # EP5
    assert review(admin, ids["plain"]).status_code == 403                                                # EP6
    assert review(customer1, 999999).status_code in (400, 404)                                           # EP7


def test_reviews_are_listed_publicly_for_a_product(delivered):
    # TC-M7-005
    ids, _ = delivered
    listed = call("GET", "/reviews", params={"product_id": ids["dup"]})
    assert listed.status_code == 200 and [x["rating"] for x in listed.json()] == [5]            # EP8


# TC-M7-006: rating boundaries. 0 and 6 fail validation; 1 and 5 are accepted for a delivered product.
@pytest.mark.parametrize("label,rating,status", [
    P("TC-M7-006", "rating0-min-1", "plain", 0, 422),
    P("TC-M7-006", "rating1-min", "r1", 1, 201),
    P("TC-M7-006", "rating2-min+1", "r2", 2, 201),
    P("TC-M7-006", "rating4-max-1", "r4", 4, 201),
    P("TC-M7-006", "rating5-max", "r5", 5, 201),
    P("TC-M7-006", "rating6-max+1", "plain", 6, 422),
    P("TC-M7-006", "rating-negative", "plain", -1, 422),
    P("TC-M7-006", "rating-fractional", "plain", 3.5, 422),
])
def test_rating_boundaries(customer1, delivered, label, rating, status):
    r = review(customer1, delivered[0][label], rating)
    assert r.status_code == status, r.text


# TC-M7-007: comment boundaries
@pytest.mark.parametrize("label,length,status", [
    P("TC-M7-007", "len299-max-1", "c299", 299, 201),
    P("TC-M7-007", "len300-max", "c300", 300, 201),
    P("TC-M7-007", "len301-max+1", "plain", 301, 422),
])
def test_comment_length_boundaries(customer1, delivered, label, length, status):
    r = review(customer1, delivered[0][label], 5, "x" * length)
    assert r.status_code == status, r.text


# ---- M8: product fields -------------------------------------------------------------------
def create(admin, **fields):
    body = {"name": f"BB Field {next(helpers._counter)}", "price": "10.00", "stock": 10, "unit": "kg", "category_id": 1}
    body.update(fields)
    return call("POST", "/admin/products", admin, json=body)


@pytest.mark.parametrize("length,status", [
    P("TC-M8-011", "len1-min-1", 1, 422), P("TC-M8-011", "len2-min", 2, 201), P("TC-M8-011", "len3-min+1", 3, 201),
    P("TC-M8-011", "len79-max-1", 79, 201), P("TC-M8-011", "len80-max", 80, 201), P("TC-M8-011", "len81-max+1", 81, 422),
])
def test_product_name_length(admin, length, status):
    assert create(admin, name="N" * length).status_code == status


@pytest.mark.parametrize("price,status", [
    P("TC-M8-012", "0.00-min-1", "0.00", 422), P("TC-M8-012", "0.01-min", "0.01", 201), P("TC-M8-012", "0.02-min+1", "0.02", 201),
    P("TC-M8-012", "9999.99-max-1", "9999.99", 201), P("TC-M8-012", "10000.00-max", "10000.00", 201),
    P("TC-M8-012", "10000.01-max+1", "10000.01", 422), P("TC-M8-012", "negative", "-1.00", 422),
])
def test_product_price(admin, price, status):
    r = create(admin, price=price)
    assert r.status_code == status, r.text
    if status == 201:
        assert r.json()["price"] == price


@pytest.mark.parametrize("stock,status", [
    P("TC-M8-013", "stock-1-min-1", -1, 422), P("TC-M8-013", "stock0-min", 0, 201), P("TC-M8-013", "stock1-min+1", 1, 201),
    P("TC-M8-013", "stock999-max-1", 999, 201), P("TC-M8-013", "stock1000-max", 1000, 201),
    P("TC-M8-013", "stock1001-max+1", 1001, 422),
])
def test_product_stock_on_create_and_on_stock_update(admin, stock, status):
    assert create(admin, stock=stock).status_code == status
    pid = make_product(admin, stock=5)
    assert call("PATCH", f"/admin/products/{pid}/stock", admin, json={"stock": stock}).status_code == (200 if status == 201 else 422)


@pytest.mark.parametrize("unit", [P("TC-M8-014", f"EP-unit-{u}", u) for u in ("kg", "g", "l", "ml", "pc", "pack")])
def test_every_listed_unit_is_accepted(admin, unit):
    assert create(admin, unit=unit).status_code == 201


@pytest.mark.parametrize("change", [
    P("TC-M8-014", "EP-unit-not-listed", {"unit": "box"}),
    P("TC-M8-014", "EP-price-not-a-number", {"price": "abc"}),
    P("TC-M8-014", "EP-stock-fractional", {"stock": 1.5}),
    P("TC-M8-014", "EP-category-missing", {"category_id": None}),
])
def test_invalid_field_classes_are_rejected(admin, change):
    assert create(admin, **change).status_code == 422


def test_non_admin_cannot_create_products(customer1):
    r = call("POST", "/admin/products", customer1, json={"name": "Nope", "price": "10.00", "stock": 1, "unit": "kg", "category_id": 1})
    assert r.status_code == 403                                                                  # TC-M8-014 EP-role


# ---- M9: wishlist ----------------------------------------------------------------------------
def test_wishlist_classes(customer2):
    # TC-M9-007
    for pid in [x["product"]["id"] for x in call("GET", "/wishlist", customer2).json()]:
        call("DELETE", f"/wishlist/items/{pid}", customer2)
    assert call("POST", "/wishlist/items", customer2, json={"product_id": 1}).status_code == 201          # EP1 new product
    assert call("POST", "/wishlist/items", customer2, json={"product_id": 1}).status_code == 409          # EP2 duplicate
    assert call("POST", "/wishlist/items", customer2, json={"product_id": 999999}).status_code == 404     # EP3 unknown product
    assert [x["product"]["id"] for x in call("GET", "/wishlist", customer2).json()] == [1]                   # EP4 listed once
    assert call("DELETE", "/wishlist/items/1", customer2).status_code == 204                              # EP5 remove saved
    assert call("DELETE", "/wishlist/items/1", customer2).status_code == 404                              # EP6 remove unsaved
    assert call("GET", "/wishlist").status_code == 401                                                     # EP7 no token


# ---- M9: banners and offers --------------------------------------------------------------------
def banner(admin, **fields):
    body = {"title": f"BB Banner {next(helpers._counter)}", "image_url": "https://example.com/b.jpg", "display_order": 50}
    body.update(fields)
    return call("POST", "/admin/banners", admin, json=body)


def test_public_banners_show_only_active_ones_in_display_order(admin):
    # TC-M9-008
    late = banner(admin, display_order=902).json()
    early = banner(admin, display_order=901).json()
    hidden = banner(admin, display_order=900, active=False).json()
    shown = call("GET", "/banners").json()
    ids = [b["id"] for b in shown]
    assert early["id"] in ids and late["id"] in ids and hidden["id"] not in ids
    assert ids.index(early["id"]) < ids.index(late["id"])
    orders = [b["display_order"] for b in shown]
    assert orders == sorted(orders)
    for b in (late, early, hidden):
        assert call("DELETE", f"/admin/banners/{b['id']}", admin).status_code == 204


def test_public_offers_list_only_live_coupons_without_admin_fields():
    # TC-M9-008
    offers = call("GET", "/catalog/offers").json()
    codes = [o["code"] for o in offers]
    assert "WELCOME10" in codes and "FLAT50" in codes and "OLD20" not in codes
    assert all("id" not in o and "active" not in o for o in offers)


def test_disabled_coupon_disappears_from_offers(admin):
    # TC-M9-008
    coupons = call("GET", "/admin/coupons", admin).json()
    flat = next(c for c in coupons if c["code"] == "FLAT50")
    assert call("PATCH", f"/admin/coupons/{flat['id']}", admin, json={"active": False}).status_code == 200
    try:
        assert "FLAT50" not in [o["code"] for o in call("GET", "/catalog/offers").json()]
    finally:
        call("PATCH", f"/admin/coupons/{flat['id']}", admin, json={"active": True})


# ---- TC-M9-009: banner field lengths -------------------------------------------------------
@pytest.mark.parametrize("field,length,status", [
    P("TC-M9-009", "title-len1-min-1", "title", 1, 422), P("TC-M9-009", "title-len2-min", "title", 2, 201),
    P("TC-M9-009", "title-len100-max", "title", 100, 201), P("TC-M9-009", "title-len101-max+1", "title", 101, 422),
    P("TC-M9-009", "image-len4-min-1", "image_url", 4, 422), P("TC-M9-009", "image-len5-min", "image_url", 5, 201),
    P("TC-M9-009", "image-len500-max", "image_url", 500, 201), P("TC-M9-009", "image-len501-max+1", "image_url", 501, 422),
])
def test_banner_field_lengths(admin, field, length, status):
    r = banner(admin, active=False, **{field: "B" * length})
    assert r.status_code == status, r.text
    if status == 201:
        call("DELETE", f"/admin/banners/{r.json()['id']}", admin)
