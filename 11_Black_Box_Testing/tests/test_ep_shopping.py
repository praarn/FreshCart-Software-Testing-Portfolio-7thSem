"""Equivalence partitioning, M2 catalog, M3 cart, M4 coupons.

TC-M2-008 search / filter / sort / detail classes (R2.3)    TC-M2-009 product visibility classes (R2.4)
TC-M3-013 cart quantity and item classes (R3.1, R3.4)
TC-M4-017 coupon classes (R4.1, R4.2)
"""
from decimal import Decimal

import pytest

import helpers
from helpers import add_to_cart, call, cart_with_subtotal, clear_cart, make_product


def P(tc, cls, *values):
    return pytest.param(*values, id=f"{tc}-{cls}")


def products(**params):
    r = call("GET", "/catalog/products", params=params)
    assert r.status_code == 200, r.text
    return r.json()


# ---- TC-M2-008 ------------------------------------------------------------------------------
@pytest.mark.parametrize("term", [
    P("TC-M2-008", "EP1-lowercase-exact", "apple"),
    P("TC-M2-008", "EP2-uppercase", "APPLE"),
    P("TC-M2-008", "EP3-partial", "ppl"),
])
def test_search_matches_case_insensitively_and_partially(term):
    names = [p["name"] for p in products(search=term)["items"]]
    assert "Apple" in names


def test_search_without_match_returns_empty_list():
    # TC-M2-008
    body = products(search="zzzz-no-such-product")
    assert body["items"] == [] and body["total"] == 0


def test_category_filter_valid_and_unknown_category():
    # TC-M2-008
    items = products(category_id=1)["items"]
    assert items and all(p["category_id"] == 1 for p in items)      # EP: existing category
    assert products(category_id=999)["total"] == 0                  # EP: category that does not exist


@pytest.mark.parametrize("sort,key", [
    P("TC-M2-008", "EP4-sort-price-ascending", "price_asc", 1),
    P("TC-M2-008", "EP5-sort-price-descending", "price_desc", -1),
])
def test_sort_orders_by_price(sort, key):
    prices = [Decimal(p["price"]) * key for p in products(sort=sort)["items"]]
    assert prices == sorted(prices)


def test_unsupported_sort_value_rejected():
    assert call("GET", "/catalog/products", params={"sort": "name_asc"}).status_code == 422   # TC-M2-008 EP6


def test_product_detail_known_and_unknown_id():
    assert call("GET", "/catalog/products/1").json()["name"] == "Apple"     # TC-M2-008 EP7
    assert call("GET", "/catalog/products/999999").status_code == 404       # TC-M2-008 EP8


# ---- TC-M2-009: visibility classes ---------------------------------------------------------
def test_active_in_stock_product_is_listed_and_buyable(admin, customer1):
    # TC-M2-009
    name = f"BB Visible {next(helpers._counter)}"
    pid = make_product(admin, stock=5, name=name)
    assert [p["id"] for p in products(search=name)["items"]] == [pid]
    clear_cart(customer1)
    assert add_to_cart(customer1, pid).status_code == 200


def test_inactive_product_hidden_from_customers_but_visible_to_admin(admin, customer1):
    # TC-M2-009
    name = f"BB Hidden {next(helpers._counter)}"
    pid = make_product(admin, active=False, name=name)
    assert call("GET", f"/catalog/products/{pid}").status_code == 404
    assert products(search=name)["items"] == []
    listed = call("GET", "/admin/products", admin, params={"search": name}).json()
    assert pid in [p["id"] for p in (listed["items"] if isinstance(listed, dict) else listed)]
    assert add_to_cart(customer1, pid).status_code == 404


def test_out_of_stock_product_listed_but_cannot_be_added(admin, customer1):
    # TC-M2-009
    pid = make_product(admin, stock=0)
    shown = call("GET", f"/catalog/products/{pid}")
    assert shown.status_code == 200 and shown.json()["stock"] == 0
    assert add_to_cart(customer1, pid).status_code == 400


# ---- TC-M3-013: cart classes ---------------------------------------------------------------
@pytest.fixture
def stocked_product(admin):
    return make_product(admin, price="50.00", stock=100)


@pytest.mark.parametrize("quantity,status", [
    P("TC-M3-013", "EP1-valid-quantity", 3, 200),
    P("TC-M3-013", "EP2-zero", 0, 422),
    P("TC-M3-013", "EP3-negative", -1, 422),
    P("TC-M3-013", "EP4-above-cap", 11, 422),
    P("TC-M3-013", "EP5-fractional", 1.5, 422),
    P("TC-M3-013", "EP6-text", "three", 422),
    P("TC-M3-013", "EP7-null", None, 422),
])
def test_cart_quantity_classes(customer1, stocked_product, quantity, status):
    clear_cart(customer1)
    r = call("POST", "/cart/items", customer1, json={"product_id": stocked_product, "quantity": quantity})
    assert r.status_code == status, r.text


def test_cart_unknown_product_is_404(customer1):
    assert add_to_cart(customer1, 999999).status_code == 404       # TC-M3-013 EP8


def test_cart_update_remove_and_clear_classes(customer1, stocked_product):
    # TC-M3-013
    clear_cart(customer1)
    item = add_to_cart(customer1, stocked_product, 2).json()["items"][0]["id"]
    assert call("PUT", f"/cart/items/{item}", customer1, json={"quantity": 5}).json()["items"][0]["quantity"] == 5   # EP9 update
    assert call("DELETE", f"/cart/items/{item}", customer1).json()["items"] == []                                   # EP10 remove
    assert call("DELETE", f"/cart/items/{item}", customer1).status_code == 404                                       # EP11 already gone
    assert call("DELETE", "/cart", customer1).json()["items"] == []                                                  # EP12 clear


# ---- TC-M4-017: coupon classes -------------------------------------------------------------
def apply(token, code):
    return call("POST", "/cart/coupon", token, json={"code": code})


def test_valid_coupon_for_first_order_customer(admin, customer2):
    # TC-M4-017
    cart_with_subtotal(admin, customer2, "250.00")
    r = apply(customer2, "WELCOME10")
    assert r.status_code == 200 and r.json()["coupon_code"] == "WELCOME10"
    assert Decimal(r.json()["discount"]) == Decimal("25.00")


def test_coupon_code_is_case_insensitive(admin, customer2):
    # TC-M4-017
    cart_with_subtotal(admin, customer2, "250.00")
    r = apply(customer2, "welcome10")
    assert r.status_code == 200 and r.json()["coupon_code"] == "WELCOME10"


@pytest.mark.parametrize("code,price,who,fragment", [
    P("TC-M4-017", "EP3-unknown-code", "NOSUCH", "250.00", "customer2", "not a valid coupon"),
    P("TC-M4-017", "EP4-expired", "OLD20", "250.00", "customer2", "expired"),
    P("TC-M4-017", "EP5-below-minimum", "FLAT50", "250.00", "customer2", "minimum"),
    P("TC-M4-017", "EP6-first-order-only-but-has-orders", "WELCOME10", "250.00", "customer1", "first-time"),
])
def test_rejected_coupon_classes_have_distinct_messages(request, admin, code, price, who, fragment):
    token = request.getfixturevalue(who)
    cart_with_subtotal(admin, token, price)
    r = apply(token, code)
    assert r.status_code == 400 and fragment in r.json()["message"].lower()
    assert call("GET", "/cart", token).json()["coupon_code"] is None      # nothing was applied


def test_second_coupon_replaces_the_first(admin, customer2):
    cart_with_subtotal(admin, customer2, "600.00")
    assert apply(customer2, "WELCOME10").json()["coupon_code"] == "WELCOME10"
    r = apply(customer2, "FLAT50")
    assert r.json()["coupon_code"] == "FLAT50" and Decimal(r.json()["discount"]) == Decimal("50.00")   # TC-M4-017 EP7


def test_weekday_coupon_on_a_weekday(admin, customer1):
    """FRESH15 is Monday-Friday only; the frozen test clock is a Tuesday."""
    cart_with_subtotal(admin, customer1, "900.00")
    r = apply(customer1, "FRESH15")
    assert r.status_code == 200 and Decimal(r.json()["discount"]) == Decimal("135.00")   # TC-M4-017 EP8
