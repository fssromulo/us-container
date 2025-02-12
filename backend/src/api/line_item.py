# Python imports
from typing import List

# Pip imports
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import line_item
from src.dependencies import auth
from src.schemas.line_items import LineItemOut, UpdateLineItem, UpdateLineItemExtra
from src.schemas.token import Status


router = APIRouter(
    tags=["line_items"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("/line_item/{line_item_id}", response_model=LineItemOut)
async def get_line_item(line_item_id: str, user: Auth0User = Depends(auth.get_user)) -> LineItemOut:
    return await line_item.get_line_item(line_item_id, user)


@router.patch("/line_item", response_model=List[LineItemOut])
async def update_line_item(
    line_item_schemas: List[UpdateLineItem], background_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)
) -> List[LineItemOut]:
    result = await line_item.update_line_item(line_item_schemas, user, background_tasks=background_tasks)

    return result


@router.patch("/line_item_extra", response_model=List[LineItemOut])
async def update_line_item_extra(
    line_item_schemas: UpdateLineItemExtra, background_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)
) -> List[LineItemOut]:
    return await line_item.update_line_item(
        line_item_schemas.lineItems,
        user,
        line_item_schemas.inventoryIdsToMakeAvailable,
        line_item_schemas.move_out_date,
        line_item_schemas.move_out_type,
        line_item_schemas.is_move_out,
        background_tasks=background_tasks,
    )


@router.get("/line_item/pickup_email/{line_item_id}")
async def send_pickup_email(line_item_id: str, background_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)):
    return await line_item.send_pickup_email(line_item_id, user, background_tasks)


@router.get("/line_item/inventory/{inventory_id}")
async def get_line_item_by_inventory_id(
    inventory_id: str, user: Auth0User = Depends(auth.get_user)
) -> list[LineItemOut]:
    return await line_item.get_line_item_by_inventory_id(inventory_id, user)


@router.delete("/line_item/{line_item_id}", response_model=Status)
async def delete_line_item(line_item_id: str, user: Auth0User = Depends(auth.get_user)):
    delete_line_item = [p for p in user.permissions if p == "delete:order_column-line_item"]
    if not delete_line_item:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete the line item",
        )
    return await line_item.delete_line_item(line_item_id, user)
