# Python imports
from decimal import Decimal

# Internal imports
from src.crud.order_crud import order_crud
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.orders.order import Order
from src.database.models.total_order_balance import TotalOrderBalance
from src.schemas.total_order_balance import TotalOrderBalanceIn, TotalOrderBalanceOut


class TotalOrderBalanceCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = TotalOrderBalanceOut
        self.create_schema = TotalOrderBalanceIn
        self.db_model = TotalOrderBalance
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
        )

    async def handle_order_balance_update(self, order_id: str, amt_to_alter: Decimal, is_adding: bool = True):
        """
        param: order_id (str)
        param: amt_to_alter (Decimal): This is the absolute value of what you are altering.
        param: is_adding (bool): This flag will handle the addition or subtraction of your absolute value
        """

        # grab order so that we can get the most recent calculated remaining balance value
        order: Order = await order_crud.get_one(
            order_id
        )  # just grabbing one of the ids bc they all pertain to the same one
        remaining_balance: Decimal = order.calculated_remaining_order_balance

        new_balance = remaining_balance + amt_to_alter if is_adding else remaining_balance - amt_to_alter

        create_order_balance: TotalOrderBalanceIn = TotalOrderBalanceIn(
            remaining_balance=new_balance, order_id=order_id
        )
        await total_order_balance_crud.create(create_order_balance)

    async def get_distinct_order_ids(self):
        order_ids = await self.db_model.all().distinct().values("order_id")
        return [entry['order_id'] for entry in order_ids]

    async def get_by_order_id(self, order_id):
        order_balances = await self.db_model.filter(order_id=order_id)
        return order_balances


total_order_balance_crud = TotalOrderBalanceCRUD()
