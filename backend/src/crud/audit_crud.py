# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.audit import Audit
from src.schemas.audit import AuditInSchema, AuditOutSchema


class AuditCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = AuditOutSchema
        self.create_schema = AuditInSchema
        self.update_schema = AuditInSchema
        self.db_model = Audit
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=50,
        )

audit_crud = AuditCRUD()