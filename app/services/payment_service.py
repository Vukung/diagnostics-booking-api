from app.models.models import Booking, BookingStatus, Payment, PaymentStatus
from app.services.booking_service import InvalidBookingTransition, transition_booking


def apply_payment_status(payment: Payment, booking: Booking, status: PaymentStatus) -> None:
    if status == PaymentStatus.SUCCESS:
        if payment.status == PaymentStatus.SUCCESS or booking.status == BookingStatus.CONFIRMED:
            return
        transition_booking(booking, BookingStatus.CONFIRMED)
        payment.status = PaymentStatus.SUCCESS
        return

    if status == PaymentStatus.FAILED:
        if payment.status == PaymentStatus.SUCCESS or booking.status in {
            BookingStatus.CONFIRMED,
            BookingStatus.CANCELLED,
        }:
            return
        if booking.status == BookingStatus.PENDING:
            transition_booking(booking, BookingStatus.FAILED)
        payment.status = PaymentStatus.FAILED