from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token
from app.db.repositories.user_repository import find_user_by_id
from app.utils.exceptions import AppException


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


async def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    payload = decode_access_token(token)

    if not payload:
        raise AppException(
            message="Invalid or expired authentication token.",
            code="INVALID_TOKEN",
            status_code=401
        )

    user_id = payload.get("sub")

    if not user_id:
        raise AppException(
            message="Invalid authentication token.",
            code="INVALID_TOKEN",
            status_code=401
        )

    try:
        user_id = int(user_id)
    except ValueError:
        raise AppException(
            message="Invalid authentication token.",
            code="INVALID_TOKEN",
            status_code=401
        )

    user = find_user_by_id(user_id)

    if not user:
        raise AppException(
            message="User associated with this token no longer exists.",
            code="USER_NOT_FOUND",
            status_code=401
        )

    return user

async def require_admin(
    current_user: dict = Depends(get_current_user)
):

    if current_user["role"] != "admin":
        raise AppException(
            message="Admin access is required.",
            code="ADMIN_ACCESS_REQUIRED",
            status_code=403
        )

    return current_user