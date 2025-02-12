# Python imports
from decimal import Decimal


def get_receipt_items_report_post_processor(data):
    list_of_transactions = []
    list_of_items = []
    for tt in data['transaction_types']:
        list_of_transactions.append(
            {
                "amount": tt.amount,
                "created_at": tt.created_at,
                "type": "transaction_type",
                "id": tt.id,
                "order": tt.rent_period.order,
                "payment_type": tt.payment_type
                if tt.credit_card_object is None
                else tt.credit_card_object.response_from_gateway['transactionResponse']['accountType'],
            }
        )

    for tt in list_of_transactions:
        order = tt['order']
        if order is None:
            continue

        description_list = []
        for line_item in order.line_items:
            # We are unable to fetch the customer delivery address
            # directly in the line items from the order so would
            # have to check if the line item address is empty
            # then we use the order level address
            description = line_item.calc_abrev_title_w_container_number_w_address()
            if (line_item.container_address() == ""):
                address = order.address
                description += f"{description} | {address.full_address()}"
            description_list.append(description)

        unit_detail_str = ",".join(description_list)

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
        for rent_period_id in balances:
            rent_period_balance_amount = Decimal(0)
            for rent_period_balance in balances[rent_period_id]:
                if rent_period_balance is None:
                    continue
                prev_balance = crt_balance
                crt_balance = rent_period_balance

                if not prev_balance or not crt_balance:
                    continue

                if tt['type'] == 'transaction_type':
                    if rent_period_balance.transaction_type and rent_period_balance.transaction_type.id == tt['id']:
                        rent_period_balance_amount += Decimal(prev_balance.remaining_balance) - Decimal(
                            crt_balance.remaining_balance
                        )

            list_of_items.append(
                {
                    "transaction_id": tt['id'],
                    "created_at": balances[rent_period_id][0].rent_period.created_at,
                    "order": order.display_order_id,
                    "unit": unit_detail_str,
                    "description": "Rent balance "
                    + balances[rent_period_id][0].rent_period.start_date.strftime("%m/%d/%y")
                    + " - "
                    + balances[rent_period_id][0].rent_period.end_date.strftime("%m/%d/%y"),
                    "amount": rent_period_balance_amount,
                    "tax": 0,
                    "taxed": balances[rent_period_id][0].rent_period.calculated_rent_period_tax > 0,
                    "payment_type": tt['payment_type'],
                }
            )

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

        for rent_period_id in balances:
            fees_found = {}
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
                            if rent_period_fee.type.name in ['LATE', 'CREDIT_CARD']:
                                if rent_period_fee.id not in fees_found:
                                    fees_found[rent_period_fee.id] = {
                                        "fee_type": rent_period_fee.type.display_name,
                                        "created_at": rent_period_fee.created_at,
                                        "amount": rent_period_fee.fee_amount,
                                        "taxed": False,
                                    }
                                else:
                                    fees_found[rent_period_fee.id] = {
                                        "fee_type": rent_period_fee.type.display_name,
                                        "created_at": rent_period_fee.created_at,
                                        "amount": fees_found[rent_period_fee.id]['amount'] + rent_period_fee.fee_amount,
                                        "taxed": False,
                                    }
                            else:
                                if (
                                    rent_period_fee.type.name is None
                                    and rent_period_balance.rent_period.calculated_rent_period_tax == 0
                                ):
                                    if rent_period_fee.id not in fees_found:
                                        fees_found[rent_period_fee.id] = {
                                            "fee_type": rent_period_fee.type.display_name,
                                            "created_at": rent_period_fee.created_at,
                                            "amount": rent_period_fee.fee_amount,
                                            "taxed": False,
                                        }
                                    else:
                                        fees_found[rent_period_fee.id] = {
                                            "fee_type": rent_period_fee.type.display_name,
                                            "created_at": rent_period_fee.created_at,
                                            "amount": fees_found[rent_period_fee.id]['amount']
                                            + rent_period_fee.fee_amount,
                                            "taxed": False,
                                        }
                                else:
                                    if rent_period_fee.id not in fees_found:
                                        fees_found[rent_period_fee.id] = {
                                            "fee_type": rent_period_fee.type.display_name,
                                            "created_at": rent_period_fee.created_at,
                                            "amount": rent_period_fee.fee_amount,
                                            "taxed": True,
                                        }
                                    else:
                                        fees_found[rent_period_fee.id] = {
                                            "fee_type": rent_period_fee.type.display_name,
                                            "created_at": rent_period_fee.created_at,
                                            "amount": fees_found[rent_period_fee.id]['amount']
                                            + rent_period_fee.fee_amount,
                                            "taxed": True,
                                        }

            for _, fee in fees_found.items():
                list_of_items.append(
                    {
                        "transaction_id": tt['id'],
                        "created_at": fee['created_at'],
                        "order": order.display_order_id,
                        "unit": unit_detail_str,
                        "description": fee['fee_type'],
                        "amount": fee['amount'],
                        "tax": 0,
                        "taxed": fee['taxed'],
                        "payment_type": tt['payment_type'],
                    }
                )

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

        sum_of_amounts = Decimal(0)
        for item in list_of_items:
            if item['taxed'] is True and item['transaction_id'] == tt['id']:
                sum_of_amounts += Decimal(item['amount'])

        for item in list_of_items:
            if sum_of_amounts != 0 and item['transaction_id'] == tt['id'] and item['taxed'] is True:
                item['tax'] = Decimal(item['amount']) / sum_of_amounts * Decimal(tax_sum_amount)

    list_of_items = list(filter(lambda x: x['amount'] != 0, list_of_items))
    return list_of_items
