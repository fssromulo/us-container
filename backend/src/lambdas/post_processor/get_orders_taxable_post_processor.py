# Python imports
import copy

# Pip imports
from loguru import logger
from tortoise.queryset import QuerySet


def get_orders_taxable_post_processor(data):
    list_results = []
    list_of_transactions = []
    for tt in data['transaction_types']:
        list_of_transactions.append(
            {
                "amount": tt.amount,
                "created_at": tt.transaction_effective_date,
                "type": "transaction_type",
                "id": tt.id,
                "order": tt.order,
                "payment_type": tt.payment_type,
            }
        )

    # credit_card = data['order_credit_cards']
    # for cc in credit_card:
    #     list_of_transactions.append(
    #         {
    #             "amount": cc.response_from_gateway['payment_amount'],
    #             "created_at": cc.created_at,
    #             "type": "credit_card",
    #             "id": cc.id,
    #             "order": cc.order,
    #             "payment_type": "credit_card",
    #         }
    #     )

    for tt in list_of_transactions:
        order = tt['order']
        if order is None:
            continue

        # Taxed subtotal
        transaction_subtotal_balances = sorted(data['subtotal_balances'], key=lambda x: x.created_at)
        transaction_subtotal_balances = [x for x in transaction_subtotal_balances if x.order_id == order.id]
        prev_balance = None
        crt_balance = None
        taxed_subtotal_sum_amount = 0
        if order and order.calculated_order_tax() > 0:
            for tsb in transaction_subtotal_balances:
                prev_balance = crt_balance
                crt_balance = tsb

                if not prev_balance or not crt_balance:
                    continue

                if tt['type'] == 'transaction_type':
                    if tsb.transaction_type_id == tt['id']:
                        taxed_subtotal_sum_amount += prev_balance.balance - crt_balance.balance
                else:
                    if tsb.order_credit_card_id == tt['id']:
                        taxed_subtotal_sum_amount += prev_balance.balance - crt_balance.balance

        transaction_order_fee_balances = sorted(data['fee_balances'], key=lambda x: x.created_at)
        transaction_order_fee_balances = [x for x in transaction_order_fee_balances if x.order_id == order.id]

        taxable_fee_sum_amount = 0

        fee_ids_set = set()
        for tsb in transaction_order_fee_balances:
            fee_ids_set.add(tsb.fee_id)

        for fee_id in fee_ids_set:
            crt_fee_id_balances = [x for x in transaction_order_fee_balances if x.fee_id == fee_id]

            if not order or fee_id not in [x.id for x in order.fees if x.type.is_taxable]:
                continue

            prev_balance = None
            crt_balance = None
            for tsb in crt_fee_id_balances:
                prev_balance = crt_balance
                crt_balance = tsb

                if not prev_balance or not crt_balance:
                    continue

                if tt['type'] == 'transaction_type':
                    if tsb.transaction_type_id == tt['id']:
                        taxable_fee_sum_amount += prev_balance.remaining_balance - crt_balance.remaining_balance
                else:
                    if tsb.order_credit_card_id == tt['id']:
                        taxable_fee_sum_amount += prev_balance.remaining_balance - crt_balance.remaining_balance

        # Add taxable fees to the subtotal sum amount
        taxed_subtotal_sum_amount += taxable_fee_sum_amount

        # Not taxed subtotal
        transaction_subtotal_balances = sorted(data['subtotal_balances'], key=lambda x: x.created_at)
        transaction_subtotal_balances = [x for x in transaction_subtotal_balances if x.order_id == order.id]

        prev_balance = None
        crt_balance = None
        not_taxed_subtotal_sum_amount = 0
        if order and order.calculated_order_tax() == 0:
            for tsb in transaction_subtotal_balances:
                prev_balance = crt_balance
                crt_balance = tsb

                if not prev_balance or not crt_balance:
                    continue

                if tt['type'] == 'transaction_type':
                    if tsb.transaction_type_id == tt['id']:
                        not_taxed_subtotal_sum_amount += prev_balance.balance - crt_balance.balance
                else:
                    if tsb.order_credit_card_id == tt['id']:
                        not_taxed_subtotal_sum_amount += prev_balance.balance - crt_balance.balance

        transaction_order_fee_balances = sorted(data['fee_balances'], key=lambda x: x.created_at)
        transaction_order_fee_balances = [x for x in transaction_order_fee_balances if x.order_id == order.id]

        non_taxable_fee_sum_amount = 0

        fee_ids_set = set()
        for tsb in transaction_order_fee_balances:
            fee_ids_set.add(tsb.fee_id)

        for fee_id in fee_ids_set:
            crt_fee_id_balances = [x for x in transaction_order_fee_balances if x.fee_id == fee_id]

            if not order or fee_id in [x.id for x in order.fees if x.type.is_taxable]:
                continue

            prev_balance = None
            crt_balance = None
            for tsb in crt_fee_id_balances:
                prev_balance = crt_balance
                crt_balance = tsb

                if not prev_balance or not crt_balance:
                    continue

                if tt['type'] == 'transaction_type':
                    if tsb.transaction_type_id == tt['id']:
                        non_taxable_fee_sum_amount += prev_balance.remaining_balance - crt_balance.remaining_balance
                else:
                    if tsb.order_credit_card_id == tt['id']:
                        non_taxable_fee_sum_amount += prev_balance.remaining_balance - crt_balance.remaining_balance

        # Add tax exempt fees to the subtotal sum amount
        not_taxed_subtotal_sum_amount += non_taxable_fee_sum_amount

        transaction_tax_balances = sorted(data['tax_balances'], key=lambda x: x.created_at)
        transaction_tax_balances = [x for x in transaction_tax_balances if x.order_id == order.id]

        prev_balance = None
        crt_balance = None
        has_tax = order.calculated_order_tax() > 0
        tax_sum_amount = 0

        if has_tax:
            for tsb in transaction_tax_balances:
                prev_balance = crt_balance
                crt_balance = tsb

                if not prev_balance or not crt_balance:
                    continue

                if tt['type'] == 'transaction_type':
                    if tsb.transaction_type_id == tt['id']:
                        tax_sum_amount += prev_balance.balance - crt_balance.balance
                else:
                    if tsb.order_credit_card_id == tt['id']:
                        tax_sum_amount += prev_balance.balance - crt_balance.balance

        if (
            tax_sum_amount == 0
            and taxed_subtotal_sum_amount == 0
            and not_taxed_subtotal_sum_amount == 0
            and taxable_fee_sum_amount == 0
        ):
            continue

        customer_name = ""
        if hasattr(order, 'customer') and order.customer:
            customer_name = (
                order.customer.company_name
                if order.customer.company_name
                else order.customer.first_name + " " + order.customer.last_name
            )

        # AttributeError: 'QuerySet' object has no attribute 'company_name'
        if hasattr(order, 'single_customer') and order.single_customer:
            single_customer = order.single_customer
            customer_name = ""
            # Use isinstance() rather than type() for a typecheck.
            if isinstance(order.single_customer, QuerySet):
                logger.error(f"QuerySet object: {order.single_customer}")
                logger.error(f"QuerySet object type: {type(order.single_customer)}")
                logger.error(f"Order ID: {order.id}")
            else:
                customer_name = (
                    single_customer.company_name
                    if single_customer.company_name
                    else single_customer.first_name + " " + single_customer.last_name
                )

        result = {
            "order_id": order.display_order_id,
            "created": str(tt['created_at']),
            "name": customer_name,
            "taxed_subtotal_paid": taxed_subtotal_sum_amount,
            "total_tax_paid": tax_sum_amount,
            "tax_exempt_subtotal_paid": not_taxed_subtotal_sum_amount,
            "payment_type": tt['payment_type'],
            "container_number": "",
            "total_paid": taxed_subtotal_sum_amount + tax_sum_amount + not_taxed_subtotal_sum_amount,
        }

        first_line_item_set = False
        for line_item in order.line_items:

            item = copy.copy(result)
            if not first_line_item_set:
                first_line_item_set = True
            else:
                item['total_paid'] = "N/A"
                item['tax_exempt_subtotal_paid'] = "N/A"
                item['total_tax_paid'] = "N/A"
                item['taxed_subtotal_paid'] = "N/A"
                item['total_paid'] = "N/A"
            item['container_number'] = line_item.inventory.container_number if line_item.inventory else 'None'

            list_results.append(item)

    list_results = sorted(list_results, key=lambda x: x['created'])

    return list_results
