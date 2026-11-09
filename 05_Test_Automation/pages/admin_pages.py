from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class AdminDashboardPage(BasePage):
    def open(self):
        return super().open("/admin")

    def orders_today(self) -> str:
        return self.text("dashboard-orders-today")

    def revenue_today(self) -> str:
        return self.text("dashboard-revenue-today")

    def low_stock_ids(self):
        self.wait_visible("dashboard-low-stock-list")
        rows = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid^="dashboard-low-stock-"]')
        return [r.get_attribute("data-testid").rsplit("-", 1)[-1] for r in rows]


class AdminProductsPage(BasePage):
    def open(self):
        return super().open("/admin/products")

    def create_product(self, name: str, price: str, stock: str, unit: str, category_id: int, description: str = ""):
        self.fill("admin-product-name-input", name)
        self.fill("admin-product-price-input", price)
        self.fill("admin-product-stock-input", stock)
        self.select_by_value("admin-product-unit-select", unit)
        self.select_by_value("admin-product-category-select", str(category_id))
        if description:
            self.fill("admin-product-description-input", description)
        self.click("admin-product-create-button")
        return self

    def create_error(self) -> str:
        return self.text("admin-product-create-error")

    def field_error(self, field: str) -> str:
        return self.text(f"admin-product-{field}-error")

    def set_stock(self, product_id: int, stock: str):
        el = self.wait_visible(f"admin-product-stock-input-{product_id}")
        el.clear()
        el.send_keys(stock)
        self.click(f"admin-product-stock-save-{product_id}")
        return self

    def toggle_active(self, product_id: int):
        self.click(f"admin-product-active-toggle-{product_id}")
        return self

    def active_label(self, product_id: int) -> str:
        return self.text(f"admin-product-active-toggle-{product_id}")

    def has_row(self, product_id: int) -> bool:
        return self.exists(f"admin-product-row-{product_id}")


class AdminOrdersPage(BasePage):
    def open(self):
        return super().open("/admin/orders")

    def filter_by_status(self, status: str):
        self.select_by_value("admin-order-status-filter", status)
        return self

    def status_of(self, order_id: int) -> str:
        return self.text(f"admin-order-status-{order_id}")

    def confirm(self, order_id: int):
        self.click(f"admin-order-confirm-{order_id}")
        return self

    def pack(self, order_id: int):
        self.click(f"admin-order-pack-{order_id}")
        return self

    def assign_partner(self, order_id: int, partner_label: str):
        from selenium.webdriver.support.ui import Select

        select_el = self.wait_visible(f"admin-order-partner-select-{order_id}")
        Select(select_el).select_by_visible_text(partner_label)
        self.click(f"admin-order-assign-{order_id}")
        return self

    def reset_otp(self, order_id: int):
        self.click(f"admin-order-reset-otp-{order_id}")
        return self

    def cancel(self, order_id: int):
        self.click(f"admin-order-cancel-{order_id}")
        return self

    def error_for(self, order_id: int) -> str:
        return self.text(f"admin-order-error-{order_id}")

    def has_row(self, order_id: int) -> bool:
        return self.exists(f"admin-order-row-{order_id}")

    def row_ids(self):
        self.wait_visible("admin-orders-list")
        rows = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid^="admin-order-row-"]')
        return [r.get_attribute("data-testid").rsplit("-", 1)[-1] for r in rows]


class AdminCouponsPage(BasePage):
    def open(self):
        return super().open("/admin/coupons")

    def toggle(self, coupon_id: int):
        self.click(f"admin-coupon-toggle-{coupon_id}")
        return self

    def status_label(self, coupon_id: int) -> str:
        return self.text(f"admin-coupon-toggle-{coupon_id}")

    def row_by_code(self, code: str):
        self.wait_visible("admin-coupons-table")
        rows = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid^="admin-coupon-row-"]')
        for r in rows:
            if code in r.text:
                return r
        raise AssertionError(f"coupon row for {code} not found")


class AdminUsersPage(BasePage):
    def open(self):
        return super().open("/admin/users")

    def status_of(self, user_id: int) -> str:
        return self.text(f"admin-user-status-{user_id}")

    def lock(self, user_id: int):
        self.click(f"admin-user-lock-{user_id}")
        return self

    def unlock(self, user_id: int):
        self.click(f"admin-user-unlock-{user_id}")
        return self

    def row_by_email(self, email: str):
        self.wait_visible("admin-users-table")
        rows = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid^="admin-user-row-"]')
        for r in rows:
            if email in r.text:
                return r, r.get_attribute("data-testid").rsplit("-", 1)[-1]
        raise AssertionError(f"user row for {email} not found")


class AdminBannersPage(BasePage):
    def open(self):
        return super().open("/admin/banners")

    def create_banner(self, title: str, image_url: str, link_url: str = "", display_order: str = "0"):
        self.fill("admin-banner-title-input", title)
        self.fill("admin-banner-image-url-input", image_url)
        if link_url:
            self.fill("admin-banner-link-url-input", link_url)
        el = self.wait_visible("admin-banner-display-order-input")
        el.clear()
        el.send_keys(display_order)
        self.click("admin-banner-create-button")
        return self

    def toggle(self, banner_id: int):
        self.click(f"admin-banner-toggle-{banner_id}")
        return self

    def delete(self, banner_id: int):
        self.click(f"admin-banner-delete-{banner_id}")
        return self

    def row_count(self) -> int:
        self.wait_visible("admin-banners-list")
        return len(self.driver.find_elements(By.CSS_SELECTOR, '[data-testid^="admin-banner-row-"]'))


class AdminAuditLogPage(BasePage):
    def open(self):
        return super().open("/admin/audit-log")

    def filter_by_order(self, order_id: int):
        self.fill("admin-audit-log-order-filter", str(order_id))
        return self

    def row_count(self) -> int:
        self.wait_visible("admin-audit-log-table")
        return len(self.driver.find_elements(By.CSS_SELECTOR, '[data-testid^="admin-audit-log-row-"]'))
