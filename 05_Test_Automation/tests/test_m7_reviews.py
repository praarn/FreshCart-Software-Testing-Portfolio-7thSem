"""M7 — Reviews (R7.1)."""
from conftest import login_as
from pages.catalog_pages import ProductDetailPage
from utils import api_client
from utils.config import CUSTOMER1


def _deliver_apple_to_customer1():
    """customer1 has a seeded DELIVERED order containing Apple — see
    00_Application/backend/app/seed.py. Returns the Apple product id."""
    return api_client.product_id_by_name("Apple")


def test_review_delivered_product_succeeds(driver):
    """TC-M7-001 (R7.1): a customer can review a product from a delivered order."""
    apple_id = _deliver_apple_to_customer1()
    login_as(driver, CUSTOMER1["email"], CUSTOMER1["password"])
    page = ProductDetailPage(driver).open(apple_id)
    page.wait_visible("review-form")
    page.submit_review(5, "Fresh and crisp!")
    page.wait_visible("product-reviews-list", timeout=10)
    assert "Fresh and crisp" in page.text("product-reviews-list")


def test_cannot_review_never_delivered_product(driver):
    """TC-M7-002 (R7.1): reviewing a product never delivered to this customer is rejected."""
    banana_id = api_client.product_id_by_name("Banana")  # not part of customer1's delivered order
    login_as(driver, CUSTOMER1["email"], CUSTOMER1["password"])
    page = ProductDetailPage(driver).open(banana_id)
    page.wait_visible("review-form")
    page.submit_review(4, "Should fail")
    assert "delivered" in page.review_error().lower()


def test_cannot_review_same_product_twice(driver):
    """TC-M7-003 (R7.1): a customer cannot submit a second review for the same product."""
    apple_id = _deliver_apple_to_customer1()
    token = api_client.login(CUSTOMER1["email"], CUSTOMER1["password"])
    r1 = api_client.post("/reviews", token=token, json={"product_id": apple_id, "rating": 5, "comment": "first"})
    assert r1.status_code == 201
    r2 = api_client.post("/reviews", token=token, json={"product_id": apple_id, "rating": 3, "comment": "second"})
    assert r2.status_code == 409
