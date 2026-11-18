from pages.base_page import BasePage


class CartPage(BasePage):
    def open(self):
        return super().open("/cart")

    def is_empty(self) -> bool:
        return self.exists("cart-empty")

    def set_item_quantity(self, item_id: int, qty: int):
        self.select_by_value(f"cart-item-qty-{item_id}", str(qty))
        return self

    def remove_item(self, item_id: int):
        self.click(f"cart-item-remove-{item_id}")
        return self

    def clear_cart(self):
        self.click("cart-clear-button")
        return self

    def apply_coupon(self, code: str):
        self.fill("coupon-code-input", code)
        self.click("coupon-apply-button")
        return self

    def remove_coupon(self):
        self.click("coupon-remove-button")
        return self

    def coupon_error(self) -> str:
        return self.text("coupon-error")

    def subtotal(self) -> str:
        return self.text("cart-subtotal")

    def discount(self) -> str:
        return self.text("cart-discount")

    def delivery_fee(self) -> str:
        return self.text("cart-delivery-fee")

    def total(self) -> str:
        return self.text("cart-total")

    def go_to_checkout(self):
        self.click("cart-checkout-link")
        return CheckoutPage(self.driver)


class CheckoutPage(BasePage):
    def open(self):
        return super().open("/checkout")

    def fill_address(self, line1: str, city: str, pincode: str):
        self.fill("checkout-line1-input", line1)
        self.fill("checkout-city-input", city)
        self.fill("checkout-pincode-input", pincode)
        return self

    def select_slot_by_index(self, index: int):
        self.select_by_index("checkout-slot-select", index)
        return self

    def pay_cod(self):
        self.select_by_value("checkout-payment-method-select", "COD")
        return self

    def pay_upi(self, upi_id: str):
        self.select_by_value("checkout-payment-method-select", "UPI")
        self.fill("checkout-upi-id-input", upi_id)
        return self

    def pay_card(self, number: str, expiry: str, cvv: str):
        self.select_by_value("checkout-payment-method-select", "CARD")
        self.fill("checkout-card-number-input", number)
        self.fill("checkout-card-expiry-input", expiry)
        self.fill("checkout-cvv-input", cvv)
        return self

    def submit(self):
        self.click("checkout-submit-button")
        return self

    def error_text(self) -> str:
        return self.text("checkout-form-error")
