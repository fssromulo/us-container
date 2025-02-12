# Pip imports
from pydantic import Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.quote_searches import QuoteSearches


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


QuoteSearchesIn = pydantic_model_creator(
    QuoteSearches,
    name="QuoteSearchesIn",
    exclude=("id", "created_at", "modified_at"),
    exclude_readonly=True,
    # config_class=Config,
)

QuoteSearchesOut = pydantic_model_creator(QuoteSearches, name="QuoteSearchesOut", exclude_readonly=True)
