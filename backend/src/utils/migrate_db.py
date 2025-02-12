# Python imports
import asyncio
import uuid

# import sys
from typing import Dict

# Pip imports
from loguru import logger
from tortoise import Tortoise

# Internal imports
from src.database.tortoise_init import init_models


init_models()

# Internal imports
from src.crud.container_attribute_crud import container_attribute_crud
from src.crud.container_inventory_new_crud import container_inventory_new_crud  # noqa: E402
from src.crud.container_price_crud import container_price_crud  # noqa: E402
from src.crud.container_product_attribute import container_product_attribute_crud
from src.crud.container_product_new_crud import container_product_new_crud  # noqa: E402
from src.crud.inventory_crud import inventory_crud  # noqa: E402
from src.crud.location_price_new_crud import location_price_new_crud  # noqa: E402
from src.database.config import TORTOISE_ORM  # noqa: E402
from src.schemas.container_inventory_new import ContainerInventoryNewIn  # noqa: E402
from src.schemas.container_product_attribute import ContainerProductAttributeIn
from src.schemas.container_product_new import ContainerProductNewIn  # noqa: E402
from src.schemas.location_price import LocationPriceNewIn  # noqa: E402


def handler(event, context):
    asyncio.run(async_handler(event, context))


def process_dimensions(item) -> Dict[str, str]:
    if not item:
        item = "0x0x0"
    dimensions = item.split("x")

    return {"length": str(dimensions[0]), "width": str(dimensions[1]), "height": str(dimensions[2])}


async def async_handler(event, context):
    await Tortoise.init(config=TORTOISE_ORM)

    standard_attr = await container_attribute_crud.get_by_name("Standard")
    double_door_attr = await container_attribute_crud.get_by_name("Double Door")
    high_cube_attr = await container_attribute_crud.get_by_name("High Cube")

    container_product_new_list = []
    container_attribute_list = []

    new_products = {}
    for account_id in [1, 2]:
        logger.info(f"Processing acount {account_id} for creating ContainerProductNew and LocationPriceNew")
        container_price_items = await container_price_crud.get_all(account_id)

        location_old_price_ids = {}
        location_price_in_list = []
        for item in container_price_items:
            location_price_in = LocationPriceNewIn(
                id=str(uuid.uuid4()),
                city=item.location.city,
                state=item.location.state,
                zip=item.location.zip,
                region=item.location.region,
                account_id=account_id,
            )
            location_old_price_ids[item.location.id] = location_price_in
            location_price_in_list.append(location_price_in)

        await location_price_new_crud.bulk_create(location_price_in_list, len(location_price_in_list))

        i = 1

        for item in container_price_items:
            dimensions = process_dimensions(item.attributes.get('dimensions'))

            container_product_new_id = uuid.uuid4()

            newContainerProducNewIn = ContainerProductNewIn(
                id=container_product_new_id,
                name="",
                description=item.description,
                price=item.sale_price,
                monthly_price=item.monthly_rental_price,
                cost_per_mile=item.location.cost_per_mile,
                minimum_shipping_cost=item.location.minimum_shipping_cost,
                container_size=item.container_size,
                location_id=location_old_price_ids[item.location.id].id,
                length=float(dimensions['length']),
                width=float(dimensions['width']),
                height=float(dimensions['height']),
                condition=item.condition,
                product_type=str(item.product_type),
            )

            logger.info(f"Creating ContainerProductNewIn {i}")
            # res = await container_product_new_crud.create(newContainerProducNewIn)
            container_product_new_list.append(newContainerProducNewIn)

            if item.attributes.get('standard', False):
                container_attribute_standard = ContainerProductAttributeIn(
                    **{"container_product_new_id": container_product_new_id, "container_attribute_id": standard_attr.id}
                )
                container_attribute_list.append(container_attribute_standard)

            if item.attributes.get('double_door', False):
                container_attribute_double_door = ContainerProductAttributeIn(
                    **{
                        "container_product_new_id": container_product_new_id,
                        "container_attribute_id": double_door_attr.id,
                    }
                )
                container_attribute_list.append(container_attribute_double_door)

            if item.attributes.get('high_cube', False):
                container_attribute_high_cube = ContainerProductAttributeIn(
                    **{
                        "container_product_new_id": container_product_new_id,
                        "container_attribute_id": high_cube_attr.id,
                    }
                )
                container_attribute_list.append(container_attribute_high_cube)

            standard = item.attributes.get('standard', False)
            double_door = item.attributes.get('double_door', False)
            high_cube = item.attributes.get('high_cube', False)
            new_products[
                str(account_id)
                + " "
                + str(standard)
                + " "
                + str(double_door)
                + " "
                + str(high_cube)
                + " "
                + str(item.condition)
                + " "
                + str(item.container_size)
            ] = container_product_new_id
            i += 1
    logger.info("Container Product New List", len(container_product_new_list))
    await container_product_new_crud.bulk_create(container_product_new_list, len(container_product_new_list))
    await container_product_attribute_crud.bulk_create(container_attribute_list, len(container_attribute_list))

    for account_id in [1, 2]:
        skip = 0
        logger.info(f"Processing acount {account_id} for creating ContainerInventoryNew")
        while True:
            inventory_items = await inventory_crud.get_all(account_id, pagination={"limit": 1000, "skip": skip})
            logger.info(f"Got all {len(inventory_items)}. {skip}")
            if len(inventory_items) == 0:
                break
            skip += 1000

            new_inventory_items_list = []
            for item in inventory_items:
                new_products_key = (
                    str(account_id)
                    + " "
                    + str(item.type.get("standard", False))
                    + " "
                    + str(item.type.get("double_door", False))
                    + " "
                    + str(item.type.get("high_cube", False))
                    + " "
                    + str(item.condition)
                    + " "
                    + str(item.container_size)
                )
                product_id = new_products.get(new_products_key)

                new_inventory_items_list.append(
                    ContainerInventoryNewIn(
                        id=item.id,
                        total_cost=item.total_cost,
                        status=item.status,
                        purchase_type=item.purchase_type,
                        invoice_number=item.invoice_number,
                        invoiced_at=item.invoiced_at,
                        pickup_at=item.pickup_at,
                        payment_type=item.payment_type,
                        paid_at=item.paid_at,
                        vendor_id=item.vendor.id,
                        account_id=item.account_id,
                        container_number=item.container_number,
                        container_release_number=item.container_release_number,
                        product_id=product_id,
                        depot_id=item.depot.id if item.depot else None,
                    )
                )

            await container_inventory_new_crud.bulk_create(new_inventory_items_list, len(new_inventory_items_list))


handler(None, None)
