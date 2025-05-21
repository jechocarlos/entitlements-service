from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app import crud, models, schemas
from app.database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Entitlement, status_code=201)
async def create_entitlement(
    entitlement: schemas.EntitlementCreate,
    db: AsyncSession = Depends(get_db)
):
    # Basic validation example: ensure user_id, resource_type, and resource_id are present
    if not all([entitlement.user_id, entitlement.resource_type, entitlement.resource_id]):
        raise HTTPException(status_code=400, detail="user_id, resource_type, and resource_id are required")
    
    # Potentially check for existing identical entitlement if duplicates are not allowed
    # existing = await crud.get_entitlements(db, user_id=entitlement.user_id, resource_type=entitlement.resource_type, resource_id=entitlement.resource_id, is_active=True)
    # if existing:
    #     raise HTTPException(status_code=409, detail="Active entitlement for this user and resource already exists")

    return await crud.create_entitlement(db=db, entitlement=entitlement)

@router.get("/", response_model=schemas.EntitlementList)
async def read_entitlements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    user_id: Optional[str] = Query(None, description="Filter by User ID"),
    resource_type: Optional[str] = Query(None, description="Filter by Resource Type (e.g., 'collection', 'document')"),
    resource_id: Optional[str] = Query(None, description="Filter by Resource ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: AsyncSession = Depends(get_db)
):
    entitlements = await crud.get_entitlements(
        db, skip=skip, limit=limit, 
        user_id=user_id, resource_type=resource_type, 
        resource_id=resource_id, is_active=is_active
    )
    total_count = await crud.get_entitlements_count(
        db, user_id=user_id, resource_type=resource_type, 
        resource_id=resource_id, is_active=is_active
    )
    return {"items": entitlements, "total": total_count}

@router.get("/{entitlement_id}", response_model=schemas.Entitlement)
async def read_entitlement(
    entitlement_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    db_entitlement = await crud.get_entitlement(db, entitlement_id=entitlement_id)
    if db_entitlement is None:
        raise HTTPException(status_code=404, detail="Entitlement not found")
    return db_entitlement

@router.put("/{entitlement_id}", response_model=schemas.Entitlement)
async def update_entitlement(
    entitlement_id: UUID,
    entitlement_update: schemas.EntitlementUpdate,
    db: AsyncSession = Depends(get_db)
):
    updated_entitlement = await crud.update_entitlement(db, entitlement_id=entitlement_id, entitlement_update=entitlement_update)
    if updated_entitlement is None:
        raise HTTPException(status_code=404, detail="Entitlement not found")
    return updated_entitlement

@router.delete("/{entitlement_id}", response_model=schemas.Entitlement)
async def delete_entitlement(
    entitlement_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    deleted_entitlement = await crud.delete_entitlement(db, entitlement_id=entitlement_id)
    if deleted_entitlement is None:
        raise HTTPException(status_code=404, detail="Entitlement not found")
    return deleted_entitlement
