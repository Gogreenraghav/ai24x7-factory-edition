# Tenant model - law firm / advocate account
from sqlalchemy import Column, String, Boolean, BigInteger, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class PlanEnum(str, enum.Enum):
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ELITE = "elite"
    ENTERPRISE = "enterprise"


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    subdomain = Column(String(100), unique=True, nullable=False)
    plan = Column(String(50), default=PlanEnum.BASIC.value)
    case_limit = Column(BigInteger, default=30)
    storage_limit_bytes = Column(BigInteger, default=5_368_709_120)  # 5GB
    storage_used_bytes = Column(BigInteger, default=0)
    is_active = Column(Boolean, default=True)
    razorpay_customer_id = Column(String(100))
    razorpay_subscription_id = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
