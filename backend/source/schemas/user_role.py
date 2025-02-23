from typing import Optional

from source.schemas.role import Role
from pydantic import UUID4, BaseModel, ConfigDict


# Shared properties
class UserRoleBase(BaseModel):
    user_id: Optional[UUID4] | str
    role_id: Optional[UUID4]


# Properties to receive via API on creation
class UserRoleCreate(UserRoleBase):
    pass


# Properties to receive via API on update
class UserRoleUpdate(BaseModel):
    role_id: UUID4


class UserRoleInDBBase(UserRoleBase):
    role: Role

    model_config = ConfigDict(
        from_attributes=True
    )


# Additional properties to return via API
class UserRole(UserRoleInDBBase):
    pass


class UserRoleInDB(UserRoleInDBBase):
    pass