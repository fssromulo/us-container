# Pip imports
from fastapi import HTTPException, status
from tortoise.exceptions import DoesNotExist

# Internal imports
from src.auth.auth import Auth0User
from src.crud.depot_crud import depot_crud, DepotCrud
from src.crud.note_crud import note_crud
from src.database.models.inventory.depot import Depot
from src.schemas.depot import CreateOrUpdateDepot, DepotInSchema, DepotOutSchema
from src.schemas.notes import NoteInSchema
from src.schemas.token import Status


async def save_depot(depot: CreateOrUpdateDepot, user: Auth0User, depot_id: str = None) -> Depot:
    note = depot.note
    del depot.note
    depot_dict = depot.dict(exclude_unset=True)

    depot_dict["account_id"] = user.app_metadata.get("account_id")

    if depot_id:
        saved_depot = await depot_crud.update(
            user.app_metadata.get("account_id"), depot_id, DepotInSchema(**depot_dict)
        )
    else:
        saved_depot = await depot_crud.create(DepotInSchema(**depot_dict))

    if note:
        await note_crud.create(
            NoteInSchema(
                title=note.title,
                content=note.content,
                author_id=user.app_metadata.get("id"),
                depot_id=saved_depot.id,
            )
        )

    return saved_depot


async def get_all_container_depots(user: Auth0User) -> list[DepotOutSchema]:
    return await depot_crud.get_all(user.app_metadata.get("account_id"))


async def get_container_depot(container_depot_id: str, user: Auth0User) -> DepotOutSchema:
    try:
        return await depot_crud.get_one(user.app_metadata.get("account_id"), container_depot_id)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container depot does not exist")

async def get_container_depot_by_name(container_depot_name:str, user: Auth0User) -> DepotOutSchema:
    try:
        return await DepotCrud.get_by_name(user.app_metadata.get("account_id"), container_depot_name)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container depot does not exist")


async def create_depot(container_depot: CreateOrUpdateDepot, user: Auth0User) -> DepotOutSchema:
    return await save_depot(container_depot, user)


async def update_depot(
    container_depot_id: str, container_depot: CreateOrUpdateDepot, user: Auth0User
) -> DepotOutSchema:
    return await save_depot(container_depot, user, container_depot_id)


async def delete_container_depot(container_depot_id: str, user: Auth0User):
    await depot_crud.delete_one(user.app_metadata.get("account_id"), container_depot_id)
    return Status(message="Deleted depot")
