from pages.base_page import BasePage


class LoginPage(BasePage):
    def open(self):
        return super().open("/login")

    def login(self, email: str, password: str):
        self.fill("login-email-input", email)
        self.fill("login-password-input", password)
        self.click("login-submit-button")
        return self

    def error_text(self) -> str:
        return self.text("login-form-error")


class RegisterPage(BasePage):
    def open(self):
        return super().open("/register")

    def register(self, name: str, email: str, password: str, phone: str):
        self.fill("register-name-input", name)
        self.fill("register-email-input", email)
        self.fill("register-password-input", password)
        self.fill("register-phone-input", phone)
        self.click("register-submit-button")
        return self

    def field_error(self, field: str) -> str:
        return self.text(f"register-{field}-error")
