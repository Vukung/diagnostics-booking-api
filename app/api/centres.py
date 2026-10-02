from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from app.api.deps import CurrentAdmin, DbSession
from app.models.models import Centre, CentreTest, Test
from app.schemas.centres import CentreCreate, CentreDetail, CentrePage, CentreSummary, CentreTestCreate, TestResponse

router = APIRouter(prefix="/centres", tags=["centres"])


@router.get("", response_model=CentrePage)
def list_centres(
    db: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> CentrePage:
    total = db.scalar(select(func.count()).select_from(Centre)) or 0
    centres = db.scalars(
        select(Centre).order_by(Centre.name, Centre.id).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return CentrePage(items=centres, total=total, page=page, page_size=page_size)


@router.get("/{centre_id}", response_model=CentreDetail)
def get_centre(centre_id: UUID, db: DbSession) -> CentreDetail:
    centre = db.get(Centre, centre_id)
    if centre is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Centre not found")
    offered_tests = db.execute(
        select(Test, CentreTest.price)
        .join(CentreTest, CentreTest.test_id == Test.id)
        .where(CentreTest.centre_id == centre_id)
        .order_by(Test.name, Test.id)
    ).all()
    tests = [TestResponse(id=test.id, name=test.name, price=price) for test, price in offered_tests]
    return CentreDetail(id=centre.id, name=centre.name, location=centre.location, tests=tests)


@router.post("", response_model=CentreSummary, status_code=status.HTTP_201_CREATED)
def create_centre(payload: CentreCreate, db: DbSession, _admin: CurrentAdmin) -> Centre:
    centre = Centre(name=payload.name, location=payload.location)
    db.add(centre)
    db.commit()
    db.refresh(centre)
    return centre


@router.post("/{centre_id}/tests", response_model=TestResponse, status_code=status.HTTP_201_CREATED)
def add_test_to_centre(
    centre_id: UUID,
    payload: CentreTestCreate,
    db: DbSession,
    _admin: CurrentAdmin,
) -> TestResponse:
    if db.get(Centre, centre_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Centre not found")

    test = db.scalar(select(Test).where(func.lower(Test.name) == payload.name.lower()))
    if test is None:
        test = Test(name=payload.name)
        db.add(test)
        db.flush()

    if db.scalar(
        select(CentreTest).where(CentreTest.centre_id == centre_id, CentreTest.test_id == test.id)
    ) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Test is already offered at this centre")

    db.add(CentreTest(centre_id=centre_id, test_id=test.id, price=Decimal(payload.price)))
    db.commit()
    return TestResponse(id=test.id, name=test.name, price=payload.price)