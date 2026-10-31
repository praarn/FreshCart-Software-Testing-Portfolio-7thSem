"""M3 — Cart (R3.1-R3.5)."""
from conftest import login_as
from pages.catalog_pages import CatalogPage
from pages.cart_checkout_pages import CartPage
from utils import api_client
from utils.config import CUSTOMER2


def test_add_item_within_quantity_range(driver):
    """TC-M3-001 (R3.1): adding 2 of an item succeeds."""
    login_as(driver, CUSTOMER2["email"], CUSTOMER2["password"])
    apple_id = api_client.product_id_by_name("Apple")
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    r = api_client.post("/cart/items", token=token, json={"product_id": apple_id, "quantity": 2})
    assert r.status_code == 200
    cart = CartPage(driver).open()
    cart.wait_visible("cart-summary")
    item = cart.find(f"cart-item-{r.json()['items'][0]['id']}")
    assert "2" in item.text


def test_add_quantity_above_stock_rejected(driver):
    """TC-M3-002 (R3.1, boundary): adding more than available stock is rejected."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    mango_id = api_client.product_id_by_name("Mango")  # seeded with stock=2
    r = api_client.post("/cart/items", token=token, json={"product_id": mango_id, "quantity": 3})
    assert r.status_code == 400


def test_readding_existing_item_increases_quantity(driver):
    """TC-M3-004 (R3.3): adding an item already in the cart increases its quantity."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    apple_id = api_client.product_id_by_name("Apple")
    api_client.post("/cart/items", token=token, json={"product_id": apple_id, "quantity": 2})
    r = api_client.post("/cart/items", token=token, json={"product_id": apple_id, "quantity": 1})
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 1
    assert items[0]["quantity"] == 3


def test_readding_beyond_cap_rejected_not_clamped(driver):
    """TC-M3-005 (R3.1/R3.3, boundary): re-adding beyond the 10-per-item cap is rejected,
    and the existing quantity is left unchanged (not silently clamped to 10)."""
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    apple_id = api_client.product_id_by_name("Apple")
    api_client.post("/cart/items", token=token, json={"product_id": apple_id, "quantity": 8})
    r = api_client.post("/cart/items", token=token, json={"product_id": apple_id, "quantity": 5})
    assert r.status_code == 400
    cart = api_client.get("/cart", token=token).json()
    assert cart["items"][0]["quantity"] == 8


def test_update_item_quantity_via_cart_page(driver):
    """TC-M3-006 (R3.4): the cart page quantity dropdown updates the line total."""
    login_as(driver, CUSTOMER2["email"], CUSTOMER2["password"])
    apple_id = api_client.product_id_by_name("Apple")
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    item = api_client.post("/cart/items", token=token, json={"product_id": apple_id, "quantity": 2}).json()["items"][0]

    cart = CartPage(driver).open()
    cart.wait_visible("cart-summary")
    cart.set_item_quantity(item["id"], 1)
    cart.wait_text_contains("cart-subtotal", "180.00")


def test_remove_item_from_cart(driver):
    """TC-M3-007 (R3.4): removing an item takes it out of the cart."""
    login_as(driver, CUSTOMER2["email"], CUSTOMER2["password"])
    apple_id = api_client.product_id_by_name("Apple")
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    item = api_client.post("/cart/items", token=token, json={"product_id": apple_id, "quantity": 1}).json()["items"][0]

    cart = CartPage(driver).open()
    cart.wait_visible("cart-summary")
    cart.remove_item(item["id"])
    cart.wait_visible("cart-empty")


def test_clear_cart(driver):
    """TC-M3-008 (R3.4): clearing the cart empties all items."""
    login_as(driver, CUSTOMER2["email"], CUSTOMER2["password"])
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    apple_id = api_client.product_id_by_name("Apple")
    banana_id = api_client.product_id_by_name("Banana")
    api_client.post("/cart/items", token=token, json={"product_id": apple_id, "quantity": 1})
    api_client.post("/cart/items", token=token, json={"product_id": banana_id, "quantity": 1})

    cart = CartPage(driver).open()
    cart.wait_visible("cart-summary")
    cart.clear_cart()
    cart.wait_visible("cart-empty")


def test_cart_totals_recalculate_on_change(driver):
    """TC-M3-009 (R3.5): changing quantity recalculates subtotal/delivery/total."""
    login_as(driver, CUSTOMER2["email"], CUSTOMER2["password"])
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    apple_id = api_client.product_id_by_name("Apple")  # price 180.00
    item = api_client.post("/cart/items", token=token, json={"product_id": apple_id, "quantity": 1}).json()["items"][0]

    cart = CartPage(driver).open()
    cart.wait_visible("cart-summary")
    assert "180.00" in cart.subtotal()
    cart.set_item_quantity(item["id"], 2)
    cart.wait_text_contains("cart-subtotal", "360.00")
