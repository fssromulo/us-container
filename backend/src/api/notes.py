# Python imports
from typing import List

# Pip imports
from fastapi import APIRouter, Depends, BackgroundTasks
from tortoise.contrib.fastapi import HTTPNotFoundError

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import notes
from src.crud.note_crud import note_crud
from src.dependencies import auth
from src.schemas.notes import NoteInSchema, NoteOutSchema, UpdateNote, UpdateNoteIsPublic
from src.schemas.token import Status


router = APIRouter(
    tags=["line_items"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/notes",
    response_model=List[NoteOutSchema],
)
async def get_notes(user: Auth0User = Depends(auth.get_user)):
    return await notes.get_notes(user)


@router.get(
    "/note/{note_id}",
    response_model=NoteOutSchema,
)
async def get_note(note_id: int, user: Auth0User = Depends(auth.get_user)) -> NoteOutSchema:
    return await notes.get_note(note_id, user)


@router.post(
    "/notes",
    response_model=NoteOutSchema,
)
async def create_note(note: NoteInSchema, background_tasks: BackgroundTasks, user: Auth0User = Depends(auth.get_user)) -> NoteOutSchema:
    return await notes.create_note(note, user, background_tasks=background_tasks)


@router.patch(
    "/note/{note_id}",
    response_model=NoteOutSchema,
    responses={404: {"model": HTTPNotFoundError}},
)
async def update_note(note_id: str, note: UpdateNote, user: Auth0User = Depends(auth.get_user)) -> NoteOutSchema:
    return await notes.update_note(note_id, note, user)


@router.patch("/notes_is_public/{order_id}")
async def update_note(order_id: str, note: UpdateNoteIsPublic, user: Auth0User = Depends(auth.get_user)):
    return await notes.update_note_is_public(order_id, note, user)


@router.delete(
    "/note/{note_id}",
    response_model=Status,
    responses={404: {"model": HTTPNotFoundError}},
)
async def delete_note(note_id: int, user: Auth0User = Depends(auth.get_user)):
    return notes.delete_note(note_id, user)
    return await note_crud.delete_one(user.app_metadata["account_id"], note_id)
