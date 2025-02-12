# Pip imports
from psycopg2 import sql

# Internal imports
from src.schemas.reports import FilterObject


def get_bottom_10_states_delivery_efficiency(filters: FilterObject, psycopg2_connection=None):
    query = (
        sql.SQL(
            """
                        SELECT
                            oa.state AS state,
                            AVG(count_business_days(o.paid_at::DATE, o.delivered_at::DATE)) AS days
                        FROM
                            "order" o
                        INNER JOIN order_address oa ON o.address_id = oa.id
                        INNER JOIN line_item li on o.id = li.order_id
                        INNER JOIN container_inventory i on li.inventory_id = i.id
                        WHERE
                            o.created_at BETWEEN  {begin_date}
                                AND {end_date}
                            AND o.account_id={account_id}
                            AND o.delivered_at IS NOT NULL
                            AND o.paid_at IS NOT NULL AND count_business_days(o.paid_at::DATE, o.delivered_at::DATE) > 0
                        GROUP BY state
                        ORDER BY days DESC
                        LIMIT 10
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
