# Cases router - /api/v1/cases/*
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.core.database import get_db
from app.models.case import Case, Hearing
from app.schemas.case import (
    CaseCreate, CaseUpdate, CaseResponse,
    HearingCreate, HearingResponse
)
from app.middleware.tenant import get_current_tenant

router = APIRouter(prefix="/api/v1/cases", tags=["Cases"])


@router.get("", response_model=List[CaseResponse])
async def list_cases(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    court_name: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    tenant: dict = Depends(get_current_tenant)
):
    """List all cases for current tenant (with filters)."""
    
    query = select(Case).where(Case.tenant_id == UUID(tenant["tenant_id"]))
    
    if status:
        query = query.where(Case.status == status)
    if priority:
        query = query.where(Case.priority == priority)
    if court_name:
        query = query.where(Case.court_name.ilike(f"%{court_name}%"))
    if search:
        query = query.where(
            Case.case_title.ilike(f"%{search}%") |
            Case.case_no.ilike(f"%{search}%") |
            Case.cnr_number.ilike(f"%{search}%")
        )
    
    query = query.order_by(Case.created_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    cases = result.scalars().all()
    
    return [CaseResponse.model_validate(c) for c in cases]


@router.post("", response_model=CaseResponse)
async def create_case(
    data: CaseCreate,
    db: AsyncSession = Depends(get_db),
    tenant: dict = Depends(get_current_tenant)
):
    """Create a new case."""
    
    case = Case(
        tenant_id=UUID(tenant["tenant_id"]),
        created_by=UUID(tenant["user_id"]),
        **data.model_dump()
    )
    db.add(case)
    await db.commit()
    await db.refresh(case)
    
    return CaseResponse.model_validate(case)


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant: dict = Depends(get_current_tenant)
):
    """Get a single case by ID."""
    
    result = await db.execute(
        select(Case).where(
            and_(
                Case.id == case_id,
                Case.tenant_id == UUID(tenant["tenant_id"])
            )
        )
    )
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    return CaseResponse.model_validate(case)


@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: UUID,
    data: CaseUpdate,
    db: AsyncSession = Depends(get_db),
    tenant: dict = Depends(get_current_tenant)
):
    """Update a case."""
    
    result = await db.execute(
        select(Case).where(
            and_(
                Case.id == case_id,
                Case.tenant_id == UUID(tenant["tenant_id"])
            )
        )
    )
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(case, key, value)
    
    await db.commit()
    await db.refresh(case)
    
    return CaseResponse.model_validate(case)


@router.delete("/{case_id}")
async def delete_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant: dict = Depends(get_current_tenant)
):
    """Soft delete a case (mark as disposed)."""
    
    result = await db.execute(
        select(Case).where(
            and_(
                Case.id == case_id,
                Case.tenant_id == UUID(tenant["tenant_id"])
            )
        )
    )
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    case.status = "disposed"
    await db.commit()
    
    return {"message": "Case marked as disposed"}


# ---- Hearings ----

@router.get("/{case_id}/hearings", response_model=List[HearingResponse])
async def list_hearings(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant: dict = Depends(get_current_tenant)
):
    """List hearings for a case."""
    
    result = await db.execute(
        select(Hearing).where(
            and_(
                Hearing.case_id == case_id,
                Hearing.tenant_id == UUID(tenant["tenant_id"])
            )
        ).order_by(Hearing.hearing_date.desc())
    )
    hearings = result.scalars().all()
    
    return [HearingResponse.model_validate(h) for h in hearings]


@router.post("/{case_id}/hearings", response_model=HearingResponse)
async def create_hearing(
    case_id: UUID,
    data: HearingCreate,
    db: AsyncSession = Depends(get_db),
    tenant: dict = Depends(get_current_tenant)
):
    """Add a hearing to a case."""
    
    # Verify case belongs to tenant
    case_result = await db.execute(
        select(Case).where(
            and_(
                Case.id == case_id,
                Case.tenant_id == UUID(tenant["tenant_id"])
            )
        )
    )
    if not case_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Case not found")
    
    hearing = Hearing(
        tenant_id=UUID(tenant["tenant_id"]),
        case_id=case_id,
        hearing_date=data.hearing_date,
        hearing_time=data.hearing_time,
        court_name=data.court_name,
        purpose=data.purpose,
    )
    db.add(hearing)
    await db.commit()
    await db.refresh(hearing)
    
    return HearingResponse.model_validate(hearing)


@router.get("/hearings/upcoming", response_model=List[HearingResponse])
async def upcoming_hearings(
    days: int = Query(7, le=90),
    db: AsyncSession = Depends(get_db),
    tenant: dict = Depends(get_current_tenant)
):
    """Get upcoming hearings for next N days."""
    
    today = date.today()
    end_date = date.today()
    
    result = await db.execute(
        select(Hearing).where(
            and_(
                Hearing.tenant_id == UUID(tenant["tenant_id"]),
                Hearing.hearing_date >= today,
                Hearing.hearing_date <= end_date
            )
        ).order_by(Hearing.hearing_date)
    )
    hearings = result.scalars().all()
    
    return [HearingResponse.model_validate(h) for h in hearings]
