# Python imports
from datetime import datetime

# Internal imports
from src.crud.order_card_info_crud import order_credit_card_crud
from src.crud.order_crud import order_crud
from src.crud.rent_period_balance_crud import rent_period_balance_crud
from src.crud.rent_period_tax_balance_crud import rent_period_tax_balance_crud
from src.crud.rent_period_fee_balance_crud import rent_period_fee_balance_crud
from src.schemas.reports import FilterObject


async def get_orders_summary_rentals(filters: FilterObject):
    date_format = '%Y-%m-%dT%H:%M:%S.%fZ'

    result = await order_crud.get_all_orders(
        datetime.strptime(filters.begin_date, date_format), datetime.strptime(filters.end_date, date_format), filters.account_id, filters.purchase_type
    )

    rent_period_balances = []
    rent_period_tax_balances = []
    rent_period_fee_balances = []

    for tt in result['transaction_types']:
        try:
            if not tt.rent_period:
                continue
            rent_period_balances += await rent_period_balance_crud.get_all_by_rent_period_id(tt.rent_period.id)
            rent_period_tax_balances += await rent_period_tax_balance_crud.get_all_by_rent_period_id(tt.rent_period.id)
            rent_period_fee_balances += await rent_period_fee_balance_crud.get_all_by_rent_period_id(tt.rent_period.id)
        except Exception as e:
            pass

    result['rent_period_balances'] = remove_duplicates(rent_period_balances)
    result['rent_period_tax_balances'] = remove_duplicates(rent_period_tax_balances)
    result['rent_period_fee_balances'] = remove_duplicates(rent_period_fee_balances)

    return result


def remove_duplicates(models):
    unique_models = {}
    for model in models:
        # Assuming each model has an 'id' attribute
        if model.id not in unique_models:
            unique_models[model.id] = model

    # Convert the dictionary values back to a list
    return list(unique_models.values())
