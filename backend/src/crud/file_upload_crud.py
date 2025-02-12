
from src.schemas.file_upload import (
    FileUploadInSchema,
    FileUploadOutSchema
)

from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.file_upload import FileUpload

file_upload_crud = TortoiseCRUD(
    schema=FileUploadOutSchema,
    create_schema=FileUploadInSchema,
    update_schema=FileUploadInSchema,
    db_model=FileUpload
)