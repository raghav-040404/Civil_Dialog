from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

from app.db.repositories.user_repository import (
    find_user_by_email,
    create_user
)

from app.utils.exceptions import AppException


async def register_user(
    name: str,
    email: str,
    password: str
):

    existing_user = find_user_by_email(email)

    if existing_user:
        raise AppException(
            message="A user with this email already exists.",
            code="EMAIL_ALREADY_REGISTERED",
            status_code=409
        )

    password_hash = hash_password(password)

    user = create_user(
        name=name.strip(),
        email=email,
        password_hash=password_hash
    )

    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"]
    }


async def authenticate_user(
    email: str,
    password: str
):

    user = find_user_by_email(email)

    if not user:
        raise AppException(
            message="Invalid email or password.",
            code="INVALID_CREDENTIALS",
            status_code=401
        )

    password_valid = verify_password(
        password,
        user["password_hash"]
    )

    if not password_valid:
        raise AppException(
            message="Invalid email or password.",
            code="INVALID_CREDENTIALS",
            status_code=401
        )

    access_token = create_access_token(
        user_id=user["id"]
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }