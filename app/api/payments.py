import hashlib
import hmac
import secrets
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, DbSession
from app.core.config import get_settings
from app.models.models import Booking, BookingStatus, Payment, PaymentStatus, WebhookEvent
from app.schemas.payments import PaymentCreate, PaymentResponse, WebhookRequest, WebhookResponse
from app.services.booking_service import InvalidBookingTransition
from app.services.payment_service import apply_payment_status

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payload: PaymentCreate, db: DbSession, user: CurrentUser) -> Payment:
    booking = db.scalar(
        select(Booking)
        .where(Booking.id == payload.booking_id, Booking.user_id == user.id)
        .with_for_update()
    )
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if booking.status not in {BookingStatus.PENDING, BookingStatus.FAILED}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Booking is not payable")
    if payload.simulate not in {None, "success", "fail"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="simulate must be success or fail")

    if payload.simulate == "success":
        outcome = PaymentStatus.SUCCESS
    elif payload.simulate == "fail":
        outcome = PaymentStatus.FAILED
    else:
        outcome = secrets.choice([PaymentStatus.SUCCESS, PaymentStatus.FAILED])
    payment = Payment(
        booking_id=booking.id,
        amount=booking.amount,
        status=PaymentStatus.PENDING,
        provider_reference=f"sim_{secrets.token_urlsafe(18)}",
    )
    db.add(payment)
    try:
        db.flush()
        apply_payment_status(payment, booking, outcome)
        db.commit()
    except InvalidBookingTransition as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    db.refresh(payment)
    return payment


@router.post("/webhook/", response_model=WebhookResponse)
async def payment_webhook(
    payload: WebhookRequest,
    request: Request,
    db: DbSession,
    x_webhook_signature: str | None = Header(default=None),
) -> WebhookResponse:
    raw_body = await request.body()
    expected = hmac.new(get_settings().webhook_secret.encode(), raw_body, hashlib.sha256).hexdigest()
    if x_webhook_signature is None or not hmac.compare_digest(x_webhook_signature, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature")

    if db.get(WebhookEvent, payload.event_id) is not None:
        return WebhookResponse(detail="already processed")

    payment = db.scalar(
        select(Payment).where(Payment.provider_reference == payload.provider_reference).with_for_update()
    )
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    booking = db.scalar(select(Booking).where(Booking.id == payment.booking_id).with_for_update())
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    event = WebhookEvent(
        event_id=payload.event_id,
        payload=payload.model_dump(mode="json"),
    )
    db.add(event)
    try:
        apply_payment_status(payment, booking, payload.status)
        db.commit()
    except InvalidBookingTransition:
        db.rollback()
        return WebhookResponse(detail="ignored out-of-order event")
    except IntegrityError:
        db.rollback()
        return WebhookResponse(detail="already processed")
    return WebhookResponse(detail="processed")