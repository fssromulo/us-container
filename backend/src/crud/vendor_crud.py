# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.inventory.vendor import Vendor
from src.schemas.vendors import VendorInSchema, VendorOutSchema


vendor_crud = TortoiseCRUD(
    schema=VendorOutSchema, create_schema=VendorInSchema, update_schema=VendorInSchema, db_model=Vendor
)
