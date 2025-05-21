from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from . import models, schemas
from uuid import UUID

async def get_entitlement(db: AsyncSession, entitlement_id: UUID) -> Optional[models.Entitlement]:
    result = await db.execute(select(models.Entitlement).filter(models.Entitlement.id == entitlement_id))
    return result.scalars().first()

async def get_entitlements(
    db: AsyncSession, 
    skip: int = 0, 
    limit: int = 100,
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    is_active: Optional[bool] = None
) -> List[models.Entitlement]:
    query = select(models.Entitlement)
    if user_id:
        query = query.filter(models.Entitlement.user_id == user_id)
    if resource_type:
        query = query.filter(models.Entitlement.resource_type == resource_type)
    if resource_id:
        query = query.filter(models.Entitlement.resource_id == resource_id)
    if is_active is not None:
        query = query.filter(models.Entitlement.is_active == is_active)
    
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

async def create_entitlement(db: AsyncSession, entitlement: schemas.EntitlementCreate) -> models.Entitlement:
    db_entitlement = models.Entitlement(**entitlement.dict())
    db.add(db_entitlement)
    await db.commit()
    await db.refresh(db_entitlement)
    return db_entitlement

async def update_entitlement(
    db: AsyncSession, 
    entitlement_id: UUID, 
    entitlement_update: schemas.EntitlementUpdate
) -> Optional[models.Entitlement]:
    db_entitlement = await get_entitlement(db, entitlement_id)
    if not db_entitlement:
        return None

    update_data = entitlement_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_entitlement, key, value)

    await db.commit()
    await db.refresh(db_entitlement)
    return db_entitlement

async def delete_entitlement(db: AsyncSession, entitlement_id: UUID) -> Optional[models.Entitlement]:
    db_entitlement = await get_entitlement(db, entitlement_id)
    if not db_entitlement:
        return None
    await db.delete(db_entitlement)
    await db.commit()
    return db_entitlement

async def get_entitlements_count(
    db: AsyncSession,
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    is_active: Optional[bool] = None
) -> int:
    # This is a simplified count. For more complex queries, consider count(Entitlement.id)
    # or a more specific count query if performance becomes an issue.
    query = select(models.Entitlement.id) # Select only ID for counting
    if user_id:
        query = query.filter(models.Entitlement.user_id == user_id)
    if resource_type:
        query = query.filter(models.Entitlement.resource_type == resource_type)
    if resource_id:
        query = query.filter(models.Entitlement.resource_id == resource_id)
    if is_active is not None:
        query = query.filter(models.Entitlement.is_active == is_active)

    # Execute the query and count the results
    # Note: For a large number of rows, this might not be the most performant way to count.
    # A dedicated count query (e.g., using func.count) might be better.
    # from sqlalchemy import func
    # query = select(func.count(models.Entitlement.id))
    # ... add filters ...
    # result = await db.execute(query)
    # return result.scalar_one()
    
    all_ids = await db.execute(query)
    return len(all_ids.scalars().all()) # This fetches all IDs then counts, can be inefficient
