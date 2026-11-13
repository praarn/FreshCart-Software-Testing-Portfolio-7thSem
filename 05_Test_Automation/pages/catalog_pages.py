from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CatalogPage(BasePage):
    def open(self):
        return super().open("/")

    def search(self, term: str):
        self.fill("catalog-search-input", term)
        return self

    def select_category_filter(self, category_id: int):
        self.select_by_value("catalog-category-select", str(category_id))
        return self

    def sort_by(self, value: str):
        self.select_by_value("catalog-sort-select", value)
        return self

    def product_card(self, product_id: int):
        return self.find(f"product-card-{product_id}")

    def add_to_cart(self, product_id: int):
        self.click(f"add-to-cart-button-{product_id}")
        return self

    def toggle_wishlist(self, product_id: int):
        self.click(f"wishlist-toggle-{product_id}")
        return self

    def wait_wishlisted(self, product_id: int, timeout: int = 10):
        """Block until the heart has filled, i.e. POST /wishlist/items has completed. Navigating away
        earlier can abort the request (see diagnostics/diag_wishlist_race.py)."""
        from selenium.webdriver.support.ui import WebDriverWait

        WebDriverWait(self.driver, timeout).until(
            lambda d: "text-red-500" in self.find(f"wishlist-toggle-{product_id}").get_attribute("class")
        )
        return self

    def is_out_of_stock(self, product_id: int) -> bool:
        return self.exists(f"product-out-of-stock-{product_id}")

    def open_product(self, product_id: int):
        self.click(f"product-link-{product_id}")
        return ProductDetailPage(self.driver)

    def select_category_chip(self, category_id: int):
        self.click(f"category-card-{category_id}")
        return self

    def product_grid_count(self) -> int:
        self.wait_visible("catalog-product-grid")
        return len(self.driver.find_elements(By.CSS_SELECTOR, '[data-testid^="product-card-"]'))

    def next_page(self):
        self.click("catalog-next-page")
        return self

    def prev_page(self):
        self.click("catalog-prev-page")
        return self

    def page_indicator_text(self) -> str:
        return self.text("catalog-page-indicator")


class ProductDetailPage(BasePage):
    def open(self, product_id: int):
        return super().open(f"/product/{product_id}")

    def add_to_cart(self):
        self.click("product-detail-add-to-cart")
        return self

    def toggle_wishlist(self):
        self.click("product-detail-wishlist-toggle")
        return self

    def submit_review(self, rating: int, comment: str = ""):
        self.select_by_value("review-rating-select", str(rating))
        if comment:
            self.fill("review-comment-input", comment)
        self.click("review-submit-button")
        return self

    def review_error(self) -> str:
        return self.text("review-form-error")

    def is_out_of_stock(self) -> bool:
        return self.exists("product-detail-out-of-stock")
