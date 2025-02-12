# pip imports
# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
# internal imports
from src.database.models.orders.coupon_code_order import CouponCodeOrder


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


CouponCodeOrderIn = pydantic_model_creator(
    CouponCodeOrder,
    name="CouponCodeOrderIn",
    exclude=("created_at", "modified_at", "id"),
    exclude_readonly=True,
    config_class=Config,
)

CouponCodeOrderOut = pydantic_model_creator(
    CouponCodeOrder,
    exclude_readonly=True,
    name="CouponCodeOrderOut",
    optional=("coupon_line_item_value")
)
