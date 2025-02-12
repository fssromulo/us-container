# ...

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.order_fee_balance import OrderFeeBalance
from src.schemas.order_fee_balance import OrderFeeBalanceIn, OrderFeeBalanceOut


class OrderFeeBalanceCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = OrderFeeBalanceOut
        self.create_schema = OrderFeeBalanceIn
        self.update_schema = OrderFeeBalanceIn
        self.db_model = OrderFeeBalance
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=50)

    async def get_latest_balance(self, account_id: int, fee_id: str, order_id: str):
        return (
            await self.db_model.filter(account_id=account_id)
            .filter(order_id=order_id)
            .filter(fee_id=fee_id)
            .order_by('-created_at')
            .first()
        )

    async def drop_balances(self, fee_id: str, account_id: int):
        fees_list = await self.db_model.all().filter(fee_id=fee_id).filter(account_id=account_id)
        ids_list_to_delete = []
        for fee in fees_list:
            ids_list_to_delete.append(fee.id)
        return await self.db_model.filter(account_id=account_id).filter(id__in=ids_list_to_delete).delete()

    async def get_by_order_id(self, order_id: str):
        models = await self.db_model.filter(order_id=order_id)
        if models:
            results = []
            for model in models:
                await model.fetch_related()
                result = await self.schema.from_tortoise_orm(model)
                results.append(result)
            return results
        else:
            return []


order_fee_balance_crud = OrderFeeBalanceCRUD()
