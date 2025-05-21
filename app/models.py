import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Entitlement(Base):
    __tablename__ = "entitlements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False, index=True) # ID of the user from an external system
    resource_type = Column(String, nullable=False, index=True) # e.g., 'collection', 'document', 'tool_feature'
    resource_id = Column(String, nullable=False, index=True) # ID of the resource being entitled
    access_level = Column(String, nullable=True) # e.g., 'read', 'write', 'admin', 'use'
    is_active = Column(Boolean, default=True)
    # You can add more specific permission flags as boolean columns if needed
    # can_edit = Column(Boolean, default=False)
    # can_delete = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # A short description or reason for this entitlement
    description = Column(Text, nullable=True)

    # Who granted this entitlement (e.g., system, admin_user_id)
    granted_by = Column(String, nullable=True)

    def __repr__(self):
        return f"<Entitlement(id={self.id}, user_id='{self.user_id}', resource='{self.resource_type}:{self.resource_id}')>"

# If you have other related models, define them here. For example:
# class User(Base):
#     __tablename__ = "users"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     username = Column(String, unique=True, index=True)
#     email = Column(String, unique=True, index=True)
#     # entitlements = relationship("Entitlement", back_populates="user")

# class Resource(Base):
#     __tablename__ = "resources"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     name = Column(String, index=True)
#     type = Column(String) # 'collection', 'document'
#     # entitlements = relationship("Entitlement", back_populates="resource")
