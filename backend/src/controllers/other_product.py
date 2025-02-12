# Python imports
from typing import List

# Pip imports
from fastapi import HTTPException, status
from tortoise.exceptions import DoesNotExist

# Internal imports
from src.auth.auth import Auth0User
from src.crud.other_product_crud import other_product_crud
from src.schemas.other_product import CreateUpdateOtherProduct, OtherProductIn, OtherProductOut
from src.schemas.token import Status


async def save_other_price(
    other_price: CreateUpdateOtherProduct, user: Auth0User, other_price_id: str = None
) -> OtherProductOut:
    other_price_dict = other_price.dict(exclude_unset=True)

    other_price_dict["account_id"] = user.app_metadata.get("account_id")
    product_category_id = None if other_price.product_category_id in (None, "") else other_price.product_category_id
    if other_price_id:
        other_product_new_dict = {
            "name": other_price.name,
            "description": other_price.description,
            "cost_per_mile": 0,
            "minimum_shipping_cost": 0,
            "shipping_time": other_price.shipping_time,
            "product_link": other_price.product_link,
            "in_stock": other_price.in_stock,
            "price": other_price.price,
            "product_category_id": product_category_id,
            "account_id": user.app_metadata.get("account_id"),
        }

        other_product_new_dict = {key: value for key, value in other_product_new_dict.items() if value is not None}
        saved_other_price = await other_product_crud.update(
            user.app_metadata.get("account_id"), other_price_id, OtherProductIn(**other_product_new_dict)
        )
    else:
        product_category_id = None if other_price.product_category_id in (None, "") else other_price.product_category_id
        saved_other_price = await other_product_crud.create(
            OtherProductIn(
                **{
                    "name": other_price.name,
                    "description": other_price.description,
                    "cost_per_mile": 0,
                    "minimum_shipping_cost": 0,
                    "shipping_time": other_price.shipping_time,
                    "product_link": other_price.product_link,
                    "in_stock": other_price.in_stock,
                    "price": other_price.price,
                    "account_id": user.app_metadata.get("account_id"),
                    "product_category_id": product_category_id,
                }
            )
        )

    return saved_other_price


async def get_all_other_products(user: Auth0User) -> List[OtherProductOut]:
    res = await other_product_crud.get_all(user.app_metadata.get("account_id"))
    return res


async def get_other_product(other_price_id: str, user: Auth0User) -> OtherProductOut:
    try:
        return await other_product_crud.get_one(user.app_metadata.get("account_id"), other_price_id)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Other price does not exist")


async def create_other_product(other_price: CreateUpdateOtherProduct, user: Auth0User) -> OtherProductOut:
    return await save_other_price(other_price, user)


async def update_other_product(
    other_price_id: str, other_price: CreateUpdateOtherProduct, user: Auth0User
) -> OtherProductOut:
    result = await save_other_price(other_price, user, other_price_id)
    return result


async def delete_other_product(other_price_id: str, user: Auth0User) -> Status:
    await other_product_crud.delete_one(user.app_metadata.get("account_id"), other_price_id)
    return Status(message=f"Deleted other price {other_price_id}")
