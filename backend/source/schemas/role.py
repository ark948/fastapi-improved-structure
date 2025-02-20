from typing import Optional
from pydantic import UUID4, BaseModel, ConfigDict



class RoleBase(BaseModel):
    name: Optional[str]
    description: Optional[str]




class RoleInDBBase(RoleBase):
    id: UUID4

    model_config = ConfigDict(
        from_attributes=True
    )



class Role(RoleInDBBase):
    pass