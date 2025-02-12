# Pip imports
from psycopg2 import sql

# Internal imports
from src.schemas.reports import FilterObject


def get_financial_report(filters: FilterObject = None, psycopg2_connection=None):

    query = sql.SQL(
        """
            SELECT
                amount,
                    downpayment_fee,
                    late_fee,
                    rent_period_tax ,
                    order_tax ,
                    amount + downpayment_fee + late_fee + rent_period_tax + order_tax as total
            FROM (
            SELECT
                SUM(CASE
                    WHEN (type = 'PURCHASE' OR type = 'PURCHASE_ACCESSORY') AND ot.id is not NULL AND status = 'Paid' THEN COALESCE(total_price, 0.0)
                    WHEN type = 'RENT' AND rpt.id is not NULL THEN COALESCE(GREATEST(rp.amount_owed - tot.remaining_balance, 0.0), 0.0)
                    ELSE 0
                END) AS amount,
                SUM(CASE
                    WHEN rpf.fee_type = 'FIRST_PAYMENT' AND rpt.id is not NULL THEN fee_amount
                    ELSE 0
                END) AS downpayment_fee,
                SUM(CASE
                    WHEN rpf.fee_type = 'LATE' AND rpt.id is not NULL THEN fee_amount
                    ELSE 0
                END) AS late_fee,
                SUM(rpt.tax_amount) as rent_period_tax,
                SUM(ot.tax_amount) as order_tax
            FROM
                public.order o
            LEFT JOIN
                public.rent_period rp ON o.id = rp.order_id
            LEFT JOIN
                rent_period_total_balance tot ON rp.id = tot.rent_period_id
            LEFT JOIN
                rent_period_fee rpf ON rp.id = rpf.rent_period_id
            LEFT join
                rent_period_tax rpt ON rp.id = rpt.rent_period_id
            LEFT join
                order_tax ot on o.id = ot.order_id

            UNION ALL

            SELECT
                SUM(CASE
                    WHEN (type = 'PURCHASE' OR type = 'PURCHASE_ACCESSORY') AND ot.id is NULL AND status = 'Paid' THEN COALESCE(total_price, 0.0)
                    WHEN type = 'RENT' AND rpt.id is NULL THEN COALESCE(GREATEST(rp.amount_owed - tot.remaining_balance, 0.0), 0.0)
                    ELSE 0
                END) AS amount,
                SUM(CASE
                    WHEN rpf.fee_type = 'FIRST_PAYMENT' AND rpt.id is NULL  THEN fee_amount
                    ELSE 0
                END) AS downpayment_fee,
                SUM(CASE
                    WHEN rpf.fee_type = 'LATE' AND rpt.id is NULL  THEN fee_amount
                    ELSE 0
                END) AS late_fee,
                0 as rent_period_tax,
                0 as order_tax
            FROM
                public.order o
            LEFT JOIN
                public.rent_period rp ON o.id = rp.order_id
            LEFT JOIN
                rent_period_total_balance tot ON rp.id = tot.rent_period_id
            LEFT JOIN
                rent_period_fee rpf ON rp.id = rpf.rent_period_id
            LEFT join
                rent_period_tax rpt ON rp.id = rpt.rent_period_id
            LEFT join
                order_tax ot on o.id = ot.order_id) t
            """
    ).as_string(psycopg2_connection)

    return query
