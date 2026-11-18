from pages.base_page import BasePage


class DeliveryPage(BasePage):
    def open(self):
        return super().open("/delivery")

    def is_empty(self) -> bool:
        return self.exists("delivery-empty")

    def status_of(self, order_id: int) -> str:
        return self.text(f"delivery-order-status-{order_id}")

    def dispatch(self, order_id: int):
        self.click(f"delivery-dispatch-button-{order_id}")
        return self

    def deliver(self, order_id: int, otp: str):
        self.fill(f"delivery-otp-input-{order_id}", otp)
        self.click(f"delivery-deliver-button-{order_id}")
        return self

    def error_for(self, order_id: int) -> str:
        return self.text(f"delivery-order-error-{order_id}")

    def has_order(self, order_id: int) -> bool:
        return self.exists(f"delivery-order-{order_id}")
