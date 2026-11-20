"""Diagnostic for the flaky TC-M2-007: the catalog page sends one request per keystroke and applies whichever
response arrives last.  With 'Apple' deactivated, typing 'Apple' should end in the empty state; a stale response
for a shorter prefix ('A', 'Ap', ...) would leave products on screen.
    python diagnostics/diag_search_stale_response.py [N]
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from utils import api_client
from utils.config import ADMIN, BASE_URL

N = int(sys.argv[1]) if len(sys.argv) > 1 else 20
api_client.reset_db()
tok = api_client.login(ADMIN["email"], ADMIN["password"])
api_client.patch(f"/admin/products/{api_client.product_id_by_name('Apple')}/active", token=tok, json={"active": False})
o = Options()
o.add_argument("--headless=new")
d = webdriver.Chrome(options=o)
stale = 0
for i in range(N):
    d.get(BASE_URL)
    WebDriverWait(d, 30).until(lambda x: x.find_elements(By.CSS_SELECTOR, '[data-testid^="product-card-"]'))
    d.find_element(By.CSS_SELECTOR, '[data-testid="catalog-search-input"]').send_keys("Apple")
    time.sleep(3)
    empty = bool(d.find_elements(By.CSS_SELECTOR, '[data-testid="catalog-empty"]'))
    cards = len(d.find_elements(By.CSS_SELECTOR, '[data-testid^="product-card-"]'))
    if not empty:
        stale += 1
        print(f"load {i}: stale result on screen ({cards} cards, no empty state)")
print(f"{stale} of {N} loads ended with a stale list instead of the empty state")
d.quit()
