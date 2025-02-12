# ...

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.rent_period_tax import RentPeriodTax
from src.schemas.rent_period_tax import RentPeriodTaxIn, RentPeriodTaxOut


rent_period_tax_crud = TortoiseCRUD(
    schema=RentPeriodTaxOut,
    create_schema=RentPeriodTaxIn,
    update_schema=RentPeriodTaxIn,
    db_model=RentPeriodTax,
)
