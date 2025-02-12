# Pip imports
from psycopg2 import sql

# Internal imports
from src.schemas.reports import FilterObject


def get_deposit_report_by_day(filters: FilterObject = None, psycopg2_connection=None):
    query = (
        sql.SQL(
            """
            SELECT
                DATE_TRUNC('day', created_at)::VARCHAR AS day,
                SUM(CASE WHEN payment_type = 'CC' THEN sum_transactions ELSE 0 END) AS CC,
                SUM(CASE WHEN payment_type = 'Cash' THEN sum_transactions ELSE 0 END) AS Cash,
                SUM(CASE WHEN payment_type = 'Check' THEN sum_transactions ELSE 0 END) AS Check,
                SUM(CASE WHEN payment_type = 'Wire' THEN sum_transactions ELSE 0 END) AS Wire,
                SUM(CASE WHEN payment_type = 'Echeck' THEN sum_transactions ELSE 0 END) AS Echeck,
                SUM(CASE WHEN payment_type = 'RTO' THEN sum_transactions ELSE 0 END) AS RTO,
                SUM(CASE WHEN payment_type = 'Zelle' THEN sum_transactions ELSE 0 END) AS Zelle
            FROM
            (SELECT
                tt.payment_type,
                tt.created_at,
                CAST(amount AS numeric) AS sum_transactions
                FROM
                transaction_type AS tt
                JOIN public.order o
                ON tt.order_id = o.id
                WHERE
                tt.payment_type <> 'CC' AND tt.account_id = {account_id}
                AND tt.created_at BETWEEN  {begin_date} AND {end_date}
                AND o.type = {purchase_type}

                -- Union Operator
                UNION

                -- Query for Credit Card Transactions
                SELECT
                'CC' AS payment_type,
                a.created_at,
                COALESCE(CAST(response_from_gateway->>'payment_amount' AS numeric), 0.0) +
                COALESCE(CAST(response_from_gateway->>'auth_amount' AS numeric), 0.0)
                 AS sum_transactions
                FROM
                order_credit_card as a
                JOIN public.order o
                ON a.order_id = o.id
                WHERE
                a.created_at BETWEEN {begin_date} AND {end_date}
                AND o.account_id = {account_id}
                AND o.type = {purchase_type}) AS combined_data
                GROUP BY day
                ORDER BY DAY;
            """
        )
        .format(
            begin_date=sql.Literal(filters.begin_date),
            end_date=sql.Literal(filters.end_date),
            account_id=sql.Literal(filters.account_id),
            purchase_type=sql.Literal(filters.purchase_type),
        )
        .as_string(psycopg2_connection)
    )

    return query
