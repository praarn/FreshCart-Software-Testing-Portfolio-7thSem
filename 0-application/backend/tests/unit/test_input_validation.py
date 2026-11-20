"""Regression tests for DEF-005: '$' in the validation regexes matched before a trailing newline,
and '\d' matched non-ASCII digits, so values that are not exactly 'N ASCII digits' were stored.

White-box code review of the validation regexes: TC-M1-039."""
import pytest
from pydantic import ValidationError

from app.schemas.order import AddressIn, PaymentIn
from app.schemas.user import RegisterRequest

GOOD = dict(name="Jane Doe", email="jane@example.com", password="Passw0rd1", phone="9876543210")


def test_valid_registration_still_accepted():
    assert RegisterRequest(**GOOD).phone == "9876543210"


@pytest.mark.parametrize("field,value", [
    ("name", "Jane Doe\n"), ("phone", "9876543210\n"), ("phone", "9\u0968\u0969456789\u0966"),  # Devanagari digits
])
def test_register_rejects_trailing_newline_and_non_ascii_digits(field, value):
    with pytest.raises(ValidationError):
        RegisterRequest(**{**GOOD, field: value})


@pytest.mark.parametrize("pin", ["560050\n", "\u096b\u096c\u0966\u0966\u096b\u0966", "5600", "5600500"])
def test_pincode_rejects_non_exact_six_ascii_digits(pin):
    with pytest.raises(ValidationError):
        AddressIn(line1="12 Test Road", city="Bengaluru", pincode=pin)


@pytest.mark.parametrize("kw", [
    dict(method="UPI", upi_id="jane@okbank\n"),
    dict(method="CARD", card_number="4111111111111111\n", card_expiry="12/30", cvv="123"),
    dict(method="CARD", card_number="4111111111111111", card_expiry="12/30\n", cvv="123"),
    dict(method="CARD", card_number="4111111111111111", card_expiry="12/30", cvv="123\n"),
])
def test_payment_fields_reject_trailing_newline(kw):
    with pytest.raises(ValidationError):
        PaymentIn(**kw)
