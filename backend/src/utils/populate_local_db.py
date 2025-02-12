# Python imports
import random
import sys
import time
import uuid

# Pip imports
from loguru import logger


# noqa: E402
sys.path.append("..")  # noqa: E402

# Python imports
import asyncio  # noqa: E402

# Pip imports
from tortoise import Tortoise  # noqa: E402

# Internal imports
from src.database.tortoise_init import init_models  # noqa: E402


# enable schemas to read relationship between models
# flakes8: noqa
init_models()


# Internal imports
from src.auth.auth import Auth0User  # noqa: E402
from src.controllers.customers import create_customer  # noqa: E402
from src.crud.account_crud import account_crud  # noqa: E402
from src.crud.container_price_crud import container_price_crud  # noqa: E402
from src.crud.depot_crud import depot_crud  # noqa: E402
from src.crud.driver_crud import driver_crud  # noqa: E402
from src.crud.inventory_crud import inventory_crud  # noqa: E402
from src.crud.location_crud import location_crud  # noqa: E402
from src.crud.order_crud import OrderCRUD  # noqa: E402
from src.crud.order_id_counter_crud import order_id_counter_crud  # noqa: E402
from src.crud.user_crud import UserCRUD  # noqa: E402
from src.crud.vendor_crud import vendor_crud  # noqa: E402
from src.database.config import TORTOISE_ORM  # noqa: E402
from src.schemas.accounts import AccountInSchema  # noqa: E402
from src.schemas.container_locations import ContainerPriceInSchema, LocationPriceInSchema  # noqa: E402
from src.schemas.customer import CreateCustomerOrder  # noqa: E402
from src.schemas.depot import DepotInSchema  # noqa: E402
from src.schemas.driver import DriverInSchema  # noqa: E402
from src.schemas.inventory import CreateUpdateInventory  # noqa: E402
from src.schemas.inventory import InventoryIn  # noqa: E402
from src.schemas.order_id_counter import OrderIdCounterIn  # noqa: E402
from src.schemas.users import UserInSchema  # noqa: E402
from src.schemas.vendors import VendorInSchema  # noqa: E402
from src.utils.demo_data import (  # noqa: E402
    account,
    containers,
    customer_orders,
    depot_records,
    driver_records,
    inventory,
    locations,
    users,
    vendors,
)


order_crud = OrderCRUD()
user_crud = UserCRUD()

token = ""


def select_random_item(items):
    return items[random.randint(0, len(items) - 1)]


def handler(event, context):
    result = asyncio.run(async_handler(event, context))

    return {"statusCode": 200, "body": result}


async def async_handler(event, context):
    await Tortoise.init(config=TORTOISE_ORM)

    account_created = await account_crud.create(AccountInSchema(**account.dict(exclude_unset=True)))
    logger.info("account created", account_created)

    # account_created = Account(id=1)

    for user in users:
        user["account_id"] = account_created.id
        await user_crud.create(UserInSchema(**user))

    logger.info('go ahead and change the user id')
    time.sleep(20)

    user = await user_crud.get_by_email(account_created.id, "tanner.cordovatech@gmail.com")
    logger.info(user)
    auth_user = Auth0User(
        sub=f"auth0|{user.id}", email=user.email, app_metadata={"id": user.id, "account_id": account_created.id}
    )

    for vendor in vendors:
        vendor["account_id"] = account_created.id
        logger.info(vendor)
        db_vendor = await vendor_crud.create(VendorInSchema(**vendor))
        vendor["id"] = db_vendor.id

    for location in locations:
        location["account_id"] = account_created.id
        created_location = await location_crud.create(LocationPriceInSchema(**location))
        location["location_id"] = created_location.id

    for location in locations:
        for container in containers:
            container["account_id"] = account_created.id
            container["location_id"] = location["location_id"]
            await container_price_crud.create(ContainerPriceInSchema(**container))

    for depot in depot_records:
        depot["account_id"] = account_created.id
        db_depot = await depot_crud.create(DepotInSchema(**depot))
        depot["id"] = db_depot.id

    for driver in driver_records:
        driver["account_id"] = account_created.id
        db_driver = await driver_crud.create(DriverInSchema(**driver))
        driver["id"] = db_driver.id

    for i in inventory:
        inventoryCreateUpdate = CreateUpdateInventory(**i)
        inventory_dict = inventoryCreateUpdate.dict(exclude_unset=True)

        inventory_dict["account_id"] = account_created.id
        inventory_dict.pop("quantity", None)
        inventory_dict["depot_id"] = select_random_item(depot_records)["id"]
        inventory_dict["vendor_id"] = select_random_item(vendors)["id"]
        inventory_dict["status"] = inventory_dict.get("status", "Available")
        inventory_dict["id"] = str(uuid.uuid4())
        await inventory_crud.create(InventoryIn(**inventory_dict))

    await order_id_counter_crud.create(OrderIdCounterIn(account_id=account_created.id, order_id=0))

    for c in customer_orders:
        await create_customer(CreateCustomerOrder(**c), auth_user)


handler(None, None)
