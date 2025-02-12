# pip imports
# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
# internal imports
from src.database.models.orders.coupon_line_item_value import CouponLineItemValue


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


CouponLineItemValueIn = pydantic_model_creator(
    CouponLineItemValue,
    name="CouponLineItemValueIn",
    exclude=("created_at", "modified_at", "id"),
    exclude_readonly=True,
    config_class=Config,
)

CouponLineItemValueOut = pydantic_model_creator(
    CouponLineItemValue,
    exclude_readonly=True,
    name="CouponLineItemValueOut",
)
