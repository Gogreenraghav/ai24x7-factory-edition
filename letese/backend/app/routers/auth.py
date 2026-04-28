# Auth router - /api/v1/auth/*
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.database import get_db
from app.core.security import (
    get_password_hash, verify_password, 
    create_tokens, decode_token
)
from app.models.tenant import Tenant, PlanEnum
from app.models.user import User, UserRole
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse,
    RefreshRequest, UserResponse, TenantResponse
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register new tenant (law firm) + first user (advocate admin)."""
    
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create tenant
    tenant = Tenant(
        id=uuid.uuid4(),
        name=data.firm_name,
        email=data.email,
        subdomain=data.subdomain.lower().replace(" ", "-"),
        plan=PlanEnum.BASIC.value,
        case_limit=30,
    )
    db.add(tenant)
    await db.flush()
    
    # Create first user (advocate admin)
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        email=data.email,
        password_hash=get_password_hash(data.password),
        full_name=data.full_name,
        phone=data.phone,
        role=UserRole.ADVOCATE_ADMIN.value,
        bar_council_no=data.bar_council_no,
        is_verified=True,  # For MVP, skip OTP
    )
    db.add(user)
    await db.commit()
    
    # Generate tokens
    tokens = create_tokens(
        user_id=str(user.id),
        tenant_id=str(tenant.id),
        role=user.role
    )
    
    return TokenResponse(
        **tokens,
        user_id=str(user.id),
        tenant_id=str(tenant.id),
        role=user.role
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login with email + password."""
    
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    
    # Get tenant
    tenant_result = await db.execute(select(Tenant).where(Tenant.id == user.tenant_id))
    tenant = tenant_result.scalar_one_or_none()
    
    if not tenant or not tenant.is_active:
        raise HTTPException(status_code=403, detail="Firm account is disabled")
    
    # Generate tokens
    tokens = create_tokens(
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        role=user.role
    )
    
    return TokenResponse(
        **tokens,
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        role=user.role
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token."""
    
    payload = decode_token(data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    
    # Get user
    result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    tokens = create_tokens(
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        role=user.role
    )
    
    return TokenResponse(**tokens, user_id=str(user.id), tenant_id=str(user.tenant_id), role=user.role)


@router.get("/me", response_model=UserResponse)
async def get_me(
    db: AsyncSession = Depends(get_db),
    tenant_info: dict = Depends(__import__('app.middleware.tenant', fromlist=['get_current_tenant']).get_current_tenant)
):
    """Get current user profile."""
    
    result = await db.execute(select(User).where(User.id == uuid.UUID(tenant_info["user_id"])))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse.model_validate(user)


@router.get("/tenant", response_model=TenantResponse)
async def get_tenant(
    db: AsyncSession = Depends(get_db),
    tenant_info: dict = Depends(__import__('app.middleware.tenant', fromlist=['get_current_tenant']).get_current_tenant)
):
    """Get current tenant info."""
    
    result = await db.execute(select(Tenant).where(Tenant.id == uuid.UUID(tenant_info["tenant_id"])))
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    return TenantResponse.model_validate(tenant)
