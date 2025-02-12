from decimal import Decimal
from src.database.models.tax import Tax
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.schemas.tax import (
    TaxInSchema,
    TaxOutSchema,
)

class TaxCrud(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = TaxOutSchema
        self.create_schema = TaxInSchema
        self.db_model = Tax
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
        )

    async def get_tax_rate(self, account_id: int, state: str) -> Decimal:
        if state is None:
            return 0
        model = await self.db_model.filter(account_id=account_id).filter(state=state.upper()).first()
        if model:
            tax_out: Tax = await self.schema.from_tortoise_orm(model)
            return tax_out.rate
        else:
            return 0


tax_crud = TaxCrud()
