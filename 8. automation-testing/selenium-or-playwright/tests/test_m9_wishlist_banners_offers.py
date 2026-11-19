"""M9 — Wishlist, banners and offers (R9.1-R9.3)."""
from conftest import login_as
from pages.admin_pages import AdminBannersPage
from pages.catalog_pages import CatalogPage
from pages.wishlist_page import WishlistPage
from utils import api_client
from utils.config import ADMIN, CUSTOMER2


def test_add_product_to_wishlist(driver):
    """TC-M9-001 (R9.1): clicking the heart icon adds a product to the wishlist."""
    apple_id = api_client.product_id_by_name("Apple")
    login_as(driver, CUSTOMER2["email"], CUSTOMER2["password"])
    page = CatalogPage(driver).open()
    page.wait_visible("catalog-product-grid")
    page.wait_visible("nav-logout-button")  # auth resolved; before that the heart redirects to /login (DEF-006)
    page.toggle_wishlist(apple_id)
    page.wait_wishlisted(apple_id)  # do not navigate before the save request completes

    wishlist = WishlistPage(driver).open()
    wishlist.wait_visible("wishlist-grid", timeout=10)
    assert wishlist.has_item(apple_id)


def test_duplicate_wishlist_add_rejected(driver):
    """TC-M9-002 (R9.1): adding the same product to the wishlist twice is rejected."""
    apple_id = api_client.product_id_by_name("Apple")
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    r1 = api_client.post("/wishlist/items", token=token, json={"product_id": apple_id})
    assert r1.status_code == 201
    r2 = api_client.post("/wishlist/items", token=token, json={"product_id": apple_id})
    assert r2.status_code == 409


def test_remove_from_wishlist(driver):
    """TC-M9-003 (R9.1): removing a wishlisted product works from the wishlist page."""
    apple_id = api_client.product_id_by_name("Apple")
    token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
    api_client.post("/wishlist/items", token=token, json={"product_id": apple_id})

    login_as(driver, CUSTOMER2["email"], CUSTOMER2["password"])
    page = WishlistPage(driver).open()
    page.wait_visible("wishlist-grid")
    page.remove(apple_id)
    page.wait_visible("wishlist-empty", timeout=10)


def test_only_active_banners_shown_publicly(driver):
    """TC-M9-004 (R9.2): an inactive banner does not appear in the public homepage carousel."""
    admin_token = api_client.login(ADMIN["email"], ADMIN["password"])
    r = api_client.post(
        "/admin/banners",
        token=admin_token,
        json={"title": "Inactive Test Banner", "image_url": "https://picsum.photos/seed/inactive/400/200", "active": False, "display_order": 99},
    )
    assert r.status_code == 201

    public_banners = api_client.get("/banners").json()
    assert all(b["title"] != "Inactive Test Banner" for b in public_banners)


def test_admin_banner_crud(driver):
    """TC-M9-005 (R9.2): admin can create, toggle, and delete a banner."""
    login_as(driver, ADMIN["email"], ADMIN["password"])
    page = AdminBannersPage(driver).open()
    page.wait_visible("admin-banner-create-form")
    before = page.row_count()
    page.create_banner("Automation Test Banner", "https://picsum.photos/seed/autotest/400/200")
    page.wait_visible("admin-banners-list")
    import time

    time.sleep(0.5)
    assert page.row_count() == before + 1

    banners = api_client.get("/admin/banners", token=api_client.login(ADMIN["email"], ADMIN["password"])).json()
    created = next(b for b in banners if b["title"] == "Automation Test Banner")
    page.toggle(created["id"])
    page.wait_text_contains(f"admin-banner-toggle-{created['id']}", "Inactive")
    page.delete(created["id"])
    time.sleep(0.5)
    assert page.row_count() == before


def test_offers_section_excludes_expired_coupon(driver):
    """TC-M9-006 (R9.3): the public offers list includes active coupons but excludes OLD20."""
    offers = api_client.get("/catalog/offers").json()
    codes = {o["code"] for o in offers}
    assert "WELCOME10" in codes
    assert "FLAT50" in codes
    assert "FRESH15" in codes
    assert "OLD20" not in codes

    page = CatalogPage(driver).open()
    page.wait_visible("offers-section")
    assert page.exists("offer-WELCOME10")
    assert not page.exists("offer-OLD20")
