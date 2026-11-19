from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class OrdersPage(BasePage):
    def open(self):
        return super().open("/orders")

    def is_empty(self) -> bool:
        return self.exists("orders-empty")

    def open_order(self, order_id: int):
        self.click(f"order-row-{order_id}")
        return OrderDetailPage(self.driver)

    def status_of(self, order_id: int) -> str:
        return self.text(f"order-status-{order_id}")


class OrderDetailPage(BasePage):
    def open(self, order_id: int):
        return super().open(f"/orders/{order_id}")

    def order_number(self) -> str:
        return self.text("order-detail-number")

    def status(self) -> str:
        return self.text("order-detail-status")

    def otp(self) -> str:
        text = self.text("order-delivery-otp")
        digits = "".join(c for c in text if c.isdigit())
        return digits[-4:]

    def cancel(self):
        self.click("order-cancel-button")
        return self

    def can_cancel(self) -> bool:
        return self.exists("order-cancel-button")

    def timeline_entries(self):
        self.wait_visible("order-timeline")
        return self.driver.find_elements(By.CSS_SELECTOR, '[data-testid^="order-timeline-entry-"]')

    def wait_for_live_update(self, timeout: int = 10):
        return self.wait_visible("order-live-note", timeout=timeout)
