# Pip imports
from fastapi import BackgroundTasks, HTTPException
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist

# Internal imports
from src.auth.auth import Auth0User
from src.controllers.event_controller import send_event
from src.schemas.container_locations import CreateUpdateLocationPrice, LocationPriceInSchema, LocationPriceOutSchema
from src.schemas.notes import NoteInSchema, NoteOutSchema, UpdateNote, UpdateNoteIsPublic
from src.schemas.token import Status
from src.utils.utility import make_json_serializable
from src.crud.assistant_crud import assistant_crud
from ..crud.note_crud import note_crud
from src.utils.order_update_in_cache import clear_cache

from loguru import logger

async def get_notes(user: Auth0User):
    return await note_crud.get_all(user.app_metadata["account_id"])


async def get_note(note_id: int, user: Auth0User) -> NoteOutSchema:
    try:
        return await note_crud.get_note(note_id)
    except DoesNotExist:
        raise HTTPException(
            status_code=404,
            detail="Note does not exist",
        )


async def create_note(note: NoteInSchema, user: Auth0User, background_tasks: BackgroundTasks) -> NoteOutSchema:
    if note.author_id is None:
        note.author_id = str(user.id)[6:]
    saved_order = await note_crud.create(note)
    # send event to event controller
    await send_event(
        user.app_metadata['account_id'], str(note.order_id), make_json_serializable(note.dict()), "note", "create"
    )

    user_id = user.id.replace("auth0|", "")
    try:
        assistant = await assistant_crud.get_by_assistant_id(user_id)
    except HTTPException as e:
        if e.status_code == 404:
            assistant = None
        else:
            raise e

    user_ids = [user_id]
    if assistant:
        user_ids.append(assistant.manager.id)

    if saved_order.user.id != user_id:
        user_ids.append(saved_order.user.id)

    statuses = [saved_order.status]
    if saved_order.status in ['Paid', 'first_payment_received', 'Pod']:
        statuses += ['To_Deliver']

    if saved_order.type == 'RENT' and saved_order.status in ['Delinquent', 'Delivered']:
        statuses += ['On_Rent']

    try:
        clear_cache(statuses, saved_order.type, user_ids, user.app_metadata['account_id'])
    except Exception as e:
        logger.info(str(e))
    return saved_order


async def update_note(note_id: int, note: UpdateNote, user: Auth0User) -> NoteOutSchema:
    return await note_crud.update(user.app_metadata["account_id"], note_id, note)


async def delete_note(note_id: int, user: Auth0User):
    return await note_crud.delete_one(user.app_metadata["account_id"], note_id)


async def update_note_is_public(order_id: str, note: UpdateNoteIsPublic, user):
    if note.content == 'private':
        await note_crud.update(user.app_metadata["account_id"], note.id, UpdateNote(is_public=False))
    else:
        notes = await note_crud.get_all_notes_in_order(order_id)

        for note_model in notes:
            if str(note_model.id) == str(note.id):
                await note_crud.update(user.app_metadata["account_id"], note.id, UpdateNote(is_public=True))
            else:
                if note_model.is_public == True:
                    await note_crud.update(user.app_metadata["account_id"], note_model.id, UpdateNote(is_public=False))
