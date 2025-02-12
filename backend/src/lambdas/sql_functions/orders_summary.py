# Python imports
from datetime import datetime

# Internal imports
from src.crud.order_card_info_crud import order_credit_card_crud
from src.crud.order_crud import order_crud
from src.crud.order_fee_balance_crud import order_fee_balance_crud
from src.crud.subtotal_balance_crud import subtotal_balance_crud
from src.crud.tax_balance_crud import tax_balance_crud
from src.schemas.reports import FilterObject


async def get_orders_summary(filters: FilterObject):
    date_format = '%Y-%m-%dT%H:%M:%S.%fZ'

    result = await order_crud.get_all_orders(
        datetime.strptime(filters.begin_date, date_format), datetime.strptime(filters.end_date, date_format), filters.account_id, filters.purchase_type
    )

    result_credit_card = await order_credit_card_crud.get_all_between_dates_including_order(
        filters.account_id,
        datetime.strptime(filters.begin_date, date_format),
        datetime.strptime(filters.end_date, date_format),
        filters.purchase_type,
    )

    result['order_credit_cards'] = result_credit_card['order_credit_cards']

    tax_balances = []
    subtotal_balances = []
    fee_balances = []

    for tt in result['transaction_types']:
        try:
            if not tt.order:
                continue
            tax_balances += await tax_balance_crud.get_by_order_id(tt.order.id)
            subtotal_balances += await subtotal_balance_crud.get_by_order_id(tt.order.id)
            fee_balances += await order_fee_balance_crud.get_by_order_id(tt.order.id)
        except Exception as e:
            pass
    for tt in result['order_credit_cards']:
        try:
            if not tt.order:
                continue
            tax_balances += await tax_balance_crud.get_by_order_id(tt.order.id)
            subtotal_balances += await subtotal_balance_crud.get_by_order_id(tt.order.id)
            fee_balances += await order_fee_balance_crud.get_by_order_id(tt.order.id)
        except Exception as e:
            pass

    result['tax_balances'] = remove_duplicates(tax_balances)
    result['subtotal_balances'] = remove_duplicates(subtotal_balances)
    result['fee_balances'] = remove_duplicates(fee_balances)

    return result


def remove_duplicates(models):
    unique_models = {}
    for model in models:
        # Assuming each model has an 'id' attribute
        if model.id not in unique_models:
            unique_models[model.id] = model

    # Convert the dictionary values back to a list
    return list(unique_models.values())
