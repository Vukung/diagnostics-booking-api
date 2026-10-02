from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CentreCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    location: str = Field(min_length=1, max_length=300)


class CentreTestCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class TestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    price: Decimal


class CentreSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    location: str


class CentreDetail(CentreSummary):
    tests: list[TestResponse]


class CentrePage(BaseModel):
    items: list[CentreSummary]
    total: int
    page: int
    page_size: int