# Python imports
import ast
import asyncio
import hashlib
import json
import re
import traceback
import uuid
from datetime import datetime
from decimal import Decimal
from typing import List

# Pip imports
from loguru import logger

# Internal imports
from src.database.tortoise_init import init_models


init_models()  # noqa: F402

# Pip imports
import psycopg2  # noqa: E402
from tortoise import Tortoise  # noqa: E402

# Internal imports
from src.config import settings  # noqa: E402
from src.crud.order_card_info_crud import order_credit_card_crud  # noqa: E402
from src.crud.order_crud import order_crud  # noqa: E402
from src.crud.reports_crud import reports_crud  # noqa: E402
from src.database.config import TORTOISE_ORM  # noqa: E402
from src.database.models.orders.order import Order  # noqa: E402
from src.lambdas.post_processor.average_profit_per_container import (  # noqa: E402
    average_profit_per_container_post_processor,
)
from src.lambdas.post_processor.average_profit_per_container_city_location import (  # noqa: E402
    average_profit_per_container_city_location_post_processor,
)
from src.lambdas.post_processor.get_credit_cards_post_processor_no_tax import (  # noqa: E402
    get_credit_cards_post_processor_no_tax,
)
from src.lambdas.post_processor.get_credit_cards_post_processor_taxable import (  # noqa: E402
    get_credit_cards_post_processor_taxable,
)
from src.lambdas.post_processor.get_orders_no_tax_post_processor import get_orders_no_tax_post_processor  # noqa: E402
from src.lambdas.post_processor.get_orders_rentals_post_processor import get_orders_rentals_post_processor  # noqa: E402
from src.lambdas.post_processor.get_orders_summary_post_processor import get_orders_summary_post_processor  # noqa: E402
from src.lambdas.post_processor.get_orders_taxable_post_processor import get_orders_taxable_post_processor  # noqa: E402
from src.lambdas.post_processor.get_receipt_items_report_post_processor import (  # noqa: E402
    get_receipt_items_report_post_processor,
)
from src.lambdas.sql_functions.average_profit_per_container import get_average_profit_per_container  # noqa: E402
from src.lambdas.sql_functions.average_profit_per_container_city_location import (  # noqa: E402
    get_average_profit_per_container_city_location,
)
from src.lambdas.sql_functions.bottom_10_states_delivery_efficiency import (  # noqa: E402
    get_bottom_10_states_delivery_efficiency,
)
from src.lambdas.sql_functions.bottom_10_warehouses_delivery_efficiency import (  # noqa: E402; noqa: E402
    get_bottom_10_warehouses_delivery_efficiency,
)
from src.lambdas.sql_functions.commissions_accessories_report import (
    get_commissions_accessories_report,
    get_commissions_individual_accessories_report,
)
from src.lambdas.sql_functions.commissions_agents_closed_report import get_commissions_agents_closed_report
from src.lambdas.sql_functions.commissions_agents_report import get_commissions_agents_report
from src.lambdas.sql_functions.commissions_closed_individual_report import (
    get_commissions_closed_agents_individual_report,
    get_commissions_closed_individual_report,
)
from src.lambdas.sql_functions.commissions_closed_report import get_commissions_closed_report
from src.lambdas.sql_functions.commissions_individual_report import (
    get_commissions_agents_individual_report,
    get_commissions_individual_report,
)
from src.lambdas.sql_functions.commissions_report import get_commissions_report, get_commissions_report_full
from src.lambdas.sql_functions.container_sales import get_container_sales  # noqa: E402
from src.lambdas.sql_functions.container_sales_by_condition import get_container_sales_by_condition  # noqa: E402
from src.lambdas.sql_functions.container_sales_by_condition_percentages import (  # noqa: E402
    get_container_sales_by_condition_percentages,
)
from src.lambdas.sql_functions.deposit_report import get_deposit_report  # noqa: E402
from src.lambdas.sql_functions.deposit_report_by_day import get_deposit_report_by_day  # noqa: E402
from src.lambdas.sql_functions.fee_report import get_fee_report  # noqa: E402
from src.lambdas.sql_functions.financial_report import get_financial_report  # noqa: E402
from src.lambdas.sql_functions.get_credit_cards_summary import get_credit_cards_summary  # noqa: E402
from src.lambdas.sql_functions.get_rankings_report import get_rankings_report  # noqa: E402
from src.lambdas.sql_functions.num_orders_per_month import get_num_orders_per_month  # noqa: E402
from src.lambdas.sql_functions.orders_by_payment_type import get_orders_by_payment_type  # noqa: E402
from src.lambdas.sql_functions.orders_summary import get_orders_summary  # noqa: E402
from src.lambdas.sql_functions.orders_summary_rentals import get_orders_summary_rentals  # noqa: E402
from src.lambdas.sql_functions.team_commissions_report import (  # noqa: E402
    get_commissions_team_individual_report,
    get_team_commissions_report,
)
from src.lambdas.sql_functions.top_10_states_delivery_efficiency import (  # noqa: E402
    get_top_10_states_delivery_efficiency,
)
from src.lambdas.sql_functions.top_10_warehouses_delivery_efficiency import (  # noqa: E402
    get_top_10_warehouses_delivery_efficiency,
)
from src.lambdas.sql_functions.top_agents import get_top_agents  # noqa: E402
from src.lambdas.sql_functions.top_managers import get_top_managers  # noqa: E402
from src.lambdas.sql_functions.top_zip_codes import get_top_zip_codes  # noqa: E402
from src.lambdas.sql_functions.top_zip_codes_table import get_top_zip_codes_table  # noqa: E402
from src.lambdas.sql_functions.transactions import get_transactions_report  # noqa: E402
from src.lambdas.sql_functions.users_without_sales import get_users_without_sales  # noqa: E402
from src.lambdas.sql_functions.vendor_inventory import get_inventory_report  # noqa: E402
from src.schemas.reports import FilterObject  # noqa: E402
from src.schemas.reports import ReportsIn, ReportsInUpdate  # noqa: E402


# sys.path.append("..")


# enable schemas to read relationship between models
# flakes8: noqa


def create_psycopg2_connection():
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASS,
            host=settings.DB_HOST,
            port=settings.DB_PORT,
        )

        # Return the connection object
        return connection

    except (Exception, psycopg2.Error) as error:
        logger.error(f"Error while connecting to PostgreSQL: {error}")
        return None


KEYS_ORDER = [
    "query",
    "run_by",
    "begin_date",
    "end_date",
    "account_id",
    "conditions",
    "productTypes",
    "states",
    "statuses",
    "role_id",
    "purchase_type",
]

SQL_REPORTS = {
    "financial_report": (get_financial_report, False),
    "fee_report": (get_fee_report, False),
    "deposit_report": (get_deposit_report, False),
    "container_sales": (get_container_sales, False),
    "container_sales_by_condition": (get_container_sales_by_condition, False),
    "container_sales_by_condition_percentages": (get_container_sales_by_condition_percentages, False),
    "average_profit_per_container": (get_average_profit_per_container, True),
    "average_profit_per_container_city_location": (get_average_profit_per_container_city_location, True),
    "num_orders_per_month": (get_num_orders_per_month, False),
    "top_zip_codes": (get_top_zip_codes, False),
    "top_zip_codes_table": (get_top_zip_codes_table, False),
    "orders_by_payment_type": (get_orders_by_payment_type, False),
    "top_managers": (get_top_managers, False),
    "top_agents": (get_top_agents, False),
    "top_10_states_delivery_efficiency": (get_top_10_states_delivery_efficiency, False),
    "top_10_warehouses_delivery_efficiency": (get_top_10_warehouses_delivery_efficiency, False),
    "bottom_10_states_delivery_efficiency": (get_bottom_10_states_delivery_efficiency, False),
    "bottom_10_warehouses_delivery_efficiency": (get_bottom_10_warehouses_delivery_efficiency, False),
    "financial_report_summary": (get_orders_summary, True),
    "financial_report_no_tax": (get_orders_summary, True),
    "financial_report_taxable": (get_orders_summary, True),
    "financial_report_rentals": (get_orders_summary_rentals, True),
    "deposit_report_by_day": (get_deposit_report_by_day, False),
    "financial_report_credit_card_not_tax": (get_credit_cards_summary, True),
    "financial_report_credit_card_taxable": (get_credit_cards_summary, True),
    "users_without_sales": (get_users_without_sales, False),
    "vendor_inventory": (get_inventory_report, False),
    "transactions_report": (get_transactions_report, False),
    "rankings": (get_rankings_report, False),
    "receipt_items_report": (get_orders_summary_rentals, True),
    "commissions_report": (get_commissions_report, False),
    "commissions_individual_report": (get_commissions_individual_report, False),
    "commissions_team_individual_report": (get_commissions_team_individual_report, False),
    "team_commissions_report": (get_team_commissions_report, False),
    "commissions_agents_individual_report": (get_commissions_agents_individual_report, False),
    "commissions_agents_report": (get_commissions_agents_report, False),
    "commissions_closed_report": (get_commissions_closed_report, False),
    "commissions_closed_individual_report": (get_commissions_closed_individual_report, False),
    "commissions_closed_agents_individual_report": (get_commissions_closed_agents_individual_report, False),
    "commissions_agents_closed_report": (get_commissions_agents_closed_report, False),
    "commissions_accessories_report": (get_commissions_accessories_report, False),
    "commissions_individual_accessories_report": (get_commissions_individual_accessories_report, False),
    "commissions_report_full": (get_commissions_report_full, False),
}

POST_PROCESSORS = {
    "average_profit_per_container": average_profit_per_container_post_processor,
    "average_profit_per_container_city_location": average_profit_per_container_city_location_post_processor,
    "financial_report_summary": get_orders_summary_post_processor,
    "financial_report_no_tax": get_orders_no_tax_post_processor,
    "financial_report_taxable": get_orders_taxable_post_processor,
    "financial_report_credit_card_not_tax": get_credit_cards_post_processor_no_tax,
    "financial_report_credit_card_taxable": get_credit_cards_post_processor_taxable,
    "financial_report_rentals": get_orders_rentals_post_processor,
    "receipt_items_report": get_receipt_items_report_post_processor,
}


def build_filter(args):
    # change all to .get
    filter = FilterObject(
        begin_date=args['begin_date'],
        end_date=parse_date_to_end_of_day(args['end_date']),
        conditions=ast.literal_eval(args['conditions']) if args.get('conditions') else None,
        productTypes=ast.literal_eval(args['productTypes']) if args.get('productTypes') else None,
        statuses=ast.literal_eval(args['statuses']) if args.get('statuses') else None,
        states=ast.literal_eval(args['states']) if args.get('states') else None,
        account_id=args.get('account_id'),
        role_id=args.get('role_id'),
        purchase_type=args.get('purchase_type'),
        vendors=ast.literal_eval(args['vendors']) if args.get('vendors') else None,
        order_ids=ast.literal_eval(args['order_ids']) if args.get('order_ids') else None,
        manager=ast.literal_eval(args['manager']) if args.get('manager') else None,
        can_read_all=ast.literal_eval(args['can_read_all']) if args.get('can_read_all') else None,
        user_id=args.get('user_id'),
        purchase_types=ast.literal_eval(args['purchase_types']) if args.get('purchase_types') else None,
    )

    return filter


def datetime_to_string(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def convert_datetime_in_dict(data):
    if isinstance(data, dict):
        return {k: convert_datetime_in_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_datetime_in_dict(v) for v in data]
    else:
        return datetime_to_string(data)


def parse_date_to_end_of_day(date_str):
    # Try to parse with milliseconds; fallback to no milliseconds if that fails
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        except Exception as e:
            try:
                date_obj = datetime.strptime(date_str, "%m/%d/%y")
            except Exception as e:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                except Exception as e:
                    return None
    # Set the time to end of day
    end_of_day = date_obj.replace(hour=23, minute=59, second=59, microsecond=999000)  # Set to .999 for milliseconds
    end_of_day_str = end_of_day.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return end_of_day_str


def convert_uuid_in_dict(data):
    if isinstance(data, dict):
        return {k: convert_uuid_in_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_uuid_in_dict(v) for v in data]
    elif isinstance(data, uuid.UUID):
        return str(data)
    else:
        return data


def replace_decimal_with_float(d):
    if isinstance(d, dict):
        return {k: replace_decimal_with_float(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [replace_decimal_with_float(k) for k in d]
    elif isinstance(d, Decimal):
        return float(d)
    else:
        return d


async def sales_report(obj):
    orders_ids_total_ammounts = {}
    date_format = '%Y-%m-%dT%H:%M:%SZ'

    res = await order_credit_card_crud.get_all_between_dates(
        int(obj['account_id']),
        datetime.strptime(obj['begin_date'], date_format),
        datetime.strptime(parse_date_to_end_of_day(obj['end_date']), date_format),
    )

    for order_credit_card in res:
        if order_credit_card.order_id not in orders_ids_total_ammounts:
            orders_ids_total_ammounts[order_credit_card.order_id] = float(
                order_credit_card.response_from_gateway.get('payment_amount', 0)
            )
        else:
            orders_ids_total_ammounts[order_credit_card.order_id] += float(
                order_credit_card.response_from_gateway.get('payment_amount', 0)
            )

    sales_orders_zero_tax = []
    sales_orders_greater_zero = []

    orders: List[Order] = await order_crud.get_by_ids(
        obj['account_id'], [str(x) for x in orders_ids_total_ammounts.keys()]
    )
    for order in orders:

        if order.type == "RENT":
            continue

        result = {
            "order_id": str(order.id),
            "created_at": str(order.created_at),
            "paid_at": str(order.paid_at),
            "Customer Name": order.customer.full_name if order.customer else None,
            "Calculated Line Items Title": order.calculated_line_items_title,
            "Phone": order.customer.phone if order.customer else None,
            "Agent": "",
            "Email": order.customer.email if order.customer else None,
            "Total paid": orders_ids_total_ammounts[order.id],
            "Calculated Profit": "",
            "Calculated Sub Total Price": order.calculated_sub_total_price,
            "Calculated Remaining Order Balance": order.calculated_remaining_order_balance,
            "Calculated Fees": order.calculated_fees,
            "Calculated Shipping Revenue Total": order.calculated_shipping_revenue_total,
            "Calculated Order Tax": order.calculated_order_tax,
            "Calculated Fees Without Bank Fee": order.calculated_fees_without_bank_fee,
            "Payment Type": order.payment_type,
        }

        for key, value in result.items():
            if isinstance(value, Decimal):
                result[key] = str(value)

        if order.calculated_order_tax == 0:
            sales_orders_zero_tax.append(result)
        else:
            sales_orders_greater_zero.append(result)

    return {"sales_orders_zero_tax": sales_orders_zero_tax, "sales_orders_greater_zero": sales_orders_greater_zero}


async def run_function(connection, name, args_object):
    if name == "sales_report":
        filtered_result = await sales_report(args_object)
    else:
        sql_report, useTortoise = SQL_REPORTS[name]
        if callable(sql_report) and not useTortoise:
            psycopg2_connection = create_psycopg2_connection()
            filters = build_filter(args_object)
            sql_report = sql_report(filters, psycopg2_connection)
        else:
            filters = build_filter(args_object)
            sql_report = await sql_report(filters)

        result = sql_report
        if not useTortoise:
            result = await connection.execute_query_dict(sql_report)

        if name in POST_PROCESSORS:
            result = POST_PROCESSORS[name](result)

        filtered_result = []
        for item in result:
            item = replace_decimal_with_float(item)
            item = convert_datetime_in_dict(item)
            item = convert_uuid_in_dict(item)
            filtered_result.append(item)
    return filtered_result


async def update_record(connection, result, account_id, id):
    await reports_crud.update(account_id, id, ReportsInUpdate(status="COMPLETED", result=result, account_id=account_id))


async def delete_record_with_hash(hash_str):
    await reports_crud.delete_by_hash(hash_str)


async def insert_record_running(connection, obj, hash_str, name):
    obj_clone = obj.copy()
    obj_clone['name'] = name
    obj_clone['run_at'] = str(datetime.now())
    obj_clone['query_hash'] = hash_str
    obj_clone['status'] = 'RUNNING'
    res = await reports_crud.create(ReportsIn(**obj_clone))
    return res.id


async def check_hash_in_the_reports_table(hash_str, connection, date):
    sql_query = (
        f"SELECT FROM public.reports where query_hash='{hash_str}' AND DATE(run_at) = '{date}' AND status='COMPLETED'"
    )
    result = await connection.execute_query(sql_query)
    return result[0] != 0


def parse_url(message):
    obj = {}
    args = message.split("?")
    obj['query'] = args[0]

    items = args[1].split('&')
    for item in items:
        args = item.split("=")
        key = args[0]
        value = args[1]
        obj[key] = value

    return obj


def clean_run_by(run_by):
    return re.sub(r'[^a-zA-Z0-9]', '', run_by)


def compute_hash(obj):
    hash_str = ""
    for key in KEYS_ORDER:
        if key == 'run_by':
            hash_str += str(clean_run_by(obj['run_by']))
            continue
        if key in obj and obj[key] is not None:
            hash_str += str(obj[key])
    md5_hash = hashlib.md5(hash_str.encode('utf-8'))
    return md5_hash.hexdigest()


def handler(event, context):
    result = asyncio.run(async_handler(event, context))

    return {'statusCode': 200, 'body': result}


async def async_handler(event, context):
    try:
        await Tortoise.init(config=TORTOISE_ORM)

        connection = Tortoise.get_connection('default')
        # im getting length of 0 on records
        # so I will check the length of records first
        records = event.get('Records', [])
        if len(records) == 0:
            logger.error("No records found")
            return
        else:
            message = records[0]['body']

        obj = json.loads(message)

        if obj == "warming":
            logger.info("Warming, wait for the next message")
            return

        # Assuming compute_hash is a custom function
        message_hash = compute_hash(obj)
        logger.info(f"Message hash: {message_hash}")

        await delete_record_with_hash(message_hash)

        # Assuming insert_record_running, run_function, and update_record are custom functions
        report_id = await insert_record_running(connection, obj, message_hash, obj.get('query', ''))

        result = await run_function(connection, obj.get('query', ''), obj)
        await update_record(connection, result, obj.get('account_id', ''), report_id)

    except Exception as e:
        # Handle exceptions appropriately (log, re-raise, etc.)
        logger.error(f"Error processing message: {str(e)}")
        logger.error(f"Error traceback: {traceback.format_exc()}")
        # logger.error(f"results: {result}")

    finally:
        # Close the database connection if needed
        await Tortoise.close_connections()
