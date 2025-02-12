# Python imports
from decimal import Decimal


def average_profit_per_container_post_processor(data):
    states = {}

    for item in data:
        if len(item.line_items) == 0 or not item.line_items[0].inventory:
            continue

        if item.line_items[0].inventory.depot.state not in states:
            try:
                states[item.line_items[0].inventory.depot.state] = {
                    "sum": item.calculated_profit() / Decimal(len(item.line_items)),
                    "count": Decimal(1),
                }
            except:
                pass
        else:
            try:
                states[item.line_items[0].inventory.depot.state] = {
                    "sum": states[item.line_items[0].inventory.depot.state]['sum']
                    + Decimal(item.calculated_profit()) / Decimal(len(item.line_items)),
                    "count": states[item.line_items[0].inventory.depot.state]['count'] + Decimal(1),
                }
            except:
                pass

    result = []
    for state in states:
        result.append({"state": state, "profit": states[state]['sum'] / states[state]['count']})
    return result
