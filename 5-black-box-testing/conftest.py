import pytest

import helpers


@pytest.fixture(scope="session", autouse=True)
def _clean_database_once():
    helpers.reset()


@pytest.fixture(scope="session")
def admin():
    return helpers.login(helpers.ADMIN)


@pytest.fixture(scope="session")
def driver():
    return helpers.login(helpers.DRIVER1)


@pytest.fixture(scope="session")
def customer1():
    return helpers.login(helpers.CUSTOMER1)


@pytest.fixture(scope="session")
def customer2():
    return helpers.login(helpers.CUSTOMER2)


@pytest.fixture(scope="module")
def clean_module():
    """Modules that place many orders start from a clean database so slot capacity is not shared."""
    helpers.reset()


@pytest.fixture
def fresh_db():
    """For tests that change shared state (orders, OTP attempts, first-order status, lockout)."""
    helpers.reset()
    yield
    helpers.reset()   # leave no locked account or consumed first-order status behind for later tests


# ---- link every test to its test case ID(s) so the JUnit report can be grouped per TC ----------
import inspect
import re

_TC = re.compile(r"TC-M\d-\d{3}")


def pytest_collection_modifyitems(items):
    unnamed = []
    for item in items:
        ids = set(_TC.findall(item.name))
        if not ids:
            try:
                ids = set(_TC.findall(inspect.getsource(item.function)))
            except (OSError, TypeError):
                pass
        item.user_properties.append(("tc", ",".join(sorted(ids))))
        if not ids:
            unnamed.append(item.nodeid)
    if unnamed:
        listing = chr(10).join(unnamed)
        raise pytest.UsageError(f"tests that name no test case (TC-Mx-nnn) in their id or source:{chr(10)}{listing}")
