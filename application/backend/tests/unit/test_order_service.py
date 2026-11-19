"""White-box tests for app/services/order_service.py (R6.1-R6.4).

White-box method 1, basis path testing: TC-M6-020 (complete_delivery, V(G) = 7, 6 feasible paths).
White-box method 2, statement/branch/condition coverage: TC-M6-021 (complete_delivery, admin_advance_status,
assign_delivery_partner, cancel_order)."""
import itertools

import pytest

from app.core.errors import BadRequestError, ConflictError, ForbiddenError
from app.models.enums import OrderStatus, Role
from app.services import order_service
from tests.unit.conftest import NOW, make_order, make_user

ALLOWED = {(OrderStatus.PLACED, OrderStatus.CONFIRMED), (OrderStatus.CONFIRMED, OrderStatus.PACKED)}
ALL_PAIRS = list(itertools.product(OrderStatus, OrderStatus))


@pytest.mark.parametrize("frm,to", ALL_PAIRS, ids=[f"{a.value}->{b.value}" for a, b in ALL_PAIRS])
async def test_admin_transition_matrix(db, frm, to):
    """All 36 (from, to) pairs: only PLACED->CONFIRMED and CONFIRMED->PACKED succeed (R6.1, R6.3)."""
    admin = await make_user(db, Role.ADMIN, "a@x.test")
    customer = await make_user(db, Role.CUSTOMER, "c@x.test")
    order = await make_order(db, customer.id, status=frm)
    if (frm, to) in ALLOWED:
        assert (await order_service.admin_advance_status(db, order.id, to, admin, NOW)).status == to
    else:
        with pytest.raises(ConflictError):
            await order_service.admin_advance_status(db, order.id, to, admin, NOW)
        assert order.status == frm


async def _out_for_delivery(db, **kw):
    partner = await make_user(db, Role.DELIVERY_PARTNER, "d@x.test")
    customer = await make_user(db, Role.CUSTOMER, "c@x.test")
    order = await make_order(db, customer.id, status=OrderStatus.OUT_FOR_DELIVERY, delivery_partner_id=partner.id, **kw)
    return partner, order


async def test_complete_delivery_wrong_partner(db):  # path 1
    _, order = await _out_for_delivery(db)
    other = await make_user(db, Role.DELIVERY_PARTNER, "d2@x.test")
    with pytest.raises(ForbiddenError):
        await order_service.complete_delivery(db, order.id, other, "1234", NOW)


async def test_complete_delivery_wrong_status(db):  # path 2
    partner = await make_user(db, Role.DELIVERY_PARTNER, "d@x.test")
    customer = await make_user(db, Role.CUSTOMER, "c@x.test")
    order = await make_order(db, customer.id, status=OrderStatus.PACKED, delivery_partner_id=partner.id)
    with pytest.raises(ConflictError, match="Cannot deliver"):
        await order_service.complete_delivery(db, order.id, partner, "1234", NOW)


async def test_complete_delivery_blocked_even_with_correct_otp(db):  # path 3
    partner, order = await _out_for_delivery(db, otp_blocked=True, otp_attempts=3)
    with pytest.raises(ConflictError, match="Too many incorrect OTP"):
        await order_service.complete_delivery(db, order.id, partner, "1234", NOW)


async def test_complete_delivery_wrong_otp_attempts_remain(db):  # path 4: attempts 1 and 2
    partner, order = await _out_for_delivery(db)
    with pytest.raises(BadRequestError, match="2 attempt"):
        await order_service.complete_delivery(db, order.id, partner, "0000", NOW)
    with pytest.raises(BadRequestError, match="1 attempt"):
        await order_service.complete_delivery(db, order.id, partner, "0000", NOW)
    assert order.otp_attempts == 2 and order.otp_blocked is False


async def test_complete_delivery_third_wrong_otp_blocks(db):  # path 5, TC-M6-009
    partner, order = await _out_for_delivery(db)
    for _ in range(2):
        with pytest.raises(BadRequestError):
            await order_service.complete_delivery(db, order.id, partner, "0000", NOW)
    with pytest.raises(ConflictError, match="No attempts remaining"):
        await order_service.complete_delivery(db, order.id, partner, "0000", NOW)
    assert order.otp_blocked is True
    with pytest.raises(ConflictError, match="Too many"):
        await order_service.complete_delivery(db, order.id, partner, "1234", NOW)


async def test_complete_delivery_success(db):  # path 6, TC-M6-008
    partner, order = await _out_for_delivery(db)
    result = await order_service.complete_delivery(db, order.id, partner, "1234", NOW)
    assert result.status == OrderStatus.DELIVERED and result.delivered_at == NOW


async def test_admin_reset_then_deliver(db):  # TC-M6-010
    partner, order = await _out_for_delivery(db)
    admin = await make_user(db, Role.ADMIN, "a@x.test")
    for _ in range(2):
        with pytest.raises(BadRequestError):
            await order_service.complete_delivery(db, order.id, partner, "0000", NOW)
    with pytest.raises(ConflictError):
        await order_service.complete_delivery(db, order.id, partner, "0000", NOW)
    await order_service.reset_otp_attempts(db, order.id, admin, NOW)
    assert (await order_service.complete_delivery(db, order.id, partner, "1234", NOW)).status == OrderStatus.DELIVERED


@pytest.mark.parametrize("status,ok", [
    (OrderStatus.PLACED, True), (OrderStatus.CONFIRMED, True), (OrderStatus.PACKED, False),
    (OrderStatus.OUT_FOR_DELIVERY, False), (OrderStatus.DELIVERED, False), (OrderStatus.CANCELLED, False),
])
async def test_customer_cancel_allowed_only_in_placed_or_confirmed(db, status, ok):  # R6.2
    customer = await make_user(db, Role.CUSTOMER, "c@x.test")
    order = await make_order(db, customer.id, status=status)
    if ok:
        assert (await order_service.cancel_order(db, order.id, customer, NOW)).status == OrderStatus.CANCELLED
    else:
        with pytest.raises(ConflictError):
            await order_service.cancel_order(db, order.id, customer, NOW)


async def test_cancel_by_other_customer_forbidden(db):  # R6.6
    owner = await make_user(db, Role.CUSTOMER, "c@x.test")
    other = await make_user(db, Role.CUSTOMER, "c2@x.test")
    order = await make_order(db, owner.id)
    with pytest.raises(ForbiddenError):
        await order_service.cancel_order(db, order.id, other, NOW)


async def test_assign_partner_requires_packed_and_a_partner(db):  # TC-M6-006
    admin = await make_user(db, Role.ADMIN, "a@x.test")
    partner = await make_user(db, Role.DELIVERY_PARTNER, "d@x.test")
    customer = await make_user(db, Role.CUSTOMER, "c@x.test")
    confirmed = await make_order(db, customer.id, status=OrderStatus.CONFIRMED, number="FC-1")
    with pytest.raises(ConflictError, match="PACKED"):
        await order_service.assign_delivery_partner(db, confirmed.id, partner.id, admin, NOW)
    packed = await make_order(db, customer.id, status=OrderStatus.PACKED, number="FC-2")
    with pytest.raises(BadRequestError, match="not a delivery partner"):
        await order_service.assign_delivery_partner(db, packed.id, customer.id, admin, NOW)
    assert (await order_service.assign_delivery_partner(db, packed.id, partner.id, admin, NOW)).delivery_partner_id == partner.id


async def test_admin_can_cancel_another_customers_order(db):  # is_admin=True skips the ownership check (not in R6.2 text)
    owner = await make_user(db, Role.CUSTOMER, "c@x.test")
    admin = await make_user(db, Role.ADMIN, "a@x.test")
    order = await make_order(db, owner.id, status=OrderStatus.CONFIRMED)
    result = await order_service.cancel_order(db, order.id, admin, NOW, is_admin=True)
    assert result.status == OrderStatus.CANCELLED and result.cancelled_at == NOW
