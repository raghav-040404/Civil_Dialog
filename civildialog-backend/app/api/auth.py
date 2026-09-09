from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.user import UserRegister
from app.schemas.auth import (
    RegisterResponse,
    LoginResponse
)

from app.services.auth_service import (
    register_user,
    authenticate_user
)


router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=201
)
async def register(request: UserRegister):

    user = await register_user(
        name=request.name,
        email=str(request.email),
        password=request.password
    )

    return {
        "success": True,
        "data": user
    }


@router.post(
    "/login",
    response_model=LoginResponse
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    token = await authenticate_user(
        email=form_data.username,
        password=form_data.password
    )

    return token