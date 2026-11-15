"""Black-box helpers: every call goes through the public HTTP API, nothing imports application code.

The suite assumes the backend runs in test mode with the frozen clock used everywhere else in the
portfolio (APP_ENV=test FIXED_NOW=2026-11-10T09:00:00, a Tuesday).
"""
import itertools
import os
from datetime import datetime, timedelta

import requests

# 127.0.0.1 rather than localhost: on Windows "localhost" tries IPv6 first and every request stalls for seconds.
API = os.environ.get("FRESHCART_API_URL", "http://127.0.0.1:8000/api")
SESSION = requests.Session()   # keep-alive connection
NOW = datetime.fromisoformat(os.environ.get("FRESHCART_NOW", "2026-11-10T09:00:00"))

ADMIN = ("admin@freshcart.test", "Admin@1234")
DRIVER1 = ("driver1@freshcart.test", "Driver@1234")
CUSTOMER1 = ("customer1@freshcart.test", "Customer@1234")   # has past orders: not a first-order customer
CUSTOMER2 = ("customer2@freshcart.test", "Customer@1234")   # no orders: first-order coupon eligible

GOOD_ADDRESS = {"line1": "12 MG Road", "city": "Bengaluru", "pincode": "560050"}
COD = {"method": "COD"}

_rate_limited_calls = 0   # /auth/login and /auth/register allow 10 per minute per IP (R1.7)
_counter = itertools.count(1)


def reset() -> None:
    """Wipe and reseed the database; also clears the login/register rate limit (test mode only)."""
    global _rate_limited_calls
    SESSION.post(f"{API}/test/reset", timeout=30).raise_for_status()
    _rate_limited_calls = 0


def call(method: str, path: str, token: str | None = None, **kw) -> requests.Response:
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return SESSION.request(method, f"{API}{path}", headers=headers, timeout=20, **kw)


def rate_limited(method: str, path: str, **kw) -> requests.Response:
    """A call to a rate-limited endpoint; resets the database before the 10/min limit would be hit."""
    global _rate_limited_calls
    if _rate_limited_calls >= 8:
        reset()
    _rate_limited_calls += 1
    return call(method, path, **kw)


def login(account: tuple[str, str]) -> str:
    r = rate_limited("POST", "/auth/login", json={"email": account[0], "password": account[1]})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def unique_email(length: int | None = None) -> str:
    base = f"bb{next(_counter)}x{os.getpid()}"
    if length is None:
        return f"{base}@example.com"
    domain = "@x.co"
    return (base + "a" * length)[: length - len(domain)] + domain


def register_payload(**override) -> dict:
    body = {"name": "Jane Doe", "email": unique_email(), "password": "Pasw0rd1", "phone": "9123456780"}
    body.update(override)
    return body


def register(**override) -> requests.Response:
    return rate_limited("POST", "/auth/register", json=register_payload(**override))


# ---- catalog / cart helpers ------------------------------------------------------------------

def make_product(admin: str, price: str = "100.00", stock: int = 100, active: bool = True, **extra) -> int:
    body = {"name": f"BB Item {next(_counter)}", "price": price, "stock": stock, "unit": "kg",
            "category_id": 1, "active": active}
    body.update(extra)
    r = call("POST", "/admin/products", admin, json=body)
    assert r.status_code == 201, r.text
    return r.json()["id"]


def clear_cart(token: str) -> None:
    assert call("DELETE", "/cart", token).status_code == 200


def add_to_cart(token: str, product_id: int, quantity: int = 1) -> requests.Response:
    return call("POST", "/cart/items", token, json={"product_id": product_id, "quantity": quantity})


def cart_with_subtotal(admin: str, token: str, price: str, quantity: int = 1) -> dict:
    """Empty the cart, then fill it with one product so that the subtotal is price * quantity."""
    clear_cart(token)
    r = add_to_cart(token, make_product(admin, price), quantity)
    assert r.status_code == 200, r.text
    return r.json()


# ---- checkout helpers ------------------------------------------------------------------------

_slot_rotation = itertools.count()


def next_slot(token: str) -> str:
    """Rotate through the available slots so no slot reaches its capacity of 5 orders (R5.2)."""
    slots = [s for s in call("GET", "/checkout/slots", token).json() if s["available"]]
    most_free = max(s["remaining_capacity"] for s in slots)
    candidates = [s["slot_start"] for s in slots if s["remaining_capacity"] == most_free]
    return candidates[next(_slot_rotation) % len(candidates)]


def slot_at(day_offset: int, hour: int, minute: int = 0) -> str:
    d = (NOW.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=day_offset)).replace(hour=hour, minute=minute)
    return d.isoformat()


def checkout(token: str, address: dict | None = None, slot: str | None = None, payment: dict | None = None) -> requests.Response:
    return call("POST", "/checkout", token, json={
        "address": address or GOOD_ADDRESS,
        "slot_start": slot or next_slot(token),
        "payment": payment or COD,
    })


def place_order(admin: str, token: str, price: str = "100.00", quantity: int = 1) -> dict:
    cart_with_subtotal(admin, token, price, quantity)
    r = checkout(token)
    assert r.status_code == 201, r.text
    return r.json()


def driver1_id(admin: str) -> int:
    users = call("GET", "/admin/users", admin).json()
    return next(u["id"] for u in users if u["email"] == DRIVER1[0])


def advance_to_out_for_delivery(admin: str, driver: str, order_id: int) -> None:
    for status in ("CONFIRMED", "PACKED"):
        assert call("PATCH", f"/admin/orders/{order_id}/status", admin, json={"to_status": status}).status_code == 200
    r = call("POST", f"/admin/orders/{order_id}/assign-partner", admin, json={"delivery_partner_id": driver1_id(admin)})
    assert r.status_code == 200, r.text
    assert call("POST", f"/delivery/orders/{order_id}/dispatch", driver).status_code == 200


def field_names(response: requests.Response) -> list[str]:
    return [e["field"] for e in response.json().get("field_errors", [])]
