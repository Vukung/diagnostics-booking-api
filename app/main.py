from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.bookings import router as bookings_router
from app.api.centres import router as centres_router
from app.api.payments import router as payments_router

app = FastAPI(title="EVE Healthcare API", version="0.1.0")
app.include_router(auth_router)
app.include_router(centres_router)
app.include_router(bookings_router)
app.include_router(payments_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}