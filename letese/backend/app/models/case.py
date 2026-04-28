# Case model - the core entity
from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey, BigInteger, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class CaseStatus(str, enum.Enum):
    ACTIVE = "active"
    PENDING = "pending"
    CLOSED = "closed"
    DISPOSED = "disposed"


class CasePriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Case(Base):
    __tablename__ = "cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    cnr_number = Column(String(50), index=True)
    case_no = Column(String(100), nullable=False)
    court_name = Column(String(255), nullable=False)
    case_type = Column(String(100))
    case_title = Column(String(500))
    subject = Column(Text)
    description = Column(Text)
    
    status = Column(String(50), default=CaseStatus.ACTIVE.value, index=True)
    priority = Column(String(50), default=CasePriority.NORMAL.value)
    
    opposing_party_name = Column(String(255))
    opposing_counsel = Column(String(255))
    
    next_hearing_date = Column(Date, index=True)
    next_hearing_purpose = Column(String(255))
    judge_name = Column(String(255))
    
    filed_date = Column(Date)
    
    created_by = Column(UUID(as_uuid=True))
    assigned_to = Column(UUID(as_uuid=True))
    
    tags = Column(ARRAY(String), default=[])
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Hearing(Base):
    __tablename__ = "hearings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    case_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    hearing_date = Column(Date, nullable=False, index=True)
    hearing_time = Column(String(20))
    court_name = Column(String(255))
    purpose = Column(String(255))
    order_url = Column(String(500))
    order_text = Column(Text)
    
    reminder_15d = Column(String(20), default="pending")  # pending/sent/failed
    reminder_7d = Column(String(20), default="pending")
    reminder_48h = Column(String(20), default="pending")
    reminder_24h = Column(String(20), default="pending")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
