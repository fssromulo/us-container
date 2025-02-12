# Python imports
import asyncio

# import sys
from typing import List

# Pip imports
from loguru import logger
from tortoise import Tortoise

# Internal imports
from src.database.tortoise_init import init_models


# enable schemas to read relationship between models
# flakes8: noqa
init_models()


# Internal imports
from src.crud.account_crud import account_crud  # noqa: E402
from src.crud.container_inventory_crud import container_inventory_crud  # noqa: E402
from src.database.config import TORTOISE_ORM  # noqa: E402
from src.database.models.account import Account  # noqa: E402
from src.schemas.container_inventory import ContainerInventoryOut  # noqa: E402
from src.services.notifications.email_service import send_inventory_release_notification  # noqa: E402


def handler(event, context):
    result = asyncio.run(async_handler(event, context))

    return {'statusCode': 200, 'body': result}


async def async_handler(event, context):
    await Tortoise.init(config=TORTOISE_ORM)
    accounts: List[Account] = await account_crud.get_all()
    for account in accounts:
        if True:  # account.cms_attributes.get('should_send_release_notification', False):
            container_inventory: List[
                ContainerInventoryOut
            ] = await container_inventory_crud.get_containers_without_container_numbers(account.id)

            await handle_inventory_check(container_inventory)


async def handle_inventory_check(containers: List[ContainerInventoryOut]):
    # Lets check if is attached to an order
    email_items = [
        {"container_release_number": con.container_release_number, "created_at": con.created_at.strftime("%b %d %Y ")}
        for con in containers
    ]
    for inventory in containers:
        if inventory.line_items is not None and inventory.line_items.shipping_revenue == 0:
            # If it is attached check if it is a pickup order for now do nothing
            email_items = [
                item for item in email_items if item['container_release_number'] != inventory.container_release_number
            ]

    logger.info(f"Sending notification for release number {[x['container_release_number'] for x in email_items]}")
    logger.info(email_items)
    # we should not send multiple emails, rather just one containing all the containers
    send_inventory_release_notification(email_items)


# if __name__ == "__main__":  # TODO COMMENT THIS OUT BEFORE PUSHING UP
#    handler(None, None)
