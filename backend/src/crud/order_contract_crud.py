# ...

# Pip imports
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.order_contract import OrderContract
from src.schemas.order_contract import OrderContractIn, OrderContractOut


# order_contract_crud = TortoiseCRUD(
#     schema=OrderContractOut,
#     create_schema=OrderContractIn,
#     update_schema=OrderContractIn,
#     db_model=OrderContract,
# )


class OrderContractCrud(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = OrderContractOut
        self.create_schema = OrderContractIn
        self.update_schema = OrderContractIn
        self.db_model = OrderContract
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
        )

    async def get_one(self, contract_id: str) -> Model:
        try:
            model = await self.db_model.get(contract_id=contract_id)
        except DoesNotExist:
            raise
        if model:
            return await self.schema.from_tortoise_orm(model)

    async def update(self, item_id: int, model: Model) -> Model:
        if isinstance(model, self.update_schema):
            model = model.dict(exclude_unset=True)
            query = self.db_model.filter(id=item_id)
            await query.update(**model)
            return await self.schema.from_queryset_single(self.db_model.get(id=item_id))

    async def get_contracts_by_order_id(self, order_id: str) -> Model:
        try:
            # Filter the contracts by order_id, check for title in meta_data, and order by created_at in descending order
            query = self.db_model.filter(order_id=order_id).order_by('-created_at')

        except DoesNotExist:
            raise

        return await self.schema.from_queryset(query)

    async def get_contracts_by_signed_date(self, start_date, end_date) -> Model:
        try:
            # Filter the contracts by order_id, check for title in meta_data, and order by created_at in descending order
            query = self.db_model.filter(
                status="contract-signed", modified_at__gte=start_date, modified_at__lte=end_date
            ).order_by('-modified_at')

        except DoesNotExist:
            raise

        return await self.schema.from_queryset(query)


order_contract_crud = OrderContractCrud()
