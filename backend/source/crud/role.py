from typing import Optional


from source.crud.base import CRUDBase
from source.models import Role
from source.schemas.role import RoleCreate, RoleUpdate
from sqlalchemy.orm import Session


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Role]:
        return db.query(self.model).filter(Role.name == name).first()


role = CRUDRole(Role)