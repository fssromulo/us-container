# Python imports
from decimal import Decimal


def average_profit_per_container_city_location_post_processor(data):
    states = {}

    for item in data:
        if len(item.line_items) == 0 or not item.line_items[0].inventory:
            continue
        key = item.line_items[0].inventory.depot.city + " " + item.line_items[0].inventory.depot.state
        if key not in states:
            try:
                states[key] = {"sum": item.calculated_profit() / Decimal(len(item.line_items)), "count": Decimal(1)}
            except:
                pass
        else:
            try:
                states[key] = {
                    "sum": states[key]['sum'] + Decimal(item.calculated_profit()) / Decimal(len(item.line_items)),
                    "count": states[key]['count'] + Decimal(1),
                }
            except:
                pass

    result = []
    for state in states:
        result.append({"state": state, "profit": states[state]['sum'] / states[state]['count']})
    result = sorted(result, key=lambda x: -x['profit'])
    return result[:100]
