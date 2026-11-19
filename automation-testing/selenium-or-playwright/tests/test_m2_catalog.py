"""M2 — Catalog (R2.1-R2.4)."""
from decimal import Decimal

from pages.catalog_pages import CatalogPage
from utils import api_client


def test_catalog_lists_six_categories(driver):
    """TC-M2-001 (R2.1): at least the 6 required categories are seeded and shown."""
    page = CatalogPage(driver).open()
    page.wait_visible("category-showcase")
    names = {el.text for el in driver.find_elements("css selector", '[data-testid^="category-card-"]')}
    for expected in ["Fruits", "Vegetables", "Dairy", "Bakery", "Beverages", "Snacks"]:
        assert expected in names


def test_search_partial_case_insensitive(driver):
    """TC-M2-002 (R2.3): searching 'APP' (uppercase, partial) finds Apple."""
    page = CatalogPage(driver).open()
    page.search("APP")
    page.wait_visible("catalog-product-grid")
    apple_id = api_client.product_id_by_name("Apple")
    assert page.exists(f"product-card-{apple_id}")


def test_filter_by_category(driver):
    """TC-M2-003 (R2.3): filtering by category returns only that category's products."""
    r = api_client.get("/catalog/categories")
    fruits = next(c for c in r.json() if c["name"] == "Fruits")
    page = CatalogPage(driver).open()
    page.select_category_filter(fruits["id"])
    page.wait_visible("catalog-product-grid")

    products = api_client.get(f"/catalog/products?category_id={fruits['id']}").json()["items"]
    assert all(p["category_name"] == "Fruits" for p in products)
    assert len(products) > 0


def test_sort_price_ascending(driver):
    """TC-M2-004 (R2.3): sorting by price ascending orders results correctly."""
    page = CatalogPage(driver).open()
    page.sort_by("price_asc")
    page.wait_visible("catalog-product-grid")
    items = api_client.get("/catalog/products?sort=price_asc").json()["items"]
    prices = [Decimal(p["price"]) for p in items]
    assert prices == sorted(prices)


def test_pagination_ten_per_page(driver):
    """TC-M2-005 (R2.3): the catalog paginates at 10 items per page."""
    page = CatalogPage(driver).open()
    page.wait_visible("catalog-product-grid")
    assert page.product_grid_count() == 10
    assert "Page 1 of" in page.page_indicator_text()


def test_out_of_stock_visible_but_disabled(driver):
    """TC-M2-006 (R2.4): an out-of-stock product is shown with a disabled add-to-cart."""
    watermelon_id = api_client.product_id_by_name("Watermelon")
    page = CatalogPage(driver).open()
    page.search("Watermelon")
    page.wait_visible("catalog-product-grid")
    assert page.is_out_of_stock(watermelon_id)
    btn = page.find(f"add-to-cart-button-{watermelon_id}")
    assert btn.get_attribute("disabled") is not None


def test_inactive_product_hidden_from_customers(driver):
    """TC-M2-007 (R2.4): a product deactivated by admin disappears from the catalog."""
    from utils.config import ADMIN

    apple_id = api_client.product_id_by_name("Apple")
    admin_token = api_client.login(ADMIN["email"], ADMIN["password"])
    r = api_client.patch(f"/admin/products/{apple_id}/active", token=admin_token, json={"active": False})
    assert r.status_code == 200

    page = CatalogPage(driver).open()
    page.search("Apple")
    # Searching for a now-inactive, uniquely-named product returns zero results, so the
    # grid container itself collapses to zero height (Selenium treats a childless block
    # element as "not displayed") — wait on the empty-state message instead, which is the
    # precise, correctly-asserting signal that R2.4's "hidden from customers" held.
    page.wait_visible("catalog-empty")
    assert not page.exists(f"product-card-{apple_id}")

    detail_resp = api_client.get(f"/catalog/products/{apple_id}")
    assert detail_resp.status_code == 404
