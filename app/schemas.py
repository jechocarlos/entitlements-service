from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime

# Base schema for Entitlement
class EntitlementBase(BaseModel):
    user_id: str
    resource_type: str
    resource_id: str
    access_level: Optional[str] = None
    is_active: Optional[bool] = True
    description: Optional[str] = None
    granted_by: Optional[str] = None
    expires_at: Optional[datetime] = None

# Schema for creating an Entitlement (request)
class EntitlementCreate(EntitlementBase):
    pass

# Schema for updating an Entitlement (request)
class EntitlementUpdate(BaseModel):
    user_id: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    access_level: Optional[str] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None
    granted_by: Optional[str] = None
    expires_at: Optional[datetime] = None

# Schema for reading/returning an Entitlement (response)
class Entitlement(EntitlementBase):
    id: UUID4
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True # Pydantic V1
        # from_attributes = True # Pydantic V2

# For paginated list response
class EntitlementList(BaseModel):
    items: List[Entitlement]
    total: int
    # page: int
    # size: int
