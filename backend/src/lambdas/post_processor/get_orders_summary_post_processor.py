# Pip imports
from loguru import logger


def get_orders_summary_post_processor(data):
    total_taxable_orders_subtotal = 0
    total_tax_exempt_orders_subtotal = 0
    total_tax = 0
    total_paid_tax_exempt_orders = 0
    total_paid_taxable_orders = 0
    total_shipping_revenue = 0
    total_trucking_revenue = 0

    if data['purchase_type'] == "PURCHASE" or data['purchase_type'] == 'PURCHASE_ACCESSORY':
        order_ids = set()
        for transaction_type in data['transaction_types']:
            if transaction_type.order is None:
                continue

            if transaction_type.order.calculated_order_tax() > 0:
                if transaction_type.order.id not in order_ids:
                    total_taxable_orders_subtotal += transaction_type.order.calculated_sub_total_price()
                    total_tax += transaction_type.order.calculated_order_tax()
                    total_shipping_revenue += transaction_type.order.calculated_shipping_revenue_total()
                    container_price = sum([line_item.revenue or 0 for line_item in transaction_type.order.line_items])
                    if container_price == 0:
                        total_trucking_revenue += sum(
                            [line_item.shipping_revenue or 0 for line_item in transaction_type.order.line_items]
                        )
                    order_ids.add(transaction_type.order.id)

                total_paid_taxable_orders += transaction_type.amount
            else:
                if transaction_type.order.id not in order_ids:
                    total_tax_exempt_orders_subtotal += transaction_type.order.calculated_sub_total_price()
                    total_shipping_revenue += transaction_type.order.calculated_shipping_revenue_total()
                    order_ids.add(transaction_type.order.id)
                    container_price = sum([line_item.revenue or 0 for line_item in transaction_type.order.line_items])
                    if container_price == 0:
                        total_trucking_revenue += sum(
                            [line_item.shipping_revenue or 0 for line_item in transaction_type.order.line_items]
                        )
                total_paid_tax_exempt_orders += transaction_type.amount
    else:
        rent_period_ids = set()
        for transaction_type in data['transaction_types']:
            if transaction_type.rent_period is None:
                continue

            if transaction_type.rent_period.calculated_rent_period_tax() > 0:
                logger.info(f"transaction_type.rent_period.order.id: {transaction_type.rent_period.order.id}")
                if transaction_type.rent_period.id not in rent_period_ids:
                    total_taxable_orders_subtotal += transaction_type.rent_period.order.calculated_sub_total_price()
                    total_tax += transaction_type.rent_period.order.calculated_order_tax()
                    total_shipping_revenue += transaction_type.rent_period.order.calculated_shipping_revenue_total()
                    rent_period_ids.add(transaction_type.rent_period.order.id)

                total_paid_taxable_orders += transaction_type.amount
            else:
                if transaction_type.rent_period.order.id not in rent_period_ids:
                    total_tax_exempt_orders_subtotal += transaction_type.rent_period.order.calculated_sub_total_price()
                    total_shipping_revenue += transaction_type.rent_period.order.calculated_shipping_revenue_total()
                    rent_period_ids.add(transaction_type.rent_period.order.id)

                total_paid_tax_exempt_orders += transaction_type.amount

    return [
        {
            "total_taxable_orders_subtotal": total_taxable_orders_subtotal,
            "total_tax": total_tax,
            "total_tax_exempt_orders_subtotal": total_tax_exempt_orders_subtotal,
            "total_paid_taxable_orders": total_paid_taxable_orders,
            "total_paid_tax_exempt_orders": total_paid_tax_exempt_orders,
            "total_shipping_revenue": total_shipping_revenue,
            "total_trucking_revenue": total_trucking_revenue,
        }
    ]
