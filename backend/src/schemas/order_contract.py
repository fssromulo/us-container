# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.order_contract import OrderContract


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


OrderContractIn = pydantic_model_creator(
    OrderContract,
    name="OrderContractIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    config_class=Config,
)

OrderContractOut = pydantic_model_creator(
    OrderContract,
    name="OrderContractOut",
    include=("id", "created_at", "modified_at", "status", "contract_id", "meta_data", "order_id", "contract_pdf_link"),
)
