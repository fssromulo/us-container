
# ...

from src.schemas.order_tax import (
    OrderTaxIn,
    OrderTaxOut,
)

from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.order_tax import OrderTax

order_tax_crud = TortoiseCRUD(
    schema=OrderTaxOut,
    create_schema=OrderTaxIn,
    update_schema=OrderTaxIn,
    db_model=OrderTax,
)
