
# ...

from src.schemas.quote_searches import (
    QuoteSearchesIn,
    QuoteSearchesOut,
)

from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.quote_searches import QuoteSearches

quote_searches_crud = TortoiseCRUD(
    schema=QuoteSearchesOut,
    create_schema=QuoteSearchesIn,
    update_schema=QuoteSearchesIn,
    db_model=QuoteSearches,
)
