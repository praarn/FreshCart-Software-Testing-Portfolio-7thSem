"""Diagnostic for test_add_product_to_wishlist: does navigating right after the heart click
lose the POST /wishlist/items request? Runs N iterations with and without waiting for the heart to fill.
Run from Test_Automation with the stack up:  python diagnostics/diag_wishlist_race.py [N]
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
from utils.config import BASE_URL, CUSTOMER2

N = int(sys.argv[1]) if len(sys.argv) > 1 else 6
o = Options()
o.add_argument("--headless=new")
d = webdriver.Chrome(options=o)
apple = api_client.product_id_by_name("Apple")
results = {"no_wait": 0, "wait_for_fill": 0}
for mode in results:
    for _ in range(N):
        api_client.reset_db()
        token = api_client.login(CUSTOMER2["email"], CUSTOMER2["password"])
        d.get(BASE_URL)
        d.execute_script("localStorage.setItem('fc_token', arguments[0]);", token)
        d.get(BASE_URL)
        WebDriverWait(d, 30).until(lambda x: x.find_elements(By.CSS_SELECTOR, '[data-testid="catalog-product-grid"] [data-testid^="product-card-"]'))
        btn = d.find_element(By.CSS_SELECTOR, f'[data-testid="wishlist-toggle-{apple}"]')
        btn.click()
        if mode == "wait_for_fill":
            WebDriverWait(d, 10).until(lambda x: "text-red-500" in x.find_element(By.CSS_SELECTOR, f'[data-testid="wishlist-toggle-{apple}"]').get_attribute("class"))
        d.get(BASE_URL + "/wishlist")
        time.sleep(1)
        saved = any(i["product"]["id"] == apple for i in api_client.get("/wishlist", token=token).json())
        results[mode] += saved
    print(f"{mode}: item saved in {results[mode]} of {N} iterations")
d.quit()
