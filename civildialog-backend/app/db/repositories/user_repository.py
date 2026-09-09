from typing import Optional

from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.user import User

# NOTE: function names and signatures (find_user_by_email, find_user_by_id,
# create_user) are unchanged from the original in-memory implementation.
# app/services/auth_service.py, app/core/dependencies.py and
# app/api/users.py all call these and read the result via dict
# subscripting (e.g. current_user["role"]), so each function here returns
# a plain dict shaped exactly like the old in-memory user record — no
# caller needed to change.
#
# Each function opens and closes its own short-lived session rather than
# taking a `db: Session` parameter, so no call site above this layer
# needs to change to pass one through.


def _to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "password_hash": user.password_hash,
        "role": user.role,
    }


def find_user_by_email(email: str) -> Optional[dict]:
    with SessionLocal() as db:
        user = db.scalar(
            select(User).where(User.email == email.lower())
        )

        return _to_dict(user) if user else None


def find_user_by_id(user_id: int) -> Optional[dict]:
    with SessionLocal() as db:
        user = db.get(User, user_id)

        return _to_dict(user) if user else None


def create_user(
    name: str,
    email: str,
    password_hash: str,
    role: str = "user"
) -> dict:
    with SessionLocal() as db:
        user = User(
            name=name,
            email=email.lower(),
            password_hash=password_hash,
            role=role
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return _to_dict(user)
