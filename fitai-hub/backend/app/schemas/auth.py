from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    username: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v

    @field_validator("username")
    @classmethod
    def username_valid(cls, v):
        if len(v) < 3:
            raise ValueError("El username debe tener al menos 3 caracteres")
        if not v.replace("_", "").replace(".", "").isalnum():
            raise ValueError("El username solo puede contener letras, números, _ y .")
        return v.lower()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserBasicResponse"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserBasicResponse(BaseModel):
    id: str
    email: str
    name: str
    username: str
    role: str
    avatar_url: Optional[str] = None
    is_verified: bool

    class Config:
        from_attributes = True


TokenResponse.model_rebuild()