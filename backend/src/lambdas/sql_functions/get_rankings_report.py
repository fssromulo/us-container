# Pip imports
from loguru import logger
from psycopg2 import sql

# Internal imports
from src.lambdas.sql_functions.utils import create_sql_composable
from src.schemas.reports import FilterObject


def contains_all(main_list, sub_list):
    return all(item in main_list for item in sub_list)


def get_rankings_report(filters: FilterObject, psycopg2_connection=None):
    regular_order_sql_where_clause = sql.SQL("")
    rental_order_sql_where_clause = sql.SQL("")
    accessory_sql_where_clause = sql.SQL("")

    if 'ALL' in filters.purchase_types:
        regular_order_sql_where_clause = sql.SQL(
            """
            AND 1 = 1
        """
        )
        rental_order_sql_where_clause = sql.SQL(
            """
            AND 1 = 1
        """
        )
        accessory_sql_where_clause = sql.SQL(
            """
            1 = 1
        """
        )
    elif contains_all(filters.purchase_types, ["PURCHASE", "PURCHASE_ACCESSORY", "RENT_TO_OWN"]):
        regular_order_sql_where_clause = sql.SQL(
            """
            AND type in ('PURCHASE', 'PURCHASE_ACCESSORY', 'RENT_TO_OWN')
        """
        )

        if "RENT" in filters.purchase_types:
            rental_order_sql_where_clause = sql.SQL(
                """
                AND 1 = 1
            """
            )
        else:
            rental_order_sql_where_clause = sql.SQL(
                """
                AND 1 = 2
            """
            )

        if "ACCESSORIES" in filters.purchase_types:
            accessory_sql_where_clause = sql.SQL(
                """
                1 = 1
            """
            )
        else:
            accessory_sql_where_clause = sql.SQL(
                """
                (li.product_type != 'CONTAINER_ACCESSORY' OR li.product_type is null)
            """
            )
    elif 'PURCHASE' in filters.purchase_types:
        if 'RENT_TO_OWN' in filters.purchase_types:
            regular_order_sql_where_clause = sql.SQL(
                """
                AND type in ('PURCHASE', 'RENT_TO_OWN')
            """
            )
        else:
            regular_order_sql_where_clause = sql.SQL(
                """
                AND type in ('PURCHASE')
            """
            )

        if "RENT" in filters.purchase_types:
            rental_order_sql_where_clause = sql.SQL(
                """
                AND 1 = 1
            """
            )
        else:
            rental_order_sql_where_clause = sql.SQL(
                """
                AND 1 = 2
            """
            )

        if "ACCESSORIES" in filters.purchase_types:
            accessory_sql_where_clause = sql.SQL(
                """
                1 = 1
            """
            )
        else:
            accessory_sql_where_clause = sql.SQL(
                """
                (li.product_type != 'CONTAINER_ACCESSORY' OR li.product_type is null)
            """
            )
    elif 'PURCHASE_ACCESSORY' in filters.purchase_types:
        regular_order_sql_where_clause = sql.SQL(
            """
            AND type in ('PURCHASE_ACCESSORY')
        """
        )

        if "RENT" in filters.purchase_types:
            rental_order_sql_where_clause = sql.SQL(
                """
                AND 1 = 1
            """
            )
        else:
            rental_order_sql_where_clause = sql.SQL(
                """
                AND 1 = 2
            """
            )

        if "ACCESSORIES" in filters.purchase_types:
            accessory_sql_where_clause = sql.SQL(
                """
                1 = 1
            """
            )
        else:
            accessory_sql_where_clause = sql.SQL(
                """
                (li.product_type != 'CONTAINER_ACCESSORY' OR li.product_type is null)
            """
            )

    elif 'RENT_TO_OWN' in filters.purchase_types:
        regular_order_sql_where_clause = sql.SQL(
            """
            AND type in ('RENT_TO_OWN')
        """
        )

        if "RENT" in filters.purchase_types:
            rental_order_sql_where_clause = sql.SQL(
                """
                AND 1 = 1
            """
            )
        else:
            rental_order_sql_where_clause = sql.SQL(
                """
                AND 1 = 2
            """
            )

        if "ACCESSORIES" in filters.purchase_types:
            accessory_sql_where_clause = sql.SQL(
                """
                1 = 1
            """
            )
        else:
            accessory_sql_where_clause = sql.SQL(
                """
               (li.product_type != 'CONTAINER_ACCESSORY' OR li.product_type is null)
            """
            )
    elif "ACCESSORIES" in filters.purchase_types:
        regular_order_sql_where_clause = sql.SQL(
            """
            AND type in ('PURCHASE', 'PURCHASE_ACCESSORY')
        """
        )
        rental_order_sql_where_clause = sql.SQL(
            """
                AND 1 = 2
            """
        )
        accessory_sql_where_clause = sql.SQL(
            """
            li.product_type = 'CONTAINER_ACCESSORY'
        """
        )
    elif "RENT" in filters.purchase_types:
        regular_order_sql_where_clause = sql.SQL(
            """
            AND 1 = 2
        """
        )
        rental_order_sql_where_clause = sql.SQL(
            """
                AND 1 = 1
            """
        )
        accessory_sql_where_clause = sql.SQL(
            """
            (li.product_type != 'CONTAINER_ACCESSORY' OR li.product_type is null)
        """
        )

    if filters.can_read_all:
        if not filters.manager:
            query = (
                sql.SQL(
                    """
                        WITH rankings_orders AS (
                            SELECT
                                *
                            FROM
                                "order"
                            WHERE
                                ("account_id" = {account_id} OR "account_id" = {account_id})
                                AND "signed_at" >= {begin_date}::date
                                AND "signed_at" <= {end_date}::date + INTERVAL '1 day'
                                AND "status" IN ('Paid', 'Delivered', 'Completed', 'Pod', 'Delayed')
                                AND "is_archived" = false
                                {regular_order_sql_where_clause}
                            UNION ALL
                            SELECT
                                *
                            FROM
                                "order"
                            WHERE
                                ("account_id" = {account_id} OR "account_id" = {account_id})
                                AND "paid_at" >= {begin_date}::date
                                AND "paid_at" <= {end_date}::date + INTERVAL '1 day'
                                AND "status" IN ('Paid', 'Delivered', 'Completed', 'Partially Paid', 'Delayed')
                                AND "signed_at" IS NULL
                                AND "is_archived" = false
                                {regular_order_sql_where_clause}
                        ), subtotal_price_1 AS (
                            SELECT
                                ro.id,
                                ro.user_id,
                                SUM(COALESCE(li.revenue, 0) + COALESCE(li.shipping_revenue, 0)) AS subtotal_price,
                                COUNT(*) AS num_line_items
                            FROM
                                rankings_orders ro
                            JOIN
                                line_item li ON ro.id = li.order_id
                            WHERE
                                {accessory_sql_where_clause}
                            GROUP BY
                                ro.id, ro.user_id
                        ), subtotal_price_2 AS (
                            SELECT
                                ro.id,
                                ro.user_id,
                                SUM(COALESCE(f.fee_amount, 0)) AS subtotal_price
                            FROM
                                rankings_orders ro
                            LEFT JOIN
                                fee f ON f.order_id = ro.id
                            LEFT JOIN
                                fee_type ft ON f.type_id = ft.id
                            WHERE
                                ft.is_taxable = true or ft.is_taxable is null
                            GROUP BY
                                ro.id, ro.user_id
                        ), order_rent_period AS(
                            SELECT
                                o.id as order_id,
                                rp.id as rent_period_id,
                                o.user_id as user_id,
                            ROW_NUMBER() OVER (PARTITION BY o.id ORDER BY rp.start_date ASC) AS row_num
                            FROM public.order o
                            JOIN rent_period rp
                            ON
                                o.id=rp.order_id
                            WHERE type='RENT'
                            AND status not in ('Cancelled', 'Expired')
                            AND (account_id={account_id} or account_id={account_id})
                            {rental_order_sql_where_clause}
                            ), remaining_order_rent_period AS (SELECT
                                o.order_id,
                                o.user_id,
                                o.rent_period_id,
                                tb.remaining_balance,
                            ROW_NUMBER() OVER (PARTITION BY tb.rent_period_id ORDER BY tb.created_at ASC) AS row_num2
                            FROM order_rent_period o
                            JOIN transaction_type tt
                            ON tt.rent_period_id=o.rent_period_id
                            JOIN rent_period_total_balance tb
                            ON o.rent_period_id=tb.rent_period_id
                                WHERE row_num=1
                                AND tt.created_at BETWEEN {begin_date}::date and ({end_date}::date + INTERVAL '1 day')
                        ), final_order_rent_period AS (SELECT
                                o.order_id,
                                o.user_id,
                            o.remaining_balance as subtotal_price,
                            count(*) as num_units
                            FROM remaining_order_rent_period o
                            JOIN rent_period_total_balance tb
                            ON o.rent_period_id=tb.rent_period_id
                            JOIN line_item li
                            ON o.order_id=li.order_id
                                WHERE row_num2=1
                                AND tb.remaining_balance = 0
                            group by o.order_id, o.user_id, o.remaining_balance
                        )
                        SELECT
                            name,
                            sum(subtotal_price) as subtotal_price,
                            sum(num_units) as num_units
                        FROM
                        (SELECT
                            u.first_name || ' ' || u.last_name AS name,
                            SUM(sub1.subtotal_price + COALESCE(sub2.subtotal_price, 0)) AS subtotal_price,
                            SUM(sub1.num_line_items) AS num_units
                        FROM
                            subtotal_price_1 sub1
                        LEFT JOIN
                            subtotal_price_2 sub2 ON sub1.id = sub2.id
                        JOIN
                            users u ON sub1.user_id = u.id
                        GROUP BY
                            u.first_name || ' ' || u.last_name
                        UNION ALL
                        SELECT
                            u.first_name || ' ' || u.last_name AS name,
                            final_order_rent_period.subtotal_price,
                            final_order_rent_period.num_units
                        FROM
                            final_order_rent_period
                        JOIN
                            users u ON final_order_rent_period.user_id = u.id
                        ) unions
                        GROUP BY name
                        ORDER BY num_units desc

                        """
                )
                .format(
                    begin_date=sql.Literal(filters.begin_date),
                    end_date=sql.Literal(filters.end_date),
                    regular_order_sql_where_clause=regular_order_sql_where_clause,
                    rental_order_sql_where_clause=rental_order_sql_where_clause,
                    accessory_sql_where_clause=accessory_sql_where_clause,
                    account_id=sql.Literal(filters.account_id),
                )
                .as_string(psycopg2_connection)
            )
        else:
            query = (
                sql.SQL(
                    """
                       WITH rankings_orders AS (
                            SELECT *
                            FROM "order"
                            WHERE ("account_id" = {account_id} OR "account_id" = {account_id})
                                AND "signed_at" >= {begin_date}::date
                                AND "signed_at" <= {end_date}::date + INTERVAL '1 day'
                                AND "status" IN ('Paid', 'Delivered', 'Completed', 'Pod', 'Delayed')
                                AND "is_archived" = false
                                {regular_order_sql_where_clause}
                            UNION ALL
                            SELECT *
                            FROM "order"
                            WHERE ("account_id" = {account_id} OR "account_id" = {account_id})
                                AND "paid_at" >= {begin_date}::date
                                AND "paid_at" <= {end_date}::date + INTERVAL '1 day'
                                AND "status" IN ('Paid', 'Delivered', 'Completed', 'Partially Paid', 'Delayed')
                                AND "signed_at" IS NULL
                                AND "is_archived" = false
                                {regular_order_sql_where_clause}
                        ), subtotal_price_1 AS (
                            SELECT
                                ro.id,
                                ro.user_id,
                                SUM(COALESCE(li.revenue, 0) + COALESCE(li.shipping_revenue, 0)) AS subtotal_price,
                                COUNT(*) AS num_line_items
                            FROM rankings_orders ro
                            JOIN line_item li ON ro.id = li.order_id
                            WHERE {accessory_sql_where_clause}
                            GROUP BY ro.id, ro.user_id
                        ), subtotal_price_2 AS (
                            SELECT
                                ro.id,
                                ro.user_id,
                                SUM(COALESCE(f.fee_amount, 0)) AS subtotal_price
                            FROM rankings_orders ro
                            LEFT JOIN fee f ON f.order_id = ro.id
                            LEFT JOIN fee_type ft ON f.type_id = ft.id
                            WHERE ft.is_taxable = true OR ft.is_taxable IS NULL
                            GROUP BY ro.id, ro.user_id
                        ), order_rent_period AS (
                            SELECT
                                o.id as order_id,
                                rp.id as rent_period_id,
                                o.user_id as user_id,
                                ROW_NUMBER() OVER (PARTITION BY o.id ORDER BY rp.start_date ASC) AS row_num
                            FROM public.order o
                            JOIN rent_period rp ON o.id = rp.order_id
                            WHERE type = 'RENT' AND status not in ('Cancelled', 'Expired') AND (account_id = {account_id} or account_id={account_id})
                            {rental_order_sql_where_clause}
                        ), remaining_order_rent_period AS (
                            SELECT
                                o.order_id,
                                o.user_id,
                                o.rent_period_id,
                                tb.remaining_balance,
                                ROW_NUMBER() OVER (PARTITION BY tb.rent_period_id ORDER BY tt.created_at ASC) AS row_num2
                            FROM order_rent_period o
                            JOIN transaction_type tt ON tt.rent_period_id = o.rent_period_id
                            JOIN rent_period_total_balance tb ON o.rent_period_id = tb.rent_period_id
                            WHERE o.row_num = 1
                                AND tt.created_at BETWEEN {begin_date}::date AND ({end_date}::date + INTERVAL '1 day')
                        ), final_order_rent_period AS (
                            SELECT
                                o.order_id,
                                o.user_id,
                                o.remaining_balance as subtotal_price,
                                count(*) as num_units
                            FROM remaining_order_rent_period o
                            JOIN rent_period_total_balance tb ON o.rent_period_id = tb.rent_period_id
                            JOIN line_item li ON o.order_id = li.order_id
                            WHERE o.row_num2 = 1 AND tb.remaining_balance = 0
                            GROUP BY o.order_id, o.user_id, o.remaining_balance
                        ), managers AS (
                            SELECT
                                manager_id,
                                sum(subtotal_price) as subtotal_price,
                                sum(num_units) as num_units
                            FROM (
                                SELECT
                                    COALESCE(a.manager_id, sub1.user_id) as manager_id,
                                    SUM(sub1.subtotal_price + COALESCE(sub2.subtotal_price, 0)) AS subtotal_price,
                                    SUM(sub1.num_line_items) AS num_units
                                FROM subtotal_price_1 sub1
                                LEFT JOIN subtotal_price_2 sub2 ON sub1.id = sub2.id
                                LEFT JOIN assistant a ON a.assistant_id = sub1.user_id
                                GROUP BY sub1.user_id, a.manager_id
                                UNION ALL
                                SELECT
                                    COALESCE(a.manager_id, final_order_rent_period.user_id) as manager_id,
                                    SUM(final_order_rent_period.subtotal_price),
                                    SUM(final_order_rent_period.num_units)
                                FROM final_order_rent_period
                                LEFT JOIN assistant a ON a.assistant_id = final_order_rent_period.user_id
                                GROUP BY final_order_rent_period.user_id, a.manager_id
                            ) unions
                            GROUP BY manager_id
                        )
                        SELECT
                            u.first_name || ' ' || u.last_name AS name,
                            SUM(managers.subtotal_price) AS subtotal_price,
                            SUM(managers.num_units) AS num_units
                        FROM managers
                        JOIN users u ON managers.manager_id = u.id
                        GROUP BY u.first_name || ' ' || u.last_name
                        ORDER BY num_units DESC;
                        """
                )
                .format(
                    begin_date=sql.Literal(filters.begin_date),
                    end_date=sql.Literal(filters.end_date),
                    regular_order_sql_where_clause=regular_order_sql_where_clause,
                    rental_order_sql_where_clause=rental_order_sql_where_clause,
                    accessory_sql_where_clause=accessory_sql_where_clause,
                    account_id=sql.Literal(filters.account_id),
                )
                .as_string(psycopg2_connection)
            )
    else:
        if not filters.manager:
            query = (
                sql.SQL(
                    """
                        WITH rankings_orders AS (
                            SELECT
                                *
                            FROM
                                "order"
                            WHERE
                                ("account_id" = {account_id} OR "account_id" = {account_id})
                                AND "signed_at" >= {begin_date}::date
                                AND "signed_at" <= {end_date}::date + INTERVAL '1 day'
                                AND "status" IN ('Paid', 'Delivered', 'Completed', 'Pod', 'Delayed')
                                AND "is_archived" = false
                                {regular_order_sql_where_clause}
                            UNION ALL
                            SELECT
                                *
                            FROM
                                "order"
                            WHERE
                                ("account_id" = {account_id} OR "account_id" = {account_id})
                                AND "paid_at" >= {begin_date}::date
                                AND "paid_at" <= {end_date}::date + INTERVAL '1 day'
                                AND "status" IN ('Paid', 'Delivered', 'Completed', 'Partially Paid', 'Delayed')
                                AND "signed_at" IS NULL
                                AND "is_archived" = false
                                {regular_order_sql_where_clause}
                        ), subtotal_price_1 AS (
                            SELECT
                                ro.id,
                                ro.user_id,
                                SUM(COALESCE(li.revenue, 0) + COALESCE(li.shipping_revenue, 0)) AS subtotal_price,
                                COUNT(*) AS num_line_items
                            FROM
                                rankings_orders ro
                            JOIN
                                line_item li ON ro.id = li.order_id
                            WHERE
                               {accessory_sql_where_clause}
                            GROUP BY
                                ro.id, ro.user_id
                        ), subtotal_price_2 AS (
                            SELECT
                                ro.id,
                                ro.user_id,
                                SUM(COALESCE(f.fee_amount, 0)) AS subtotal_price
                            FROM
                                rankings_orders ro
                            LEFT JOIN
                                fee f ON f.order_id = ro.id
                            LEFT JOIN
                                fee_type ft ON f.type_id = ft.id
                            WHERE
                                ft.is_taxable = true or ft.is_taxable is null
                            GROUP BY
                                ro.id, ro.user_id
                        ), users_allowed AS(
                            SELECT a.assistant_id as user_id
                            FROM assistant a
                            WHERE
                                a.manager_id={user_id}
                            UNION ALL
                            SELECT {user_id}
                            UNION ALL
                            SELECT t.team_member_id as user_id
                            FROM team_member t
                            LEFT JOIN assistant a
                            ON
                            a.assistant_id=t.team_member_id
                            WHERE team_lead_id={user_id} AND a.assistant_id is NULL
                        ),  order_rent_period AS (
                            SELECT
                                o.id as order_id,
                                rp.id as rent_period_id,
                                o.user_id as user_id,
                                ROW_NUMBER() OVER (PARTITION BY o.id ORDER BY rp.start_date ASC) AS row_num
                            FROM public.order o
                            JOIN rent_period rp ON o.id = rp.order_id
                            WHERE type = 'RENT' AND status not in ('Cancelled', 'Expired') AND (account_id = {account_id} or account_id={account_id})
                            {rental_order_sql_where_clause}
                        ), remaining_order_rent_period AS (
                            SELECT
                                o.order_id,
                                o.user_id,
                                o.rent_period_id,
                                tb.remaining_balance,
                                ROW_NUMBER() OVER (PARTITION BY tb.rent_period_id ORDER BY tt.created_at ASC) AS row_num2
                            FROM order_rent_period o
                            JOIN transaction_type tt ON tt.rent_period_id = o.rent_period_id
                            JOIN rent_period_total_balance tb ON o.rent_period_id = tb.rent_period_id
                            WHERE o.row_num = 1
                                AND tt.created_at BETWEEN {begin_date}::date AND ({end_date}::date + INTERVAL '1 day')
                        ), final_order_rent_period AS (
                            SELECT
                                o.order_id,
                                o.user_id,
                                o.remaining_balance as subtotal_price,
                                count(*) as num_units
                            FROM remaining_order_rent_period o
                            JOIN rent_period_total_balance tb ON o.rent_period_id = tb.rent_period_id
                            JOIN line_item li ON o.order_id = li.order_id
                            WHERE o.row_num2 = 1 AND tb.remaining_balance = 0
                            GROUP BY o.order_id, o.user_id, o.remaining_balance
                        )
                        SELECT
                            name,
                            sum(subtotal_price) as subtotal_price,
                            sum(num_units) as num_units
                        FROM
                        (SELECT
                            u.first_name || ' ' || u.last_name AS name,
                            SUM(sub1.subtotal_price + COALESCE(sub2.subtotal_price, 0)) AS subtotal_price,
                            SUM(sub1.num_line_items) AS num_units
                        FROM
                            subtotal_price_1 sub1
                        LEFT JOIN
                            subtotal_price_2 sub2 ON sub1.id = sub2.id
                        JOIN
                            users u ON sub1.user_id = u.id
                        WHERE
                            u.id in (SELECT * FROM users_allowed)
                        GROUP BY
                            u.first_name || ' ' || u.last_name
                        UNION ALL
                        SELECT
                            u.first_name || ' ' || u.last_name AS name,
                            final_order_rent_period.subtotal_price,
                            final_order_rent_period.num_units
                        FROM
                            final_order_rent_period
                        JOIN
                            users u ON final_order_rent_period.user_id = u.id
                        WHERE
                            u.id in (SELECT * FROM users_allowed)
                        ) unions

                        GROUP BY name
                        ORDER BY num_units desc
                                """
                )
                .format(
                    begin_date=sql.Literal(filters.begin_date),
                    end_date=sql.Literal(filters.end_date),
                    user_id=sql.Literal(filters.user_id),
                    regular_order_sql_where_clause=regular_order_sql_where_clause,
                    rental_order_sql_where_clause=rental_order_sql_where_clause,
                    accessory_sql_where_clause=accessory_sql_where_clause,
                    account_id=sql.Literal(filters.account_id),
                )
                .as_string(psycopg2_connection)
            )
        else:
            query = (
                sql.SQL(
                    """
                        WITH rankings_orders AS (
                            SELECT
                                *
                            FROM
                                "order"
                            WHERE
                                ("account_id" = {account_id} OR "account_id" = {account_id})
                                AND "signed_at" >= {begin_date}::date
                                AND "signed_at" <= {end_date}::date + INTERVAL '1 day'
                                AND "status" IN ('Paid', 'Delivered', 'Completed', 'Pod', 'Delayed')
                                AND "is_archived" = false
                                {regular_order_sql_where_clause}
                            UNION ALL
                            SELECT
                                *
                            FROM
                                "order"
                            WHERE
                                ("account_id" = {account_id} OR "account_id" = {account_id})
                                AND "paid_at" >= {begin_date}::date
                                AND "paid_at" <= {end_date}::date + INTERVAL '1 day'
                                AND "status" IN ('Paid', 'Delivered', 'Completed', 'Partially Paid', 'Delayed')
                                AND "signed_at" IS NULL
                                AND "is_archived" = false
                                {regular_order_sql_where_clause}
                        ), subtotal_price_1 AS (
                            SELECT
                                ro.id,
                                ro.user_id,
                                SUM(COALESCE(li.revenue, 0) + COALESCE(li.shipping_revenue, 0)) AS subtotal_price,
                                COUNT(*) AS num_line_items
                            FROM
                                rankings_orders ro
                            JOIN
                                line_item li ON ro.id = li.order_id
                            WHERE
                                {accessory_sql_where_clause}
                            GROUP BY
                                ro.id, ro.user_id
                        ), subtotal_price_2 AS (
                            SELECT
                                ro.id,
                                ro.user_id,
                                SUM(COALESCE(f.fee_amount, 0)) AS subtotal_price
                            FROM
                                rankings_orders ro
                            LEFT JOIN
                                fee f ON f.order_id = ro.id
                            LEFT JOIN
                                fee_type ft ON f.type_id = ft.id
                            WHERE
                                ft.is_taxable = true or ft.is_taxable is null
                            GROUP BY
                                ro.id, ro.user_id
                        ), order_rent_period AS (
                            SELECT
                                o.id as order_id,
                                rp.id as rent_period_id,
                                o.user_id as user_id,
                                ROW_NUMBER() OVER (PARTITION BY o.id ORDER BY rp.start_date ASC) AS row_num
                            FROM public.order o
                            JOIN rent_period rp ON o.id = rp.order_id
                            WHERE type = 'RENT' AND status not in ('Cancelled', 'Expired') AND (account_id = {account_id} or account_id={account_id})
                            {rental_order_sql_where_clause}
                        ), remaining_order_rent_period AS (
                            SELECT
                                o.order_id,
                                o.user_id,
                                o.rent_period_id,
                                tb.remaining_balance,
                                ROW_NUMBER() OVER (PARTITION BY tb.rent_period_id ORDER BY tt.created_at ASC) AS row_num2
                            FROM order_rent_period o
                            JOIN transaction_type tt ON tt.rent_period_id = o.rent_period_id
                            JOIN rent_period_total_balance tb ON o.rent_period_id = tb.rent_period_id
                            WHERE o.row_num = 1
                                AND tt.created_at BETWEEN {begin_date}::date AND ({end_date}::date + INTERVAL '1 day')
                        ), final_order_rent_period AS (
                            SELECT
                                o.order_id,
                                o.user_id,
                                o.remaining_balance as subtotal_price,
                                count(*) as num_units
                            FROM remaining_order_rent_period o
                            JOIN rent_period_total_balance tb ON o.rent_period_id = tb.rent_period_id
                            JOIN line_item li ON o.order_id = li.order_id
                            WHERE o.row_num2 = 1 AND tb.remaining_balance = 0
                            GROUP BY o.order_id, o.user_id, o.remaining_balance
                        ),managers AS (
                            SELECT
                                manager_id,
                                sum(subtotal_price) as subtotal_price,
                                sum(num_units) as num_units
                            FROM (
                                SELECT
                                        a.manager_id as manager_id,
                                        SUM(sub1.subtotal_price + COALESCE(sub2.subtotal_price, 0)) AS subtotal_price,
                                        SUM(sub1.num_line_items) AS num_units
                                    FROM subtotal_price_1 sub1
                                    LEFT JOIN subtotal_price_2 sub2 ON sub1.id = sub2.id
                                    LEFT JOIN assistant a ON a.assistant_id = sub1.user_id
                                    WHERE a.manager_id is not null and a.manager_id={user_id}
                                    GROUP BY  a.manager_id
                                    UNION ALL
                                SELECT
                                        sub1.user_id as manager_id,
                                        SUM(sub1.subtotal_price + COALESCE(sub2.subtotal_price, 0)) AS subtotal_price,
                                        SUM(sub1.num_line_items) AS num_units
                                    FROM subtotal_price_1 sub1
                                    LEFT JOIN subtotal_price_2 sub2 ON sub1.id = sub2.id
                                    LEFT JOIN assistant a ON a.assistant_id = sub1.user_id
                                    Where a.assistant_id is null
                                    GROUP BY sub1.user_id
                                    UNION ALL
                                    SELECT
                                        COALESCE(a.manager_id, final_order_rent_period.user_id) as manager_id,
                                        SUM(final_order_rent_period.subtotal_price),
                                        SUM(final_order_rent_period.num_units)
                                    FROM final_order_rent_period
                                    LEFT JOIN assistant a ON a.assistant_id = final_order_rent_period.user_id
                                    GROUP BY final_order_rent_period.user_id, a.manager_id
                            ) unions
                            GROUP BY manager_id
                        ), users_allowed AS(
                            SELECT a.assistant_id as user_id
                            FROM assistant a
                            WHERE
                                a.manager_id={user_id}
                            UNION ALL
                            SELECT {user_id}
                            UNION ALL
                            SELECT t.team_member_id as user_id
                            FROM team_member t
                            LEFT JOIN assistant a
                            ON
                            a.assistant_id=t.team_member_id
                            WHERE team_lead_id={user_id} AND a.assistant_id is NULL
                        )
                        SELECT
                            u.first_name || ' ' || u.last_name AS name,
                            SUM(managers.subtotal_price) AS subtotal_price,
                            SUM(managers.num_units) AS num_units
                        FROM
                            managers
                        JOIN
                            users u ON managers.manager_id = u.id
                        WHERE u.id in (SELECT * FROM users_allowed)
                        GROUP BY
                            u.first_name || ' ' || u.last_name
                        ORDER BY num_units desc
                        """
                )
                .format(
                    begin_date=sql.Literal(filters.begin_date),
                    end_date=sql.Literal(filters.end_date),
                    user_id=sql.Literal(filters.user_id),
                    regular_order_sql_where_clause=regular_order_sql_where_clause,
                    rental_order_sql_where_clause=rental_order_sql_where_clause,
                    accessory_sql_where_clause=accessory_sql_where_clause,
                    account_id=sql.Literal(filters.account_id),
                )
                .as_string(psycopg2_connection)
            )
    logger.info(query)
    return query
