# Python imports
import asyncio
import os
import uuid
from datetime import datetime

# Pip imports
from loguru import logger
from tortoise import Tortoise

# Internal imports
from src.database.tortoise_init import init_models


init_models()

# Python imports
import json  # noqa: E402

# Internal imports
from src.crud.account_crud import account_crud  # noqa: E402
from src.crud.fee_type_crud import fee_type_crud  # noqa: E402
from src.crud.order_id_counter_crud import order_id_counter_crud  # noqa: E402
from src.database.config import TORTOISE_ORM  # noqa: E402
from src.database.models.account import Account  # noqa: E402
from src.schemas.accounts import AccountInSchema  # noqa: E402
from src.schemas.fee_type import FeeTypeIn  # noqa: E402
from src.schemas.order_id_counter import OrderIdCounterIn  # noqa: E402


# Enable schemas to read relationship between models

STAGE = os.environ.get("STAGE", "dev")


def handler(event, context):
    # Extract arguments from the event
    account_name = event.get("account_name", "DefaultAccountName")
    cms_attrs = event.get("cms_attrs", "")
    integrations = event.get("integrations", "")

    logger.info(f"Creating account: {account_name}")

    result = asyncio.run(async_handler(account_name, cms_attrs, integrations, context))
    return {'statusCode': 200, 'body': result}


async def get_next_account_id():
    last_account = await Account.all().order_by('-id').first()
    return (last_account.id + 1) if last_account else 1


async def async_handler(account_name, cms_attrs, integrations, context):
    await Tortoise.init(config=TORTOISE_ORM)

    try:
        next_account_id = await get_next_account_id()
        current_time = datetime.now()
        logger.info(f"Next account ID: {next_account_id}")

        account_data = {
            "name": account_name,
            "is_active": True,
            "auth0_management_token_modified_at": current_time,
            "cms_attributes": cms_attrs,
            "integrations": integrations,
            "auth0_management_token": None,
        }

        fee_types_data = [
            {
                "id": uuid.uuid4(),
                "name": 'PICK_UP',
                "is_taxable": True,
                "is_archived": False,
                "is_editable": False,
                "account_id": next_account_id,
                "display_name": "Pick Up",
                "adjusts_profit": True,
            },
            {
                "id": uuid.uuid4(),
                "name": 'DROP_OFF',
                "is_taxable": True,
                "is_archived": False,
                "is_editable": False,
                "account_id": next_account_id,
                "display_name": "Delivery",
                "adjusts_profit": True,
            },
            {
                "id": uuid.uuid4(),
                "name": 'CERTIFICATION',
                "is_taxable": True,
                "is_archived": False,
                "is_editable": True,
                "account_id": next_account_id,
                "display_name": None,
                "adjusts_profit": True,
            },
            {
                "id": uuid.uuid4(),
                "name": 'RUSH',
                "is_taxable": True,
                "is_archived": False,
                "is_editable": True,
                "account_id": next_account_id,
                "display_name": None,
                "adjusts_profit": True,
            },
            {
                "id": uuid.uuid4(),
                "name": 'LATE',
                "is_taxable": False,
                "is_archived": False,
                "is_editable": False,
                "account_id": next_account_id,
                "display_name": "Late fee",
                "adjusts_profit": True,
            },
            {
                "id": uuid.uuid4(),
                "name": 'CREDIT_CARD',
                "is_taxable": False,
                "is_archived": False,
                "is_editable": False,
                "account_id": next_account_id,
                "display_name": None,
                "adjusts_profit": False,
            },
        ]

        order_id_counter_data = {
            "id": uuid.uuid4(),
            "order_id": 100000,
            "account_id": next_account_id,
        }

        # Insert account data
        account = await account_crud.create(AccountInSchema(**account_data))
        logger.info(f"Account created: {account}")

        # Insert fee types data
        for fee_type in fee_types_data:
            await fee_type_crud.create(FeeTypeIn(**fee_type))

        # Insert order ID counter data
        order_id_counter = await order_id_counter_crud.create(OrderIdCounterIn(**order_id_counter_data))
        logger.info(f"Order ID Counter created: {order_id_counter}")

        result = "Account, Fee Types, and Order ID Counter created successfully."
        logger.info(result)
    except Exception as e:
        result = f"An error occurred: {e}"
        logger.info(result)
    finally:
        await Tortoise.close_connections()

    return result


if __name__ == "__main__":
    # Example event data for testing
    test_event = {"account_name": "BlairWorx Logistics", "cms_attrs": json.dumps({}), "integrations": {}}
    handler(test_event, "test")
