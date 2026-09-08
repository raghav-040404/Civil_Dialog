from pydantic import BaseModel

from app.schemas.user import UserResponse


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class RegisterResponse(BaseModel):
    success: bool
    data: UserResponse


class LoginResponse(BaseModel):
    access_token: str
    token_type: str