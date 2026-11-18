import sys
from pathlib import Path

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils import api_client
from utils.config import API_URL, BASE_URL


def _check_servers_up():
    try:
        r = requests.get(f"{API_URL}/health", timeout=5)
        r.raise_for_status()
    except Exception as exc:
        pytest.exit(
            f"Backend not reachable at {API_URL} ({exc}). Start it with "
            f"APP_ENV=test FIXED_NOW=2026-11-10T09:00:00 uvicorn app.main:app --reload "
            f"(see ../commands.md)."
        )
    try:
        r = requests.get(BASE_URL, timeout=5)
        r.raise_for_status()
    except Exception as exc:
        pytest.exit(f"Frontend not reachable at {BASE_URL} ({exc}). Start it with `npm run dev`.")


@pytest.fixture(scope="session", autouse=True)
def _servers():
    _check_servers_up()


@pytest.fixture
def driver():
    """Function-scoped: a fresh Chrome session per test. Slower than sharing one browser for
    the whole run, but a single long-lived session across 80+ tests was observed to go
    unstable and eventually crash (InvalidSessionIdException) partway through a full run,
    cascading failures into every later test — per-test isolation trades some runtime for
    making that failure mode structurally impossible."""
    options = Options()
    options.add_argument("--window-size=1400,1000")
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    drv = webdriver.Chrome(options=options)
    yield drv
    drv.quit()


@pytest.fixture(autouse=True)
def reset_state(driver):
    """Runs before every test: wipes/reseeds the DB and clears the browser's auth state,
    so every test starts from the same known baseline regardless of execution order."""
    api_client.reset_db()
    driver.get(BASE_URL)
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear();")
    yield


def login_as(driver, email: str, password: str) -> str:
    """Fast, UI-free login: gets a token from the API and injects it into localStorage,
    then reloads so the app picks it up. Used as setup for tests whose subject is NOT the
    login form itself (that's covered directly by the M1 auth tests)."""
    token = api_client.login(email, password)
    driver.get(BASE_URL)
    driver.execute_script("window.localStorage.setItem('fc_token', arguments[0]);", token)
    driver.get(BASE_URL)
    return token
