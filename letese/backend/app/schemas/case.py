# Case schemas - Pydantic models
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime


class CaseCreate(BaseModel):
    case_no: str
    court_name: str
    case_type: Optional[str] = None
    case_title: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    cnr_number: Optional[str] = None
    status: str = "active"
    priority: str = "normal"
    opposing_party_name: Optional[str] = None
    opposing_counsel: Optional[str] = None
    next_hearing_date: Optional[date] = None
    next_hearing_purpose: Optional[str] = None
    judge_name: Optional[str] = None
    filed_date: Optional[date] = None
    tags: Optional[List[str]] = []


class CaseUpdate(BaseModel):
    case_no: Optional[str] = None
    court_name: Optional[str] = None
    case_type: Optional[str] = None
    case_title: Optional[str] = None
    subject: Optional[str] = None
    description: Optional[str] = None
    cnr_number: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    opposing_party_name: Optional[str] = None
    opposing_counsel: Optional[str] = None
    next_hearing_date: Optional[date] = None
    next_hearing_purpose: Optional[str] = None
    judge_name: Optional[str] = None
    tags: Optional[List[str]] = None


class CaseResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    case_no: str
    court_name: str
    case_type: Optional[str]
    case_title: Optional[str]
    subject: Optional[str]
    status: str
    priority: str
    cnr_number: Optional[str]
    opposing_party_name: Optional[str]
    next_hearing_date: Optional[date]
    next_hearing_purpose: Optional[str]
    judge_name: Optional[str]
    created_by: Optional[UUID]
    tags: List[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class HearingCreate(BaseModel):
    case_id: UUID
    hearing_date: date
    hearing_time: Optional[str] = None
    court_name: Optional[str] = None
    purpose: Optional[str] = None


class HearingResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    case_id: UUID
    hearing_date: date
    hearing_time: Optional[str]
    court_name: Optional[str]
    purpose: Optional[str]
    order_url: Optional[str]
    reminder_15d: str
    reminder_7d: str
    reminder_48h: str
    reminder_24h: str

    class Config:
        from_attributes = True