from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.models.models import Booking, BookingStatus, Payment, PaymentStatus
from app.services.booking_service import InvalidBookingTransition, transition_booking
from app.services.payment_service import apply_payment_status


def make_booking(status: BookingStatus = BookingStatus.PENDING) -> Booking:
    return Booking(
        user_id=uuid4(),
        centre_id=uuid4(),
        test_id=uuid4(),
        appointment_at=datetime.now(timezone.utc),
        amount=Decimal("25.00"),
        status=status,
    )


def test_failed_booking_can_be_confirmed() -> None:
    booking = make_booking(BookingStatus.FAILED)

    transition_booking(booking, BookingStatus.CONFIRMED)

    assert booking.status == BookingStatus.CONFIRMED


def test_cancelled_booking_is_terminal() -> None:
    booking = make_booking(BookingStatus.CANCELLED)

    with pytest.raises(InvalidBookingTransition):
        transition_booking(booking, BookingStatus.CONFIRMED)


def test_successful_payment_confirms_booking() -> None:
    booking = make_booking()
    payment = Payment(
        booking_id=uuid4(),
        amount=booking.amount,
        status=PaymentStatus.PENDING,
        provider_reference="provider-ref",
    )

    apply_payment_status(payment, booking, PaymentStatus.SUCCESS)

    assert booking.status == BookingStatus.CONFIRMED
    assert payment.status == PaymentStatus.SUCCESS


def test_failed_payment_marks_pending_booking_failed() -> None:
    booking = make_booking()
    payment = Payment(
        booking_id=uuid4(),
        amount=booking.amount,
        status=PaymentStatus.PENDING,
        provider_reference="failed-provider-ref",
    )

    apply_payment_status(payment, booking, PaymentStatus.FAILED)

    assert booking.status == BookingStatus.FAILED
    assert payment.status == PaymentStatus.FAILED


def test_failure_after_success_is_ignored() -> None:
    booking = make_booking(BookingStatus.CONFIRMED)
    payment = Payment(
        booking_id=uuid4(),
        amount=booking.amount,
        status=PaymentStatus.SUCCESS,
        provider_reference="success-provider-ref",
    )

    apply_payment_status(payment, booking, PaymentStatus.FAILED)

    assert booking.status == BookingStatus.CONFIRMED
    assert payment.status == PaymentStatus.SUCCESS