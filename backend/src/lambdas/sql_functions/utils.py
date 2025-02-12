# Pip imports
from psycopg2 import sql


SQL_REPORTS_PARAMS = {
    "container_sales": ["begin_date", "end_date", "account_id", "conditions", "productTypes"],
    "container_sales_by_condition": ["begin_date", "end_date", "account_id", "productTypes"],
    "container_sales_by_condition_percentages": ["begin_date", "end_date", "account_id", "productTypes"],
    "average_profit_per_container": ["begin_date", "end_date", "account_id"],
    "average_profit_per_container_city_location": ["begin_date", "end_date", "account_id"],
    "num_orders_per_month": ["begin_date", "end_date", "account_id", "states", "productTypes", "statuses"],
    "top_zip_codes": ["begin_date", "end_date", "account_id", "statuses"],
    "orders_by_payment_type": ["begin_date", "end_date", "account_id", "states", "productTypes"],
    "top_managers": [],
    "top_agents": ["begin_date", "end_date"],
    "top_10_states_delivery_efficiency": ["begin_date", "end_date", "account_id"],
    "top_10_warehouses_delivery_efficiency": ["begin_date", "end_date", "account_id"],
    "bottom_10_states_delivery_efficiency": ["begin_date", "end_date", "account_id"],
    "bottom_10_warehouses_delivery_efficiency": ["begin_date", "end_date", "account_id"],
    "financial_report": [],
    "fee_report": ["begin_date", "end_date"],
    "notes_rankings": ["begin_date", "end_date", "account_id"],
    "deposit_report": ["begin_date", "end_date", "account_id"],
}


def create_sql_composable(list_par, replace=False):
    if not replace:
        return sql.Composed([sql.SQL("("), sql.SQL(", ").join([sql.Literal(x) for x in list_par]), sql.SQL(")")])
    else:
        return sql.Composed(
            [sql.SQL("("), sql.SQL(", ").join([sql.Literal(x.replace("'", "''")) for x in list_par]), sql.SQL(")")]
        )
