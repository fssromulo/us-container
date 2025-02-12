# Pip imports
from psycopg2 import sql

# Internal imports
from src.schemas.reports import FilterObject


def get_notes_rankings_report(filters: FilterObject = None, psycopg2_connection=None):
    query = (
        sql.SQL(
            """
         SELECT u.id AS user_id, COUNT(n.id) AS note_count
                FROM "users" u
                JOIN notes n ON u.id = n.author_id
                WHERE u.account_id = {account_id}
                AND n.created_at BETWEEN {start_date} AND {end_date}
                GROUP BY u.id
        """
        )
        .format(
            account_id=sql.Literal(filters.account_id),
            begin_date=sql.Literal(filters.begin_date),
            end_date=sql.Literal(filters.end_date),
        )
        .as_string(psycopg2_connection)
    )

    return query
