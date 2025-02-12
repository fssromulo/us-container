
def generate_processing_cost_options(account, order):
    flat_rates_enabled = account.cms_attributes.get("processing_costs", {}).get("flat_rates_enabled", False)
    percentage_rates_enabled = account.cms_attributes.get("processing_costs", {}).get("percentage_rates_enabled", False)

    processing_flat_cost = 0
    processing_percentage_cost = 0
    charge_per_line_item = False
    if flat_rates_enabled:
        flat_rates = account.cms_attributes.get("processing_costs", {}).get("flat", {})
        if order.type == 'RENT':
            processing_flat_cost = flat_rates.get("rent", 0)
        elif order.type == 'RENT_TO_OWN':
            processing_flat_cost = flat_rates.get("rent_to_own", 0)
        elif order.type == 'PURCHASE' or order.type == 'PURCHASE_ACCESSORY':
            processing_flat_cost = flat_rates.get("purchase", 0)
        charge_per_line_item = flat_rates.get("charge_per_line_item", False)

    if percentage_rates_enabled:
        percentage_rates = account.cms_attributes.get("processing_costs", {}).get("rates", {})
        if order.type == 'RENT':
            processing_percentage_cost = percentage_rates.get("rent", 0)
        elif order.type == 'RENT_TO_OWN':
            processing_percentage_cost = percentage_rates.get("rent_to_own", 0)
        elif order.type == 'PURCHASE' or order.type == 'PURCHASE_ACCESSORY':
            processing_percentage_cost = percentage_rates.get("purchase", 0)
        charge_per_line_item = percentage_rates.get("charge_per_line_item", False)

    return flat_rates_enabled, percentage_rates_enabled, processing_flat_cost, processing_percentage_cost, charge_per_line_item
