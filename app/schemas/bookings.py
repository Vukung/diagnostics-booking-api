from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.models import BookingStatus


class BookingCreate(BaseModel):
    centre_id: UUID
    test_id: UUID
    appointment_at: datetime


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    centre_id: UUID
    test_id: UUID
    appointment_at: datetime
    amount: Decimal
    status: BookingStatus
    created_at: datetime


class BookingPage(BaseModel):
    items: list[BookingResponse]
    total: int
    page: int
    page_size: int


class CancelResponse(BaseModel):
    booking: BookingResponse
    detail: str = Field(default="Booking cancelled")