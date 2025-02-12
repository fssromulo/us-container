# Internal imports
from src.crud.rent_period_tax_crud import rent_period_tax_crud
from src.schemas.rent_period_tax import RentPeriodTaxIn, RentPeriodTaxOut


async def create_rent_period_tax(rent_period_tax: RentPeriodTaxIn) -> RentPeriodTaxOut:
    saved_rent_period_tax = await rent_period_tax_crud.create(rent_period_tax)
    return saved_rent_period_tax
