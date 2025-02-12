# Python imports
from typing import List

# Pip imports
from fastapi import HTTPException, status
from tortoise.exceptions import DoesNotExist

# Internal imports
from src.auth.auth import Auth0User
from src.crud.driver_crud import driver_crud
from src.crud.note_crud import note_crud
from src.schemas.driver import DriverInSchema, DriverOutSchema, UpdateDriver
from src.schemas.notes import NoteInSchema
from src.schemas.token import Status


async def save_driver(driver: UpdateDriver, user: Auth0User, driver_id: str = None) -> DriverOutSchema:
    note = driver.note
    del driver.note
    driver_dict = driver.dict(exclude_unset=True)
    driver_dict["account_id"] = user.app_metadata.get("account_id")

    if driver_id:
        saved_driver = await driver_crud.update(
            user.app_metadata.get("account_id"), driver_id, DriverInSchema(**driver_dict)
        )
    else:
        saved_driver = await driver_crud.create(DriverInSchema(**driver_dict))

    if note:
        await note_crud.create(
            NoteInSchema(
                title=note.title,
                content=note.content,
                author_id=user.app_metadata["id"],
                driver_id=saved_driver.id,
            )
        )
    return saved_driver


async def get_all_drivers(user: Auth0User) -> List[DriverOutSchema]:
    result = await driver_crud.get_all(user.app_metadata.get("account_id"))
    return [x for x in result if not x.is_archived]

async def get_driver(driver_id: str, user: Auth0User) -> DriverOutSchema:
    try:
        return await driver_crud.get_one(user.app_metadata.get("account_id"), driver_id)
    except DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Container driver does not exist")


async def create_driver(driver: UpdateDriver, user: Auth0User) -> DriverOutSchema:
    return await save_driver(driver=driver, user=user)


async def update_container_driver(driver_id: str, driver: UpdateDriver, user: Auth0User) -> DriverOutSchema:
    return await save_driver(driver=driver, user=user, driver_id=driver_id)


async def delete_container_driver(driver_id: str, user: Auth0User) -> Status:
    await driver_crud.update(
        user.app_metadata.get("account_id"), driver_id, DriverInSchema(account_id=user.app_metadata.get("account_id"), is_archived=True)
    )
    return Status(message="Deleted driver")
