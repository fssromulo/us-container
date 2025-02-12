# Pip imports
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
# internal imports
from src.database.models.orders.coupon_code import CouponCode


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


CouponCodeIn = pydantic_model_creator(CouponCode, name="CouponCodeIn", exclude_readonly=True, config_class=Config)

CouponCodeInsecureOut = pydantic_model_creator(
    CouponCode,
    include=(
        "name",
        "amount",
        "minimum_discount_threshold",
        "start_date",
        "end_date",
        "size",
        "city",
        "type",
        "role",
        "is_permanent",
        "rules",
        "is_stackable",
        "category",
        "percentage",
        "attributes",
    ),
    name="CouponCodeInsecureOut",
)

CouponCodeOut = pydantic_model_creator(
    CouponCode,
    include=(
        "id",
        "name",
        "amount",
        "minimum_discount_threshold",
        "start_date",
        "code",
        "end_date",
        "size",
        "city",
        "type",
        "role",
        "is_permanent",
        "rules",
        "is_stackable",
        "category",
        "percentage",
        "attributes",
    ),
    name="CouponCodeOut",
)

CouponCodeUpdate = pydantic_model_creator(
    CouponCode, name="CouponCodeUpdate", exclude_readonly=True, config_class=Config
)


class CouponCodeMassDelete(BaseModel):
    ids: list = []
