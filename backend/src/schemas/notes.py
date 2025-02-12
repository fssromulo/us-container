# Python imports
from typing import Optional

# Pip imports
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.note import Note


NoteInSchema = pydantic_model_creator(Note, name="NoteIn", exclude=["created_at", "modified_at"], exclude_readonly=True)


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


NoteInSchemaUSAC = pydantic_model_creator(
    Note,
    name="NoteInUSAC",
    include=["id", "title", "content", "author_id", "line_item_id", "order_id", "created_at"],
    exclude_readonly=True,
    config_class=Config,
)

NoteOutSchema = pydantic_model_creator(
    Note,
    name="NoteOut",
    exclude=["modified_at", "author.preferences"],
)


class UpdateNote(BaseModel):
    title: Optional[str]
    content: Optional[str]
    is_public: Optional[bool]


class UpdateNoteIsPublic(BaseModel):
    id: Optional[str]
    content: Optional[str]
