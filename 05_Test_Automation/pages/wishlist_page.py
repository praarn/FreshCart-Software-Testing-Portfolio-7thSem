from pages.base_page import BasePage


class WishlistPage(BasePage):
    def open(self):
        return super().open("/wishlist")

    def is_empty(self) -> bool:
        return self.exists("wishlist-empty")

    def has_item(self, product_id: int) -> bool:
        return self.exists(f"wishlist-item-{product_id}")

    def remove(self, product_id: int):
        self.click(f"wishlist-remove-{product_id}")
        return self

    def add_to_cart(self, product_id: int):
        self.click(f"wishlist-add-to-cart-{product_id}")
        return self
