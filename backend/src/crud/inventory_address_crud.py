# ...

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.inventory_address import InventoryAddress
from src.schemas.inventory_address import InventoryAddressIn, InventoryAddressOut


inventory_address_crud = TortoiseCRUD(
    schema=InventoryAddressOut,
    create_schema=InventoryAddressIn,
    update_schema=InventoryAddressIn,
    db_model=InventoryAddress,
)
