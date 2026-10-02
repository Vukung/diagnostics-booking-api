from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.models import PaymentStatus


class PaymentCreate(BaseModel):
    booking_id: UUID
    simulate: str | None = None


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    booking_id: UUID
    amount: Decimal
    status: PaymentStatus
    provider_reference: str


class WebhookRequest(BaseModel):
    event_id: str
    provider_reference: str
    status: PaymentStatus


class WebhookResponse(BaseModel):
    detail: str