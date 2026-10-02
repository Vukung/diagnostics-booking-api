from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.centres import router as centres_router

app = FastAPI(title="EVE Healthcare API", version="0.1.0")
app.include_router(auth_router)
app.include_router(centres_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}