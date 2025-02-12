from dataclasses import dataclass
from typing import List, Dict, Any
from decimal import Decimal
from datetime import datetime
from src.utils.number_formatter import fc
from src.utils.date_formatter import dfc

@dataclass
class Column:
    field: str
    header: str
    visible: bool

def compute_dynamic_columns(state: Dict[str, Any]) -> List[Column]:
    # Determine visibility of Delivery From and Delivery To based on drop_off_pickup, drop_off, and pick_up
    show_delivery_columns = any(
        field in state['visibleColumns']
        for field in ['drop_off_pickup', 'drop_off', 'pick_up']
    )

    return [
        Column(field='shipping_container', header='Shipping Container', visible=True),
        Column(field='delivery_from', header='Delivery From', visible=show_delivery_columns),
        Column(field='delivery_to', header='Delivery To', visible=show_delivery_columns),
        Column(
            field='drop_off_pickup',
            header='Drop Off / Pickup',
            visible=state['show_combined'] and 'drop_off_pickup' in state['visibleColumns'],
        ),
        Column(
            field='drop_off',
            header='Drop Off',
            visible=not state['show_combined'] and 'drop_off' in state['visibleColumns'],
        ),
        Column(
            field='pick_up',
            header='Pickup',
            visible=not state['show_combined'] and 'pick_up' in state['visibleColumns'],
        ),
        Column(
            field='late_fees',
            header=state.get('late_fee_header', 'Late Fees'),
            visible=bool(state.get('late_fee_header')) and 'late_fees' in state['visibleColumns'],
        ),
        Column(field='monthly_rent', header='Monthly Rent', visible='monthly_rent' in state['visibleColumns']),
        Column(field='tax', header='Tax', visible='tax' in state['visibleColumns']),
        Column(field='total', header='Total', visible='total' in state['visibleColumns']),
    ]

def process_table_data(data: List[Dict[str, Any]], state: Dict[str, Any], columns: List[Column]) -> List[Dict[str, Any]]:
    line_items = []

    for el in data:
        row_data = {}

        # Update visibleColumns based on data values
        for column in columns:
            value = el.get(column.field, None)
            if value is not None and (isinstance(value, (int, float, Decimal)) and value > 0 or not isinstance(value, (int, float, Decimal))):
                if column.field not in state['visibleColumns']:
                    state['visibleColumns'].append(column.field)

        # Ensure visibility updates affect this row
        visibleColumns = compute_dynamic_columns(state)
        visibleColumns = [col for col in visibleColumns if col.visible]  # Filter visible columns

        for idx, column in enumerate(visibleColumns):
            value = el.get(column.field, None)
            if value is not None:
                if isinstance(value, (int, float, Decimal)):
                    row_data[f'item_{idx}'] = fc(value)
                else:
                    row_data[f'item_{idx}'] = value

        line_items.append(row_data)

    return line_items

def get_visible_columns_and_data(state: Dict[str, Any], data: List[Dict[str, Any]]):
    columns = compute_dynamic_columns(state)
    process_table_data(data, state, columns)
    columns = compute_dynamic_columns(state)
    columns = [col for col in columns if col.visible]  # Filter visible columns
    column_titles = [{
        f'title_{idx}': col.header
        for idx, col in enumerate(columns)
    }]
    column_titles_fields = [{
        f'title_{idx}': { 'header':col.header, 'field': col.field }
        for idx, col in enumerate(columns)
    }]
    table_data = process_table_data(data, state, columns)

    return column_titles, table_data, column_titles_fields

def filter_subtotals(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filters and returns fields where the value is greater than zero.
    """
    return [
    {**item, "value": fc(item['value'])}
    for item in data
    if isinstance(item['value'], (int, float, Decimal)) and item['value'] > 0
    ]

def last_payment_date(selected_rent_period):
    latest_date = max(
        (obj.transaction_effective_date for obj in selected_rent_period.transaction_type_rent_period),
    )
    return latest_date.strftime('%b %d, %Y')

def rent_period_dates(order, selected_rent_period):
    prefix = "Quoted" if order.get("attributes", "").get("is_quote_title", False) else "Invoiced"
    return f"{prefix} for {selected_rent_period.calculated_rent_period_display_dates}"

def selected_rent_period_number(order, selected_rent_period_id):
    sorted_rent_periods = sorted(order['rent_periods'], key=lambda x: x['start_date'])
    index = next((i for i, rent_period in enumerate(sorted_rent_periods) if str(rent_period['id']) == selected_rent_period_id), -1)
    return str(index + 1) if index != -1 else ""

