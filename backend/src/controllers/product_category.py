# Python imports
from typing import List

# Pip imports
from fastapi import HTTPException, status
from tortoise.exceptions import DoesNotExist

# Internal imports
from src.auth.auth import Auth0User
from src.crud.product_category import product_category_crud
from src.schemas.product_category import CreateUpdateProductCategory,  ProductCategoryOut, ProductCategoryIn
from src.schemas.token import Status


async def save_product_category(
    product_category: CreateUpdateProductCategory, user: Auth0User, product_category_id: str = None
) -> ProductCategoryOut:
    # product_category_dict = product_category.dict(exclude_unset=True)

    if product_category_id:
        other_product_new_dict = {
            "name": product_category.name,
            "account_id": user.app_metadata.get("account_id")
        }

        other_product_new_dict = {key: value for key, value in other_product_new_dict.items() if value is not None}
        saved_other_price = await product_category_crud.update(
            user.app_metadata.get("account_id"), product_category_id, ProductCategoryIn(**other_product_new_dict)
        )
    else:
        saved_other_price = await product_category_crud.create(ProductCategoryIn(**{
            "name": product_category.name,
            "account_id": user.app_metadata.get("account_id")
        }))
    return saved_other_price


async def get_all_product_categories(user: Auth0User):
    res = await product_category_crud.get_all(user.app_metadata.get("account_id"))
    return res

async def get_product_category(other_price_id: str, user: Auth0User) -> ProductCategoryOut:
    try:
        return await product_category_crud.get_one(user.app_metadata.get("account_id"), other_price_id)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category does not exist")


async def create_product_category(
    other_price: CreateUpdateProductCategory, user: Auth0User
) :
    return await save_product_category(other_price, user)


async def update_product_category(
    other_price_id: str, other_price: CreateUpdateProductCategory, user: Auth0User
) -> ProductCategoryOut:
    result = await save_product_category(other_price, user, other_price_id)
    return result

async def delete_product_category(product_category_id: str, user: Auth0User) -> Status:
    await product_category_crud.delete_one(user.app_metadata.get("account_id"), product_category_id)
    return Status(message=f"Deleted product category {product_category_id}")
