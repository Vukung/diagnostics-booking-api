from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DbSession
from app.models.models import Booking, CentreTest, BookingStatus
from app.schemas.bookings import BookingCreate, BookingPage, BookingResponse, CancelResponse
from app.services.booking_service import InvalidBookingTransition, transition_booking

router = APIRouter(prefix="/bookings", tags=["bookings"])


def _owned_booking(booking_id: UUID, user_id: UUID, db: DbSession) -> Booking:
    booking = db.scalar(select(Booking).where(Booking.id == booking_id, Booking.user_id == user_id))
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return booking


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(payload: BookingCreate, db: DbSession, user: CurrentUser) -> Booking:
    if payload.appointment_at.tzinfo is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="appointment_at must include a timezone")
    if payload.appointment_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Appointment must be in the future")

    offered_test = db.scalar(
        select(CentreTest).where(
            CentreTest.centre_id == payload.centre_id,
            CentreTest.test_id == payload.test_id,
        )
    )
    if offered_test is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Test is not offered at this centre")

    booking = Booking(
        user_id=user.id,
        centre_id=payload.centre_id,
        test_id=payload.test_id,
        appointment_at=payload.appointment_at,
        amount=offered_test.price,
        status=BookingStatus.PENDING,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("", response_model=BookingPage)
def list_bookings(
    db: DbSession,
    user: CurrentUser,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> BookingPage:
    query = select(Booking).where(Booking.user_id == user.id)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    bookings = db.scalars(
        query.order_by(Booking.created_at.desc(), Booking.id).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return BookingPage(items=bookings, total=total, page=page, page_size=page_size)


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: UUID, db: DbSession, user: CurrentUser) -> Booking:
    return _owned_booking(booking_id, user.id, db)


@router.post("/{booking_id}/cancel", response_model=CancelResponse)
def cancel_booking(booking_id: UUID, db: DbSession, user: CurrentUser) -> CancelResponse:
    booking = _owned_booking(booking_id, user.id, db)
    try:
        transition_booking(booking, BookingStatus.CANCELLED)
    except InvalidBookingTransition as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    db.commit()
    db.refresh(booking)
    return CancelResponse(booking=booking)