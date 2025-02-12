# Python imports
import copy


def get_credit_cards_post_processor_no_tax(data):
    line_item_list = []

    order_ids_set = set()
    order_total_paid_dict = {}
    for order_credit_card in data['order_credit_cards']:
        order = None
        if data['purchase_type'] == 'PURCHASE' or data['purchase_type'] == 'PURCHASE_ACCESSORY':
            order = order_credit_card.order
        else:
            pass

        if order is None:
            continue

        if order.id not in order_total_paid_dict:
            order_total_paid_dict[order.id] = [
                {
                    "amount": order_credit_card.response_from_gateway['payment_amount'],
                    "created_at": order_credit_card.created_at,
                }
            ]
        else:
            order_total_paid_dict[order.id].append(
                {
                    "amount": order_credit_card.response_from_gateway['payment_amount'],
                    "created_at": order_credit_card.created_at,
                }
            )

    for order_credit_card in data['order_credit_cards']:
        order = None
        if data['purchase_type'] == 'PURCHASE' or data['purchase_type'] == 'PURCHASE_ACCESSORY':
            order = order_credit_card.order
        else:
            pass

        if order is None:
            continue

        if order.id not in order_ids_set:
            order_ids_set.add(order.id)
        else:
            continue

        if (data['purchase_type'] == 'PURCHASE' or data['purchase_type'] == 'PURCHASE_ACCESSORY') and order.calculated_order_tax() == 0:
            for transaction in order_total_paid_dict[order.id]:
                customer_name = order.customer.full_name() if order.customer else None
                result = {
                    "order_id": str(order.display_order_id),
                    "created": str(transaction['created_at']),
                    "name": customer_name
                    if order.customer and (order.customer.first_name or order.customer.last_name)
                    else (order.customer.company_name if order.customer else None),
                    "total_paid": transaction['amount'],
                    "subtotal_paid": transaction['amount'],
                    "total_tax_paid": 0,
                    "calculated_remaining_order_balance": order.calculated_remaining_order_balance(),
                    "calculated_shipping_revenue_total": order.calculated_shipping_revenue_total(),
                    "calculated_order_tax": order.calculated_order_tax(),
                    "payment_type": order.payment_type,
                }

                first_line_item_set = False
                for line_item in order.line_items:

                    item = copy.copy(result)
                    if not first_line_item_set:
                        first_line_item_set = True
                    else:
                        item['total_paid'] = "N/A"
                        item['total_tax_paid'] = "N/A"
                        item['calculated_remaining_order_balance'] = "N/A"
                        item['calculated_shipping_revenue_total'] = "N/A"
                        item['calculated_order_tax'] = "N/A"
                        item['subtotal_paid'] = "N/A"
                    item['calculated_line_item_title'] = line_item.title()
                    item['container_number'] = line_item.inventory.container_number if line_item.inventory else 'None'
                    line_item_list.append(item)

    return line_item_list
