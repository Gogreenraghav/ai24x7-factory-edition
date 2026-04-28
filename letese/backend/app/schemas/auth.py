# Auth schemas - Pydantic models for request/response
from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


# ---- Auth Schemas ----

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: str
    firm_name: str
    bar_council_no: Optional[str] = None
    subdomain: str  # e.g. "sharmaadvocates"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    tenant_id: str
    role: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: str
    tenant_id: UUID
    is_verified: bool

    class Config:
        from_attributes = True


class TenantResponse(BaseModel):
    id: UUID
    name: str
    email: str
    subdomain: str
    plan: str
    is_active: bool

    class Config:
        from_attributes = True
