# Python imports
from typing import Dict, List

# Pip imports
from fastapi import HTTPException, status
from tortoise.exceptions import DoesNotExist

# Internal imports
from src.auth.auth import Auth0User
from src.controllers.event_controller import send_event
from src.crud.container_attribute_crud import container_attribute_crud
from src.crud.container_product_attribute import container_product_attribute_crud
from src.crud.container_product_crud import container_product_crud
from src.schemas.container_locations import CreateUpdateContainerPrice
from src.schemas.container_product import ContainerProduct, ContainerProductIn, ContainerProductOut, GlobalPodSettings, IsPayOnDeliveryRequest
from src.schemas.container_product_attribute import ContainerProductAttributeIn
from src.schemas.token import Status
from src.utils.utility import make_json_serializable


def process_dimensions(item) -> Dict[str, str]:
    if not item:
        item = "0x0x0"
    dimensions = item.split("x")

    return {"length": str(dimensions[0]), "width": str(dimensions[1]), "height": str(dimensions[2])}


async def get_all_container_attributes():
    pairs = await container_attribute_crud.get_all(1)
    return pairs


async def save_container_price(
    container_price: CreateUpdateContainerPrice, user: Auth0User, container_price_id: str = None
) -> ContainerProductOut:
    container_price_dict = container_price.dict(exclude_unset=True)
    container_price_dict["account_id"] = user.app_metadata.get("account_id")

    dimensions = process_dimensions(container_price.attributes.get('dimensions'))

    pairs = await container_attribute_crud.get_all(1)

    if container_price_id:
        container_product_new_dict = {
            "name": container_price.product_type,
            "description": container_price.description,
            "monthly_price": container_price.monthly_price,
            "cost_per_mile": container_price.cost_per_mile,
            "price": container_price.price,
            "minimum_shipping_cost": container_price.minimum_shipping_cost,
            "container_size": container_price.container_size,
            "location_id": container_price.location_id,
            "length": int(dimensions['length']),
            "width": int(dimensions['width']),
            "height": int(dimensions['height']),
            "condition": container_price.condition,
            "product_type": str(container_price.product_type.name) if container_price.product_type else None,
            "pod": container_price.pod
        }

        container_product_new_dict = {
            key: value for key, value in container_product_new_dict.items() if value is not None
        }
        if not container_price.attributes:
            del container_product_new_dict['high_cube']

        saved_container_price = await container_product_crud.update(
            user.app_metadata.get("account_id"), container_price_id, ContainerProductIn(**container_product_new_dict)
        )

        for pair in pairs:
            if container_price.attributes.get(pair.value, False):
                res = await container_attribute_crud.get_by_name(pair.name)

                found = False
                for cpa in saved_container_price.container_product_attributes:
                    if cpa.container_attribute.id == res.id:
                        found = True
                        break

                if not found:
                    await container_product_attribute_crud.create(
                        ContainerProductAttributeIn(
                            **{"container_product_new_id": saved_container_price.id, "container_attribute_id": res.id}
                        )
                    )
            else:
                res = await container_attribute_crud.get_by_name(pair.name)

                for cpa in saved_container_price.container_product_attributes:
                    if cpa.container_attribute.id == res.id:
                        await container_product_attribute_crud.delete_one(user.app_metadata.get("account_id"), cpa.id)

    else:
        saved_container_price = await container_product_crud.create(
            ContainerProductIn(
                **{
                    "name": container_price.product_type,
                    "description": container_price.description,
                    "monthly_price": container_price.monthly_price,
                    "cost_per_mile": container_price.cost_per_mile,
                    "price": container_price.price,
                    "minimum_shipping_cost": container_price.minimum_shipping_cost,
                    "container_size": container_price.container_size,
                    "location_id": container_price.location_id,
                    "length": int(dimensions['length']),
                    "width": int(dimensions['width']),
                    "height": int(dimensions['height']),
                    "condition": container_price.condition,
                    "product_type": str(container_price.product_type.name) if container_price.product_type else None,
                    "pod": container_price.pod
                }
            )
        )

        for pair in pairs:
            if container_price.attributes.get(pair.value, False):
                res = await container_attribute_crud.get_by_name(pair.name)

                await container_product_attribute_crud.create(
                    ContainerProductAttributeIn(
                        **{"container_product_new_id": saved_container_price.id, "container_attribute_id": res.id}
                    )
                )
        saved_container_price = await container_product_crud.get_one(
            user.app_metadata.get("account_id"), saved_container_price.id
        )

    return saved_container_price


async def get_all_container_prices(user: Auth0User) -> List[ContainerProductOut]:
    res = await container_product_crud.get_all(user.app_metadata.get("account_id"))
    return res


async def set_rental_price(container_size, rental_price, account_id):
    container_product_news: List[ContainerProduct] = await container_product_crud.get_all(account_id)
    container_product_news = [x for x in container_product_news if str(x.container_size) == str(container_size)]

    updated_product_list = []
    for product in container_product_news:
        updated_product_new: ContainerProduct = ContainerProduct(**{"id": product.id, "monthly_price": rental_price})
        updated_product_list.append(updated_product_new)

    await container_product_crud.bulk_update(models=updated_product_list, fields=['monthly_price'])


async def get_container_price(container_price_id: str, user: Auth0User) -> ContainerProductOut:
    try:
        return await container_product_crud.get_one(user.app_metadata.get("account_id"), container_price_id)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container price does not exist")


async def create_container_price(
    container_price: CreateUpdateContainerPrice, user: Auth0User, background_tasks
) -> ContainerProductOut:
    result = await save_container_price(container_price, user)
    # send event to event controller
    background_tasks.add_task(
        send_event,
        user.app_metadata['account_id'],
        str(result.id),
        make_json_serializable(result.dict()),
        "product",
        "create",
        'create:container_product:create_entry',
    )
    return result


async def update_container_price(
    container_price_id: str, container_price: CreateUpdateContainerPrice, user: Auth0User, background_tasks
) -> ContainerProductOut:
    result = await save_container_price(container_price, user, container_price_id)
    # send event to event controller
    background_tasks.add_task(
        send_event, user.app_metadata['account_id'], str(result.id), make_json_serializable(container_price.dict())
    )
    return result


async def delete_container_price(container_price_id: str, user: Auth0User, background_tasks) -> Status:
    await container_product_crud.delete_one(user.app_metadata.get("account_id"), container_price_id)
    # send event to event controller
    background_tasks.add_task(
        send_event, user.app_metadata['account_id'], str(container_price_id), {}, "product", "delete"
    )
    return Status(message=f"Deleted container price {container_price_id}")


async def set_global_pod(body: GlobalPodSettings, user):
    all_products = await container_product_crud.get_all(user.app_metadata['account_id'])

    types_ids = []
    for type in body.types:
        res = await container_attribute_crud.get_by_value(type)
        types_ids.append(res.id)

    products_to_update = []
    for product in all_products:
        if len(product.container_product_attributes) != len(types_ids):
            continue

        continue_loop = False
        for cpa in product.container_product_attributes:
            if cpa.container_attribute.id not in types_ids:
                continue_loop = True
                break

        if continue_loop:
            continue

        if product.condition != body.condition:
            continue
        
        if body.locations and str(product.location.id) not in body.locations:
            continue

        products_to_update.append(ContainerProduct(id=product.id, account_id=user.app_metadata['account_id'], pod=body.state))

    if products_to_update:
        await container_product_crud.bulk_update(products_to_update, ["pod"])
    
async def is_pay_on_delivery(body: IsPayOnDeliveryRequest, user):
    all_products = await container_product_crud.get_all(user.app_metadata['account_id'])

    for product in all_products:
        if product.title == body.product_name and product.location.city == body.location_name:
            return product.pod 
        
    return False
    