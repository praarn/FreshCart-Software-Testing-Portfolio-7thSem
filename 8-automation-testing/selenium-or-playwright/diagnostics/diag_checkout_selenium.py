"""Diagnostic: reproduce the TC-M5-001 timeout and print what the page shows and how long
each step takes. Run from 8-automation-testing/selenium-or-playwright with the stack up:  python diagnostics/diag_checkout_selenium.py
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from utils import api_client
from utils.config import BASE_URL, CUSTOMER2

o = Options()
o.add_argument("--headless=new")
o.add_argument("--window-size=1400,1000")
o.set_capability("goog:loggingPrefs", {"browser": "ALL"})
t0 = time.time()
d = webdriver.Chrome(options=o)
print(f"driver start {time.time()-t0:.1f}s")
api_client.reset_db()
token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
api_client.post("/cart/items", token=token, json={"product_id": api_client.product_id_by_name("Apple"), "quantity": 1})
d.get(BASE_URL)
d.execute_script("localStorage.setItem('fc_token', arguments[0]);", token)
for path in ("/", "/checkout"):
    t = time.time()
    d.get(BASE_URL + path)
    print(f"get {path}: {time.time()-t:.1f}s")
    for i in range(12):
        ids = d.execute_script("return [...document.querySelectorAll('[data-testid]')].map(e=>e.dataset.testid).slice(0,40)")
        print(f"  +{i}s url={d.current_url} testids={ids[:12]}")
        if "checkout-form" in ids:
            break
        time.sleep(1)
print("console:", [l["message"][:200] for l in d.get_log("browser")][:10])
d.quit()
