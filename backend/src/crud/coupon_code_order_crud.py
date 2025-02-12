# Python imports
from typing import List

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.coupon_code_crud import CouponCodeCRUD
from src.crud.order_crud import OrderCRUD
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.orders.coupon_code_order import CouponCodeOrder
from src.schemas.coupon_code import CouponCodeOut
from src.schemas.coupon_code_order import CouponCodeOrderIn, CouponCodeOrderOut
from src.schemas.orders import OrderOut


order_crud = OrderCRUD()
coupon_code_crud = CouponCodeCRUD()


class CouponCodeOrderCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = CouponCodeOrderOut
        self.create_schema = CouponCodeOrderIn
        self.db_model = CouponCodeOrder
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            max_limit=50,
        )

    async def get_one_by_id(self, coupon_code_order_id: str) -> Model:
        model = await self.db_model.get(id=coupon_code_order_id)
        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            raise NOT_FOUND

    async def get_by_order_coupon_id(self, order_id: str, coupon_id: str) -> List[CouponCodeOut]:
        return await CouponCodeOrder.filter(order_id=order_id).filter(coupon_id=coupon_id).first()

    async def get_all_by_order_id(self, account_id, order_id: int) -> List[CouponCodeOut]:
        query = await CouponCodeOrder.filter(order_id=order_id).prefetch_related('coupon')
        result = await coupon_code_crud.get_by_ids(account_id, [i.coupon_id for i in query])
        return result

    async def get_all_by_coupon_code_id(self, coupon_code_id: str) -> List[OrderOut]:
        query = await CouponCodeOrder.filter(coupon_id=coupon_code_id).prefetch_related('order')
        return await order_crud.get_by_ids(1, [i.order_id for i in query])

    async def delete_by_id(self, coupon_code_order_id: str) -> Model:
        await self.db_model.get(id=coupon_code_order_id).delete()

    async def delete_by_ids(self, coupon_id: str, ids=list[str]):
        await self.db_model.filter(coupon_id=coupon_id).filter(order_id__in=ids).delete()

    async def delete_one_by_coupon_id_and_order_id(self, order_id, coupon_id):
        await self.db_model.get(order_id=order_id, coupon_id=coupon_id).delete()


coupon_code_order_crud = CouponCodeOrderCRUD()
