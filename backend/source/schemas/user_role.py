from typing import Optional

from source.schemas.role import Role
from pydantic import UUID4, BaseModel, ConfigDict



class UserRoleBase(BaseModel):
    user_id: str
    role_id: Optional[UUID4]



class UserRoleInDBBase(UserRoleBase):
    role: Role

    model_config = ConfigDict(
        from_attributes=True
    )




class UserRole(UserRoleInDBBase):
    pass
