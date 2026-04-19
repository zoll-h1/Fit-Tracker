import re
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=200)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, pattern=r"^(male|female|other)$")
    unit_system: str = Field("metric", pattern=r"^(metric|imperial)$")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    unit_system: str
    timezone: str
    language: str
    role: str
    is_active: bool
    is_email_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = Field(None, max_length=1000)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, pattern=r"^(male|female|other)$")
    height_cm: Optional[float] = Field(None, gt=0, le=300)
    weight_kg: Optional[float] = Field(None, gt=0, le=700)
    unit_system: Optional[str] = Field(None, pattern=r"^(metric|imperial)$")
    timezone: Optional[str] = Field(None, max_length=50)
    language: Optional[str] = Field(None, pattern=r"^(en|ru)$")


TokenResponse.model_rebuild()
