# Pip imports
from psycopg2 import sql

# Internal imports
from src.lambdas.sql_functions.utils import create_sql_composable
from src.schemas.reports import FilterObject


def get_users_without_sales(filters: FilterObject = None, psycopg2_connection=None):
    query = (
        sql.SQL(
            """
                with users_with_sales as (
                    SELECT user_id
                    FROM "order"
                    WHERE paid_at BETWEEN {begin_date} AND {end_date}
                    UNION
                    SELECT user_id
                    FROM "order"
                    WHERE signed_at BETWEEN {begin_date} AND {end_date}
                    AND type <> 'RENT' 
                )
                SELECT
                    id,
                    first_name,
                    last_name,
                    email,
                    TO_CHAR(created_at, 'MM/DD/YY') AS formatted_created_at,
                    EXTRACT(DAY FROM CURRENT_DATE - created_at) AS days_as_use
                FROM users u1
                left join users_with_sales u2
                on u1.id=u2.user_id
                WHERE 
                    is_active = true
                    AND account_id = {account_id}
                    AND LOWER(first_name) != 'test' and u2.user_id is null
            """
        )
        .format(
            begin_date=sql.Literal(filters.begin_date),
            end_date=sql.Literal(filters.end_date),
            account_id=sql.Literal(filters.account_id),
        )
        .as_string(psycopg2_connection)
    )
    return query
