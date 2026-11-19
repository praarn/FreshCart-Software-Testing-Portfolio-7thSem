"""Base Page Object: thin helpers over Selenium keyed on the frontend's data-testid
attributes (see ../../0. application/frontend/explanation.md#testability)."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from utils.config import BASE_URL, DEFAULT_TIMEOUT


def testid(value: str):
    return (By.CSS_SELECTOR, f'[data-testid="{value}"]')


class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def open(self, path: str = "/"):
        self.driver.get(f"{BASE_URL}{path}")
        return self

    def wait_visible(self, tid: str, timeout: int = DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(testid(tid)))

    def wait_present(self, tid: str, timeout: int = DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(testid(tid)))

    def wait_clickable(self, tid: str, timeout: int = DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(testid(tid)))

    def wait_gone(self, tid: str, timeout: int = DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until_not(EC.presence_of_element_located(testid(tid)))

    def wait_text_contains(self, tid: str, text: str, timeout: int = DEFAULT_TIMEOUT):
        return WebDriverWait(self.driver, timeout).until(EC.text_to_be_present_in_element(testid(tid), text))

    def find(self, tid: str):
        return self.driver.find_element(*testid(tid))

    def find_all(self, tid: str):
        return self.driver.find_elements(*testid(tid))

    def exists(self, tid: str) -> bool:
        return len(self.driver.find_elements(*testid(tid))) > 0

    def click(self, tid: str):
        self.wait_clickable(tid).click()
        return self

    def fill(self, tid: str, value: str):
        el = self.wait_visible(tid)
        el.clear()
        el.send_keys(value)
        return self

    def text(self, tid: str) -> str:
        return self.wait_visible(tid).text

    def select_by_value(self, tid: str, value: str, timeout: int = DEFAULT_TIMEOUT):
        """Options of these selects (categories, slots) are loaded asynchronously, so wait for the option."""
        from selenium.webdriver.support.ui import Select

        select = Select(self.wait_visible(tid))
        WebDriverWait(self.driver, timeout).until(lambda d: any(o.get_attribute("value") == value for o in select.options))
        select.select_by_value(value)
        return self

    def select_by_index(self, tid: str, index: int, timeout: int = DEFAULT_TIMEOUT):
        from selenium.webdriver.support.ui import Select

        select = Select(self.wait_visible(tid))
        WebDriverWait(self.driver, timeout).until(lambda d: len(select.options) > index)
        select.select_by_index(index)
        return self

    def screenshot(self, path: str):
        self.driver.save_screenshot(path)
        return self
