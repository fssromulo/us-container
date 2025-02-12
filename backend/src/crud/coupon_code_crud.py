# Python imports
from typing import List

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.orders.coupon_code import CouponCode
from src.schemas.coupon_code import CouponCodeIn, CouponCodeOut, CouponCodeUpdate


coupon_code_crud = TortoiseCRUD(
    schema=CouponCodeOut,
    create_schema=CouponCodeIn,
    update_schema=CouponCodeUpdate,
    db_model=CouponCode,
)


class CouponCodeCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = CouponCodeOut
        self.create_schema = CouponCodeIn
        self.update_schema = CouponCodeUpdate
        self.db_model = CouponCode
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=50,
        )

    async def get_one_by_id(self, coupon_code_id: str) -> Model:
        model = await self.db_model.get(id=coupon_code_id)
        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            raise NOT_FOUND

    async def get_one_by_code(self, coupon_code: str, account_id) -> Model:
        model = await self.db_model.get(code=coupon_code, account_id=account_id)
        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            raise NOT_FOUND

    async def get_all(self, account_id: int) -> List[Model]:
        query = self.db_model.filter(account_id=account_id).order_by("-created_at")
        return await self.schema.from_queryset(query)

    async def delete_by_id(self, coupon_code_order_id: str) -> Model:
        await self.db_model.get(id=coupon_code_order_id).delete()

    async def update(self, account_id: int, item_id: int, model: Model) -> Model:  # type: ignore
        if isinstance(model, self.update_schema):
            model = model.dict()
            if self.has_account_id():
                query = self.db_model.filter(account_id=account_id).filter(id=item_id)
            else:
                query = self.db_model.filter(id=item_id)
            await query.update(**model)
            return await self.schema.from_queryset_single(self.db_model.get(id=item_id))


coupon_code_crud = CouponCodeCRUD()
