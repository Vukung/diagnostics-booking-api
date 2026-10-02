from app.models.models import Booking, BookingStatus


class InvalidBookingTransition(ValueError):
    pass


_ALLOWED_TRANSITIONS = {
    BookingStatus.PENDING: {BookingStatus.CONFIRMED, BookingStatus.FAILED, BookingStatus.CANCELLED},
    BookingStatus.FAILED: {BookingStatus.CONFIRMED},
    BookingStatus.CONFIRMED: {BookingStatus.CANCELLED},
    BookingStatus.CANCELLED: set(),
}


def transition_booking(booking: Booking, target: BookingStatus) -> Booking:
    if target not in _ALLOWED_TRANSITIONS[booking.status]:
        raise InvalidBookingTransition(f"Cannot transition booking from {booking.status} to {target}")
    booking.status = target
    return booking