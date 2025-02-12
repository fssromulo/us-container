# # Python imports

# # import sys
# # Python imports
# from datetime import datetime

# # Pip imports
# import pytz
# from loguru import logger

# # Internal imports
# from src.database.tortoise_init import init_models


# # enable schemas to read relationship between models
# # flakes8: noqa
# init_models()

# # Internal imports
# from src.crud.order_card_info_crud import order_credit_card_crud  # noqa: E402
# from src.crud.order_crud import order_crud  # noqa: E402
# from src.database.models.orders.order import Order  # noqa: E402
# from src.schemas.accounts import AccountOutSchema  # noqa: E402
# from src.schemas.order_credit_card import OrderCreditCardInSchema  # noqa: E402
# from src.services.payment.usa_epay_service import quick_sale as usa_epay_quick_sale  # noqa: E402


# async def handle_usa_epay_accounts(account: AccountOutSchema, api_key):
#     # all_customers = get_all_data(usa_epay_get_customers, api_key)

#     orders = await order_crud.search_orders(
#         account.id,
#         status="Current,Delinquent",
#         order_types="RENT,RENT_TO_OWN",
#     )

#     # result_data = []

#     # for customer in all_customers:
#     #     transactions = get_all_data(usa_epay_get_customer_transactions, api_key, customer['key'])

#     #     for transaction in transactions:
#     #         found_order = next((o for o in orders if o.display_order_id == transaction['invoice']), None)

#     #         if found_order:
#     #             result_dict = {
#     #                 'customer': customer,
#     #                 'transaction': transaction,
#     #                 'order': found_order.dict(),
#     #             }
#     #             result_data.append(result_dict)

#     # # Use 'display_order_id' as the key in both sorting and grouping
#     # result_data.sort(key=lambda x: x['order']['display_order_id'])

#     # grouped_data = {}
#     # for key, group in groupby(result_data, key=lambda x: x['order']['display_order_id']):
#     #     grouped_data[key] = list(group)

#     for order in orders:
#         logger.info(order)
#         order = order.dict()
#         # results.sort(key=lambda x: x['transaction']['created'], reverse=True)
#         order['credit_card'].sort(key=lambda x: x['created_at'], reverse=True)
#         today: datetime = datetime.now(pytz.utc).date()
#         charge_customer_now = await verify_charge_day(
#             order,
#             account,
#             order['credit_card'][-1]['response_from_gateway'],
#             order['credit_card'][0]['response_from_gateway'],
#             today,
#             False,
#         )
#         most_recent_transaction_failed = (
#             order['credit_card'][0]['response_from_gateway'].get('result_code') != 'A'
#             and order['credit_card'][0]['response_from_gateway'].get('result') != 'Approved'
#         )
#         if most_recent_transaction_failed:
#             charge_customer_now = await handle_late_fee(
#                 order,
#                 account,
#                 order['credit_card'][-1]['response_from_gateway'],
#                 order['credit_card'][0]['response_from_gateway'],
#             )
#             # latest_order_balance = await total_order_balance_crud.get_latest_order_balance(order['id'])

#         logger.info(f"Charge customer now: {charge_customer_now}")

#         if charge_customer_now:
#             logger.info(f"Charging customer {order['customer']['email']} for order {order['display_order_id']}")
#             transaction_to_reuse = order['credit_card'][0]['response_from_gateway']
#             latest_transaction = usa_epay_quick_sale(
#                 tran_key=transaction_to_reuse['key'], amount=order['calculated_monthly_owed_total'], api_key=api_key
#             )

#             if latest_transaction.get('result_code') == 'A' and latest_transaction.get('result') == 'Approved':
#                 logger.info('Transaction successful')
#                 await order_crud.update(account.id, order['id'], Order(status='Current'))
#                 # create_order_balance: TotalOrderBalanceIn = TotalOrderBalanceIn(remaining_balance=0, order_id=order['id'])
#                 # await total_order_balance_crud.create(create_order_balance)

#                 # # reset order balance back to monthly owed
#                 # create_order_balance: TotalOrderBalanceIn = TotalOrderBalanceIn(remaining_balance=order['calculated_monthly_owed_total'], order_id=order.id)
#                 # await total_order_balance_crud.create(create_order_balance)

#             if latest_transaction.get('result_code') != 'A' and latest_transaction.get('result') != 'Approved':
#                 logger.info('Transaction failed')
#                 # You can handle the case where the transaction failed

#             credit_card_entry = OrderCreditCardInSchema(
#                 order_id=order['id'],
#                 merchant_name="",
#                 card_type="",
#                 response_from_gateway=latest_transaction,
#             )
#             await order_credit_card_crud.create(credit_card_entry)


# # if __name__ == "__main__":  # TODO COMMENT THIS OUT BEFORE PUSHING UP
# #     handler(None, None)
