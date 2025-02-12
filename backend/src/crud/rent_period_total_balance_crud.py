# ...

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.rent_period_total_balance import RentPeriodTotalBalance
from src.schemas.rent_period_total_balance import RentPeriodTotalBalanceIn, RentPeriodTotalBalanceOut


rent_period_total_balance_crud = TortoiseCRUD(
    schema=RentPeriodTotalBalanceOut,
    create_schema=RentPeriodTotalBalanceIn,
    update_schema=RentPeriodTotalBalanceIn,
    db_model=RentPeriodTotalBalance,
)
