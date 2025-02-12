# Python imports
import copy
from decimal import Decimal

# Pip imports
from loguru import logger
from tortoise.queryset import QuerySet


def get_orders_rentals_post_processor(data):
    list_results = []
    intermediate_results = []
    list_of_transactions = []
    for tt in data['transaction_types']:
        list_of_transactions.append(
            {
                "amount": tt.amount,
                "created_at": tt.transaction_effective_date,
                "type": "transaction_type",
                "id": tt.id,
                "order": tt.rent_period.order,
                "payment_type": tt.payment_type,
                "group_id": tt.group_id,
            }
        )

    for tt in list_of_transactions:
        order = tt['order']
        if order is None:
            continue

        # Taxed subtotal
        transaction_rent_period_balances = sorted(data['rent_period_balances'], key=lambda x: x.created_at)
        transaction_rent_period_balances = [
            x for x in transaction_rent_period_balances if x.rent_period.order_id == order.id
        ]

        balances = {}
        for trpb in transaction_rent_period_balances:
            if trpb.rent_period.id not in balances:
                balances[trpb.rent_period.id] = [trpb]
            else:
                balances[trpb.rent_period.id].append(trpb)

        prev_balance = None
        crt_balance = None
        taxed_subtotal_sum_amount = Decimal(0)
        for rent_period_id in balances:
            if balances[rent_period_id][0].rent_period.calculated_rent_period_tax > 0:
                for rent_period_balance in balances[rent_period_id]:
                    if rent_period_balance is None:
                        continue
                    prev_balance = crt_balance
                    crt_balance = rent_period_balance

                    if not prev_balance or not crt_balance:
                        continue

                    if tt['type'] == 'transaction_type':
                        if rent_period_balance.transaction_type and rent_period_balance.transaction_type.id == tt['id']:
                            taxed_subtotal_sum_amount += Decimal(prev_balance.remaining_balance) - Decimal(
                                crt_balance.remaining_balance
                            )

        # Not Taxed subtotal
        transaction_rent_period_balances = sorted(data['rent_period_balances'], key=lambda x: x.created_at)
        transaction_rent_period_balances = [
            x for x in transaction_rent_period_balances if x.rent_period.order_id == order.id
        ]

        balances = {}
        for trpb in transaction_rent_period_balances:
            if trpb.rent_period.id not in balances:
                balances[trpb.rent_period.id] = [trpb]
            else:
                balances[trpb.rent_period.id].append(trpb)

        prev_balance = None
        crt_balance = None
        tax_exempt_subtotal_sum_amount = Decimal(0)
        for rent_period_id in balances:
            if balances[rent_period_id][0].rent_period.calculated_rent_period_tax == 0:
                for rent_period_balance in balances[rent_period_id]:
                    if rent_period_balance is None:
                        continue
                    prev_balance = crt_balance
                    crt_balance = rent_period_balance

                    if not prev_balance or not crt_balance:
                        continue

                    if tt['type'] == 'transaction_type':
                        if rent_period_balance.transaction_type and rent_period_balance.transaction_type.id == tt['id']:
                            tax_exempt_subtotal_sum_amount += Decimal(prev_balance.remaining_balance) - Decimal(
                                crt_balance.remaining_balance
                            )

        #  Tax
        transaction_rent_period_tax_balances = sorted(data['rent_period_tax_balances'], key=lambda x: x.created_at)
        transaction_rent_period_tax_balances = [
            x for x in transaction_rent_period_tax_balances if x.rent_period.order_id == order.id
        ]

        balances = {}
        for trpb in transaction_rent_period_tax_balances:
            if trpb.rent_period.id not in balances:
                balances[trpb.rent_period.id] = [trpb]
            else:
                balances[trpb.rent_period.id].append(trpb)

        prev_balance = None
        crt_balance = None
        tax_sum_amount = 0
        for rent_period_id in balances:
            for rent_period_balance in balances[rent_period_id]:
                if rent_period_balance is None:
                    continue
                prev_balance = crt_balance
                crt_balance = rent_period_balance

                if not prev_balance or not crt_balance:
                    continue

                if tt['type'] == 'transaction_type':
                    if rent_period_balance.transaction_type and rent_period_balance.transaction_type.id == tt['id']:
                        tax_sum_amount += prev_balance.balance - crt_balance.balance

        # Fee
        transaction_rent_period_fee_balances = sorted(data['rent_period_fee_balances'], key=lambda x: x.created_at)
        transaction_rent_period_fee_balances = [
            x for x in transaction_rent_period_fee_balances if x.rent_period.order_id == order.id
        ]

        balances = {}
        for trpb in transaction_rent_period_fee_balances:
            if trpb.rent_period.id not in balances:
                balances[trpb.rent_period.id] = [trpb]
            else:
                balances[trpb.rent_period.id].append(trpb)

        prev_balance = None
        crt_balance = None
        fee_sum_amount = Decimal(0)
        sum_non_taxable_fees = Decimal(0)
        sum_taxable_fees = Decimal(0)

        for rent_period_id in balances:
            for rent_period_balance in balances[rent_period_id]:
                if rent_period_balance is None:
                    continue
                prev_balance = crt_balance
                crt_balance = rent_period_balance

                if not prev_balance or not crt_balance:
                    continue

                if tt['type'] == 'transaction_type':
                    if rent_period_balance.transaction_type and rent_period_balance.transaction_type.id == tt['id']:
                        fee_sum_amount += Decimal(prev_balance.remaining_balance) - Decimal(
                            crt_balance.remaining_balance
                        )

                        rent_period_fees = rent_period_balance.rent_period.rent_period_fees
                        for rent_period_fee in rent_period_fees:
                            if not rent_period_fee.type.is_taxable:
                                sum_non_taxable_fees += rent_period_fee.fee_amount
                            else:
                                sum_taxable_fees += rent_period_fee.fee_amount

        if sum_taxable_fees + sum_non_taxable_fees == 0:
            pass
        else:
            tax_exempt_subtotal_sum_amount += (
                sum_non_taxable_fees / (sum_taxable_fees + sum_non_taxable_fees) * fee_sum_amount
            )
            taxed_subtotal_sum_amount += sum_taxable_fees / (sum_taxable_fees + sum_non_taxable_fees) * fee_sum_amount

        customer_name = ""
        if hasattr(order, 'customer') and order.customer:
            customer_name = (
                order.customer.company_name
                if order.customer.company_name
                else order.customer.first_name + " " + order.customer.last_name
            )

        if hasattr(order, 'single_customer') and order.single_customer:
            single_customer = order.single_customer
            customer_name = ""
            # Use isinstance() rather than type() for a typecheck.
            if isinstance(order.single_customer, QuerySet):
                # loop through the queryset and get the customer name
                for customer in order.single_customer:
                    logger.info(f"customer: {customer}")
                    customer_name = (
                        customer.company_name
                        if customer.company_name
                        else customer.first_name + " " + customer.last_name
                    )
            else:
                logger.info(f"single_customer not a queryset: {single_customer}")
                customer_name = (
                    single_customer.company_name
                    if single_customer.company_name
                    else single_customer.first_name + " " + single_customer.last_name
                )

        result = {
            "transaction_id": tt['id'],
            "order_id": order.display_order_id,
            "order": order,
            "group_id": tt['group_id'],
            "created": str(tt['created_at']),
            "name": customer_name,
            "taxed_subtotal_paid": taxed_subtotal_sum_amount,
            "total_tax_paid": tax_sum_amount,
            "tax_exempt_subtotal_paid": tax_exempt_subtotal_sum_amount,
            "payment_type": tt['payment_type'],
            "container_number": "",
            "total_paid": taxed_subtotal_sum_amount + tax_sum_amount + tax_exempt_subtotal_sum_amount,
        }
        intermediate_results.append(result)

    # Now merge results based on group_id
    grouped_results = {}
    for result in intermediate_results:
        group_id = result['group_id']
        if not group_id:  # If no group_id, treat as individual transaction
            list_results.append(result)
            continue

        if group_id not in grouped_results:
            # Create new group entry
            grouped_results[group_id] = copy.deepcopy(result)
            grouped_results[group_id]['transaction_id'] = result['transaction_id']
            grouped_results[group_id]['order_ids'] = result['order_id']
            grouped_results[group_id]['order_list'] = {result['order_id'] : result['order']}
        else:
            if result['order_id'] not in grouped_results[group_id]['order_ids']:
                grouped_results[group_id]['order_ids'] += "," + result['order_id'] 
                grouped_results[group_id]['order_list'][result['order_id']] = result['order']

            # Merge numeric values for the first line item
            if result['total_paid'] != "N/A":
                grouped_results[group_id]['taxed_subtotal_paid'] += result['taxed_subtotal_paid']
                grouped_results[group_id]['total_tax_paid'] += result['total_tax_paid']
                grouped_results[group_id]['tax_exempt_subtotal_paid'] += result['tax_exempt_subtotal_paid']
                grouped_results[group_id]['total_paid'] += result['total_paid']

    # Add all grouped results (first line items) to the final list
    for group_id, result in grouped_results.items():
        first_line_item_set = False
        for line_item in result['order'].line_items:

            item = copy.deepcopy(result)
            
            if not first_line_item_set:
                first_line_item_set = True
            else:
                item['total_paid'] = "N/A"
                item['tax_exempt_subtotal_paid'] = "N/A"
                item['total_tax_paid'] = "N/A"
                item['taxed_subtotal_paid'] = "N/A"
                item['total_paid'] = "N/A"
            item['container_number'] = line_item.inventory.container_number if line_item.inventory else 'None'

            del item['order']
            del item['order_list']
            list_results.append(item)

        #Add the other orders line items if present in grouped transaction
        if "," in result['order_ids']:
            order_ids = result['order_ids'].split(",")

            for order_id_item in order_ids:
                if order_id_item != item['order_id']:
                    first_line_item_set = False

                    for line_item in result['order_list'][order_id_item].line_items:

                        new_item = copy.deepcopy(result)
                        new_item['order_id'] = order_id_item
                        new_item['total_paid'] = "N/A"
                        new_item['tax_exempt_subtotal_paid'] = "N/A"
                        new_item['total_tax_paid'] = "N/A"
                        new_item['taxed_subtotal_paid'] = "N/A"
                        new_item['total_paid'] = "N/A"
                        new_item['container_number'] = line_item.inventory.container_number if line_item.inventory else 'None'

                        del new_item['order']
                        del new_item['order_list']
                        list_results.append(new_item)

    list_results = sorted(list_results, key=lambda x: x['created'])

    return list_results
