from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.models import User


def main() -> None:
    email = "admin@example.com"
    db = SessionLocal()
    try:
        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            db.add(User(email=email, password_hash=hash_password("admin-password"), is_admin=True))
        else:
            user.is_admin = True
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()