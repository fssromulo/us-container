# Pip imports
from psycopg2 import sql

# Internal imports
from src.schemas.reports import FilterObject


def get_fee_report(filters: FilterObject = None, psycopg2_connection=None):
    query = (
        sql.SQL(
            """
        SELECT SUM(fee.fee_amount) AS total,
        CASE
            WHEN fee_type.is_taxable = TRUE THEN 'TAXABLE'
            WHEN fee_type.is_taxable = FALSE THEN 'NON_TAXABLE'
            ELSE ''
        END AS type
        FROM fee
        RIGHT JOIN fee_type ON fee_type.id = fee.type_id
        WHERE fee.created_at BETWEEN {begin_date} AND {end_date}
        GROUP BY fee_type.is_taxable;
        """
        )
        .format(
            begin_date=sql.Literal(filters.begin_date),
            end_date=sql.Literal(filters.end_date),
        )
        .as_string(psycopg2_connection)
    )

    return query
