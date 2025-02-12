# Pip imports
from fastapi import HTTPException, status
from fastapi_cache import FastAPICache
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import atomic

# Internal imports
from src.auth.auth import Auth0User
from src.crud.container_product_crud import container_product_crud
from src.crud.location_price_crud import location_price_crud
from src.schemas.container_locations import CreateUpdateLocationPrice, LocationPriceOutSchema
from src.schemas.container_product import ContainerProduct
from src.schemas.location_price import LocationPriceIn, LocationPriceOut
from src.schemas.token import Status


@atomic()
async def save_location(location: CreateUpdateLocationPrice, user, location_id=None):
    location_dict = location.dict(exclude_unset=True)
    location_dict["account_id"] = user.app_metadata["account_id"]

    if location_id:
        location_new_dict = {
            "city": location.city,
            "state": location.state,
            "province": location.province,
            "zip": location.zip,
            "region": location.region,
            "account_id": user.app_metadata["account_id"],
            "cost_per_mile": location.cost_per_mile,
            "minimum_shipping_cost": location.minimum_shipping_cost,
            "pickup_region": location.pickup_region,
            "average_delivery_days": location.average_delivery_days,
        }
        location_new_dict = {key: value for key, value in location_new_dict.items() if value is not None}

        location_db = await location_price_crud.get_one(user.app_metadata["account_id"], location_id)

        if location.cost_per_mile and location_db.cost_per_mile != location.cost_per_mile:
            products = location_db.container_products
            updated_product_list = []
            for product in products:
                updated_product_new: ContainerProduct = ContainerProduct(
                    **{"id": product.id, "cost_per_mile": location.cost_per_mile}
                )
                updated_product_list.append(updated_product_new)
            if len(updated_product_list) > 0:
                await container_product_crud.bulk_update(
                    updated_product_list, ['cost_per_mile'], len(updated_product_list)
                )

        if location.minimum_shipping_cost and location_db.minimum_shipping_cost != location.minimum_shipping_cost:
            products = location_db.container_products
            updated_product_list = []
            for product in products:
                updated_product_new: ContainerProduct = ContainerProduct(
                    **{"id": product.id, "minimum_shipping_cost": location.minimum_shipping_cost}
                )
                updated_product_list.append(updated_product_new)

            if len(updated_product_list) > 0:
                await container_product_crud.bulk_update(
                    updated_product_list, ['minimum_shipping_cost'], len(updated_product_list)
                )

        return await location_price_crud.update(
            user.app_metadata["account_id"], location_id, LocationPriceIn(**location_new_dict)
        )

    return await location_price_crud.create(
        LocationPriceIn(
            **{
                "city": location.city,
                "state": location.state,
                "province": location.province,
                "zip": location.zip,
                "region": location.region,
                "account_id": user.app_metadata["account_id"],
                "cost_per_mile": location.cost_per_mile,
                "minimum_shipping_cost": location.minimum_shipping_cost,
                "pickup_region": location.pickup_region,
                "average_delivery_days": location.average_delivery_days,
            }
        )
    )


async def get_container_locations(user: Auth0User):
    return await location_price_crud.get_all(user.app_metadata["account_id"])


async def get_container_location(container_location_id: str, user: Auth0User) -> LocationPriceOut:
    try:
        return await location_price_crud.get_one(user.app_metadata["account_id"], container_location_id)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location does not exist")


async def create_location(container_location: CreateUpdateLocationPrice, user: Auth0User) -> LocationPriceOutSchema:
    await FastAPICache.clear(namespace="locations")
    return await save_location(container_location, user)


async def update_location(
    container_location_id: str, container_location: CreateUpdateLocationPrice, user: Auth0User
) -> LocationPriceOutSchema:
    return await save_location(container_location, user, container_location_id)


async def delete_container_location(container_location_id: str, user: Auth0User):
    await location_price_crud.delete_one(user.app_metadata["account_id"], container_location_id)
    return Status(message="Deleted location")
