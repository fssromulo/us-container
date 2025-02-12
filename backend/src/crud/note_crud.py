# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.note import Note
from src.schemas.notes import NoteInSchema, NoteOutSchema, UpdateNote


class NoteCrud(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = NoteOutSchema
        self.create_schema = NoteInSchema
        self.update_schema = UpdateNote
        self.db_model = Note
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=50,
        )

    async def get_all_notes_in_order(self, order_id):
        query = self.db_model.filter(order_id=order_id)
        return await self.schema.from_queryset(query)

    async def get_public_note(self, order_id):
        query = self.db_model.filter(order_id=order_id, is_public=True)
        return await self.schema.from_queryset(query)


note_crud = NoteCrud()
