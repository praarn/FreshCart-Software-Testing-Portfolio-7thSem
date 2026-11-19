import os

BASE_URL = os.environ.get("FRESHCART_BASE_URL", "http://localhost:3000")
API_URL = os.environ.get("FRESHCART_API_URL", "http://localhost:8000/api")
DEFAULT_TIMEOUT = 20

# Seed accounts (see application/backend/app/seed.py)
ADMIN = {"email": "admin@freshcart.test", "password": "Admin@1234"}
DRIVER1 = {"email": "driver1@freshcart.test", "password": "Driver@1234"}
DRIVER2 = {"email": "driver2@freshcart.test", "password": "Driver@1234"}
CUSTOMER1 = {"email": "customer1@freshcart.test", "password": "Customer@1234"}  # not first-order
CUSTOMER2 = {"email": "customer2@freshcart.test", "password": "Customer@1234"}  # first-order eligible

SERVICEABLE_PINCODE = "560050"
NON_SERVICEABLE_PINCODE = "560101"
