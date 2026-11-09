"""Diagnostic: does navigating right after login_as() wipe the stored session?

AuthProvider.loadUser() calls GET /auth/me and, on ANY error, clears the token.  A navigation that aborts the
in-flight request therefore logs the user out.  This script repeats  login_as -> immediate driver.get  N times and
counts how often the token is gone afterwards.
    python diagnostics/diag_token_cleared_on_navigation.py [N]
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from conftest import login_as
from utils import api_client
from utils.config import BASE_URL, CUSTOMER2

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
o = Options()
o.add_argument("--headless=new")
d = webdriver.Chrome(options=o)
lost = 0
for i in range(N):
    api_client.reset_db()
    d.get(BASE_URL)
    d.delete_all_cookies()
    d.execute_script("window.localStorage.clear();")
    login_as(d, CUSTOMER2["email"], CUSTOMER2["password"])
    d.get(BASE_URL + "/")          # what the tests do next (CatalogPage.open(), CheckoutPage.open(), ...)
    time.sleep(3)
    if d.execute_script("return localStorage.getItem('fc_token')") is None:
        lost += 1
print(f"session token lost in {lost} of {N} iterations")
d.quit()
