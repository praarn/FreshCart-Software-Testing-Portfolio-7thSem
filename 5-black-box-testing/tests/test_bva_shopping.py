"""Boundary value analysis, M2 pagination, M3 cart limits, M4 pricing. Exact values are reachable
because the admin API lets the test create a product at any price from 0.01 to 10000.00.

TC-M2-010 page size 10 and page range (R2.3)       TC-M3-014 quantity 1..10 (R3.1)
TC-M3-015 quantity vs stock (R3.1)                 TC-M3-016 re-add cap (R3.3)
TC-M3-017 distinct items 20 (R3.2)                 TC-M4-018 coupon minimum subtotal (R4.1)
TC-M4-019 coupon discount cap (R4.1, R4.4)         TC-M4-020 free-delivery threshold 299.00 (R4.3)
TC-M4-021 threshold applied after discount, rounding (R4.3, R4.4)
"""
import math
from decimal import Decimal

import pytest

import helpers
from helpers import add_to_cart, call, cart_with_subtotal, clear_cart, make_product


def P(tc, label, *values):
    return pytest.param(*values, id=f"{tc}-{label}")


D = Decimal


# ---- TC-M2-010: pagination -----------------------------------------------------------------
def test_page_size_and_page_range_boundaries():
    # TC-M2-010
    first = call("GET", "/catalog/products").json()
    total, last = first["total"], first["total_pages"]
    assert first["page_size"] == 10 and last == math.ceil(total / 10) and total > 10
    assert len(first["items"]) == 10                                                     # a full page
    tail = call("GET", "/catalog/products", params={"page": last}).json()
    assert len(tail["items"]) == total - 10 * (last - 1) and 1 <= len(tail["items"]) <= 10   # last page
    beyond = call("GET", "/catalog/products", params={"page": last + 1})
    assert beyond.status_code == 200 and beyond.json()["items"] == []                    # max+1: empty, not an error
    assert call("GET", "/catalog/products", params={"page": 0}).status_code == 422      # min-1
    assert call("GET", "/catalog/products", params={"page": -1}).status_code == 422


# ---- TC-M3-014: quantity -------------------------------------------------------------------
@pytest.fixture
def plenty(admin):
    return make_product(admin, price="20.00", stock=100)


@pytest.mark.parametrize("quantity,status", [
    P("TC-M3-014", "qty0-min-1", 0, 422), P("TC-M3-014", "qty1-min", 1, 200), P("TC-M3-014", "qty2-min+1", 2, 200),
    P("TC-M3-014", "qty9-max-1", 9, 200), P("TC-M3-014", "qty10-max", 10, 200), P("TC-M3-014", "qty11-max+1", 11, 422),
])
def test_add_quantity(customer1, plenty, quantity, status):
    clear_cart(customer1)
    assert add_to_cart(customer1, plenty, quantity).status_code == status


@pytest.mark.parametrize("quantity,status", [
    P("TC-M3-014", "update-qty0-min-1", 0, 422), P("TC-M3-014", "update-qty1-min", 1, 200),
    P("TC-M3-014", "update-qty10-max", 10, 200), P("TC-M3-014", "update-qty11-max+1", 11, 422),
])
def test_update_quantity(customer1, plenty, quantity, status):
    clear_cart(customer1)
    item = add_to_cart(customer1, plenty, 2).json()["items"][0]["id"]
    assert call("PUT", f"/cart/items/{item}", customer1, json={"quantity": quantity}).status_code == status


# ---- TC-M3-015: quantity versus stock ------------------------------------------------------
@pytest.mark.parametrize("stock,quantity,status", [
    P("TC-M3-015", "stock0-any-quantity", 0, 1, 400),
    P("TC-M3-015", "stock1-qty1-equal", 1, 1, 200),
    P("TC-M3-015", "stock1-qty2-over-by-one", 1, 2, 400),
    P("TC-M3-015", "stock3-qty2-under-by-one", 3, 2, 200),
    P("TC-M3-015", "stock3-qty3-equal", 3, 3, 200),
    P("TC-M3-015", "stock3-qty4-over-by-one", 3, 4, 400),
])
def test_quantity_against_stock(admin, customer1, stock, quantity, status):
    clear_cart(customer1)
    r = add_to_cart(customer1, make_product(admin, stock=stock), quantity)
    assert r.status_code == status, r.text
    if status == 400:
        assert call("GET", "/cart", customer1).json()["items"] == []     # rejected, nothing added


# ---- TC-M3-016: re-adding an item ----------------------------------------------------------
@pytest.mark.parametrize("first,second,status,final", [
    P("TC-M3-016", "5+5=10-at-cap", 5, 5, 200, 10),
    P("TC-M3-016", "8+2=10-at-cap", 8, 2, 200, 10),
    P("TC-M3-016", "8+3=11-over-cap", 8, 3, 400, 8),
    P("TC-M3-016", "8+5=13-over-cap", 8, 5, 400, 8),
])
def test_readd_is_capped_not_clamped(admin, customer1, first, second, status, final):
    clear_cart(customer1)
    pid = make_product(admin, stock=100)
    assert add_to_cart(customer1, pid, first).status_code == 200
    assert add_to_cart(customer1, pid, second).status_code == status
    assert call("GET", "/cart", customer1).json()["items"][0]["quantity"] == final


def test_readd_over_available_stock_is_rejected(admin, customer1):
    # TC-M3-016
    clear_cart(customer1)
    pid = make_product(admin, stock=5)
    assert add_to_cart(customer1, pid, 3).status_code == 200
    assert add_to_cart(customer1, pid, 3).status_code == 400       # 3+3=6 > stock 5 (cap 10 not reached)
    assert call("GET", "/cart", customer1).json()["items"][0]["quantity"] == 3


# ---- TC-M3-017: distinct items -------------------------------------------------------------
@pytest.fixture(scope="module")
def pool_of_21(admin):
    return [make_product(admin, price="10.00", stock=50) for _ in range(21)]


@pytest.mark.parametrize("count,status", [
    P("TC-M3-017", "19th-item-max-1", 19, 200), P("TC-M3-017", "20th-item-max", 20, 200), P("TC-M3-017", "21st-item-max+1", 21, 400),
])
def test_distinct_item_limit(customer1, pool_of_21, count, status):
    clear_cart(customer1)
    for pid in pool_of_21[: count - 1]:
        assert add_to_cart(customer1, pid).status_code == 200
    assert add_to_cart(customer1, pool_of_21[count - 1]).status_code == status
    assert len(call("GET", "/cart", customer1).json()["items"]) == (count if status == 200 else count - 1)
    clear_cart(customer1)


def test_adding_the_same_item_again_does_not_count_as_a_new_item(customer1, pool_of_21):
    # TC-M3-017
    clear_cart(customer1)
    for pid in pool_of_21[:20]:
        add_to_cart(customer1, pid)
    assert add_to_cart(customer1, pool_of_21[0]).status_code == 200      # 20 distinct, quantity of one rises to 2
    clear_cart(customer1)


# ---- TC-M4-018: coupon minimum subtotal ----------------------------------------------------
def apply(token, code):
    return call("POST", "/cart/coupon", token, json={"code": code})


@pytest.mark.parametrize("code,who,price,ok", [
    P("TC-M4-018", "WELCOME10-199.99-min-1", "WELCOME10", "customer2", "199.99", False),
    P("TC-M4-018", "WELCOME10-200.00-min", "WELCOME10", "customer2", "200.00", True),
    P("TC-M4-018", "WELCOME10-200.01-min+1", "WELCOME10", "customer2", "200.01", True),
    P("TC-M4-018", "FLAT50-499.99-min-1", "FLAT50", "customer1", "499.99", False),
    P("TC-M4-018", "FLAT50-500.00-min", "FLAT50", "customer1", "500.00", True),
    P("TC-M4-018", "FLAT50-500.01-min+1", "FLAT50", "customer1", "500.01", True),
    P("TC-M4-018", "FRESH15-799.99-min-1", "FRESH15", "customer1", "799.99", False),
    P("TC-M4-018", "FRESH15-800.00-min", "FRESH15", "customer1", "800.00", True),
    P("TC-M4-018", "FRESH15-800.01-min+1", "FRESH15", "customer1", "800.01", True),
])
def test_coupon_minimum_subtotal(request, admin, code, who, price, ok):
    token = request.getfixturevalue(who)
    cart_with_subtotal(admin, token, price)
    r = apply(token, code)
    assert r.status_code == (200 if ok else 400), r.text
    if not ok:
        assert "minimum" in r.json()["message"].lower()


# ---- TC-M4-019: discount cap (also checks ROUND_HALF_UP, R4.4) -----------------------------
@pytest.mark.parametrize("code,who,price,discount", [
    P("TC-M4-019", "WELCOME10-990-just-under-cap", "WELCOME10", "customer2", "990.00", "99.00"),
    P("TC-M4-019", "WELCOME10-1000-exactly-at-cap", "WELCOME10", "customer2", "1000.00", "100.00"),
    P("TC-M4-019", "WELCOME10-1010-just-over-cap", "WELCOME10", "customer2", "1010.00", "100.00"),
    P("TC-M4-019", "WELCOME10-2000-far-over-cap", "WELCOME10", "customer2", "2000.00", "100.00"),
    P("TC-M4-019", "FRESH15-990-just-under-cap", "FRESH15", "customer1", "990.00", "148.50"),
    P("TC-M4-019", "FRESH15-1000-exactly-at-cap", "FRESH15", "customer1", "1000.00", "150.00"),
    P("TC-M4-019", "FRESH15-1010-just-over-cap", "FRESH15", "customer1", "1010.00", "150.00"),
    P("TC-M4-019", "FLAT50-flat-amount", "FLAT50", "customer1", "500.00", "50.00"),
])
def test_discount_cap(request, admin, code, who, price, discount):
    token = request.getfixturevalue(who)
    cart_with_subtotal(admin, token, price)
    cart = apply(token, code).json()
    assert D(cart["discount"]) == D(discount)


# ---- TC-M4-020: free delivery threshold ----------------------------------------------------
@pytest.mark.parametrize("price,fee", [
    P("TC-M4-020", "0.01-min-product-price", "0.01", "40.00"),
    P("TC-M4-020", "298.99-min-1", "298.99", "40.00"),
    P("TC-M4-020", "299.00-min", "299.00", "0.00"),
    P("TC-M4-020", "299.01-min+1", "299.01", "0.00"),
])
def test_free_delivery_threshold(admin, customer1, price, fee):
    cart = cart_with_subtotal(admin, customer1, price)
    assert D(cart["delivery_fee"]) == D(fee)
    assert D(cart["total"]) == D(price) + D(fee)


# ---- TC-M4-021: threshold is tested after the discount; rounding is half-up ----------------
@pytest.mark.parametrize("price,discount,fee", [
    P("TC-M4-021", "332.21-after-discount-298.99", "332.21", "33.22", "40.00"),
    P("TC-M4-021", "332.22-after-discount-299.00", "332.22", "33.22", "0.00"),
    P("TC-M4-021", "332.23-after-discount-299.01", "332.23", "33.22", "0.00"),
    P("TC-M4-021", "half-up-20.005-to-20.01", "200.05", "20.01", "40.00"),
    P("TC-M4-021", "half-up-20.015-to-20.02", "200.15", "20.02", "40.00"),
])
def test_threshold_after_discount_and_half_up_rounding(admin, customer2, price, discount, fee):
    cart_with_subtotal(admin, customer2, price)
    cart = apply(customer2, "WELCOME10").json()
    assert D(cart["discount"]) == D(discount)
    assert D(cart["delivery_fee"]) == D(fee)
    assert D(cart["total"]) == D(price) - D(discount) + D(fee)
