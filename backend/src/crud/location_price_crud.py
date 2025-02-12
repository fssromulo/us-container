# Python imports
from typing import List

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.pricing.location_price import LocationPrice
from src.schemas.location_price import LocationPriceIn, LocationPriceOut


class LocationPriceCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = LocationPriceOut
        self.create_schema = LocationPriceIn
        self.update_schema = LocationPriceIn
        self.db_model = LocationPrice
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=50)

    async def get_by_city(self, city_name: str, account_id: int) -> Model:
        model = await self.db_model.filter(city__iexact=city_name, account_id=account_id).first()
        if model:
            return await self.schema.from_tortoise_orm(model)

        raise NOT_FOUND

    async def get_city_region_map(self, account_id: int) -> dict:
        result = await self.get_all(account_id=account_id)
        city_region_map = {}
        for location in result:
            if location.region not in city_region_map:
                city_region_map[location.region] = [location.city]
            else:
                city_region_map[location.region].append(location.city)
        return city_region_map

    async def get_city_pickup_region_map(self, account_id: int) -> dict:
        result = await self.get_all(account_id=account_id)
        city_pickup_region_map = {}
        for location in result:
            if location.pickup_region not in city_pickup_region_map:
                city_pickup_region_map[location.pickup_region] = [location.city]
            else:
                city_pickup_region_map[location.pickup_region].append(location.city)
        return city_pickup_region_map


location_price_crud = LocationPriceCRUD()
