# Python imports
from typing import List

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.fixed_location_price import FixedLocationPrice
from src.schemas.fixed_location_price import FixedLocationPriceInSchema, FixedLocationPriceOutSchema


class FixedLocationPriceCrud(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = FixedLocationPriceOutSchema
        self.create_schema = FixedLocationPriceInSchema
        self.update_schema = FixedLocationPriceInSchema
        self.db_model = FixedLocationPrice
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=50,
        )

    async def get_by_postal_code(self, postal_code: str) -> Model:
        query = self.db_model.filter(postal_code=postal_code)
        return await self.schema.from_queryset(query)


fixed_location_price_crud = FixedLocationPriceCrud()
