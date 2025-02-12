# Pip imports
from psycopg2 import sql

# Internal imports
from src.lambdas.sql_functions.utils import create_sql_composable
from src.schemas.reports import FilterObject


def get_transactions_report(filters: FilterObject, psycopg2_connection=None):
    order_ids = create_sql_composable(filters.order_ids)

    
    query = (
            sql.SQL(
                """
                        SELECT
                            tt.id,
                            tt.created_at,
                            tt.payment_type,
                            tt.notes,
                            tt.amount,
                            tt.rent_period_id,
                            occ.response_from_gateway
                        FROM
                            transaction_type tt
                            JOIN rent_period rp ON
                                rp.id=tt.rent_period_id
                            LEFT JOIN order_credit_card occ ON
                                tt.credit_card_object_id=occ.id
                        WHERE
                            tt.created_at BETWEEN  {begin_date}
                                AND {end_date}
                            AND rp.order_id in {order_ids}
                            AND tt.account_id={account_id}
                            AND group_id is null
                        UNION ALL
                        SELECT DISTINCT ON (tt.group_id)
                            tt.id,
                            tt.created_at,
                            tt.payment_type,
                            tt.notes,
                            SUM(tt.amount) OVER (PARTITION BY tt.group_id) as total_amount,
                            tt.rent_period_id,
                            occ.response_from_gateway
                        FROM
                            transaction_type tt
                            JOIN rent_period rp ON
                                rp.id=tt.rent_period_id
                            LEFT JOIN order_credit_card occ ON
                                tt.credit_card_object_id=occ.id
                        WHERE
                            tt.created_at BETWEEN  {begin_date}
                                AND {end_date}
                            AND rp.order_id in {order_ids}
                            AND tt.account_id={account_id}
                            AND group_id is not null
                        """
            )
            .format(
                begin_date=sql.Literal(filters.begin_date),
                end_date=sql.Literal(filters.end_date),
                account_id=sql.Literal(filters.account_id),
                order_ids=order_ids
            )
            .as_string(psycopg2_connection)
            )
    return query