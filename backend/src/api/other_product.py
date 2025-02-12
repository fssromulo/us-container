# Python imports
from typing import List

# Pip imports
from fastapi import APIRouter, Depends, status
from tortoise.contrib.fastapi import HTTPNotFoundError

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import other_product, product_category
from src.dependencies import auth
from src.schemas.other_product import CreateUpdateOtherProduct, OtherProductOut
from src.schemas.product_category import CreateUpdateProductCategory, ProductCategoryOut
from src.schemas.token import Status


router = APIRouter(
    tags=["other_product"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("/products", response_model=List[OtherProductOut])
async def get_all_other_product(user: Auth0User = Depends(auth.get_user)):
    return await other_product.get_all_other_products(user)


@router.get("/product/{other_product_id}", response_model=OtherProductOut)
async def get_other_product(other_product_id: str, user: Auth0User = Depends(auth.get_user)) -> OtherProductOut:
    return await other_product.get_other_product(other_product_id, user)


@router.post("/product", response_model=OtherProductOut, status_code=status.HTTP_201_CREATED)
async def create_other_product(
    other_product_data: CreateUpdateOtherProduct, user: Auth0User = Depends(auth.get_user)
) -> OtherProductOut:
    return await other_product.create_other_product(other_product_data, user)


@router.patch(
    "/product/{other_product_id}",
    response_model=OtherProductOut,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def update_other_product(
    other_product_id: str, other_product_data: CreateUpdateOtherProduct, user: Auth0User = Depends(auth.get_user)
) -> OtherProductOut:
    return await other_product.update_other_product(other_product_id, other_product_data, user)


@router.delete(
    "/product/{other_product_id}",
    response_model=Status,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPNotFoundError}},
)
async def delete_other_product(other_product_id: str, user: Auth0User = Depends(auth.get_user)):
    return await other_product.delete_other_product(other_product_id, user)


# Product Categories Endpoints
@router.get("/product_categories")
async def get_all_product_categories(user: Auth0User = Depends(auth.get_user)):
    return await product_category.get_all_product_categories(user)


@router.get("/product_category/{other_product_id}", response_model=ProductCategoryOut)
async def get_other_product(other_product_id: str, user: Auth0User = Depends(auth.get_user)) -> ProductCategoryOut:
    return await product_category.get_product_category(other_product_id, user)


@router.post("/product_category", response_model=ProductCategoryOut, status_code=status.HTTP_201_CREATED)
async def create_product_category(
    other_product_data: CreateUpdateProductCategory, user: Auth0User = Depends(auth.get_user)
) -> ProductCategoryOut:
    return await product_category.create_product_category(other_product_data, user)


@router.patch(
    "/product_category/{other_product_id}", response_model=ProductCategoryOut, status_code=status.HTTP_201_CREATED
)
async def update_product_category(
    other_product_id: str, other_product_data: CreateUpdateProductCategory, user: Auth0User = Depends(auth.get_user)
) -> ProductCategoryOut:
    return await product_category.update_product_category(other_product_id, other_product_data, user)


@router.delete("/product_category/{other_product_id}", status_code=status.HTTP_201_CREATED)
async def update_product_category(other_product_id: str, user: Auth0User = Depends(auth.get_user)):
    return await product_category.delete_product_category(other_product_id, user)
