# Python imports
from typing import List

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.coupon_code_crud import CouponCodeCRUD
from src.crud.coupon_code_order_crud import CouponCodeOrderCRUD
from src.crud.order_crud import OrderCRUD
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.orders.coupon_line_item_value import CouponLineItemValue
from src.schemas.coupon_code import CouponCodeOut
from src.schemas.coupon_line_item_value import CouponLineItemValueIn, CouponLineItemValueOut
from src.schemas.orders import OrderOut


order_crud = OrderCRUD()
coupon_code_crud = CouponCodeCRUD()
coupon_code_order_crud = CouponCodeOrderCRUD()


class CouponLineItemValueCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = CouponLineItemValueOut
        self.create_schema = CouponLineItemValueIn
        self.db_model = CouponLineItemValue
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            max_limit=50,
        )

    async def delete_all_in(self, coupon_line_item_ids : List[str], coupon_code_order_id : str):
        return await self.db_model.filter(line_item_id__in=coupon_line_item_ids).filter(coupon_code_order_id=coupon_code_order_id).delete()


coupon_line_item_crud = CouponLineItemValueCRUD()
