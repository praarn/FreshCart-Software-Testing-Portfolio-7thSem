"""Thin wrapper around the backend REST API, used for fast test setup/teardown and for
backend-truth assertions (e.g. "did stock actually decrement"). The UI is still what's
under test in each test body — this just avoids re-driving the UI for pure fixture setup
like "log in as X" or "reset the database", which is standard automation practice."""
import requests

from utils.config import API_URL


def reset_db() -> None:
    r = requests.post(f"{API_URL}/test/reset", timeout=10)
    r.raise_for_status()


def login(email: str, password: str) -> str:
    r = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password}, timeout=10)
    r.raise_for_status()
    return r.json()["access_token"]


def get(path: str, token: str | None = None, **kwargs):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return requests.get(f"{API_URL}{path}", headers=headers, timeout=10, **kwargs)


def post(path: str, token: str | None = None, json=None, **kwargs):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return requests.post(f"{API_URL}{path}", headers=headers, json=json, timeout=10, **kwargs)


def patch(path: str, token: str | None = None, json=None, **kwargs):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return requests.patch(f"{API_URL}{path}", headers=headers, json=json, timeout=10, **kwargs)


def put(path: str, token: str | None = None, json=None, **kwargs):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return requests.put(f"{API_URL}{path}", headers=headers, json=json, timeout=10, **kwargs)


def product_id_by_name(name: str) -> int:
    r = get(f"/catalog/products?search={name}")
    r.raise_for_status()
    items = r.json()["items"]
    match = next(p for p in items if p["name"].lower() == name.lower())
    return match["id"]
