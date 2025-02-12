# Python imports
from http.client import NOT_FOUND

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.pricing.location_price import LocationPrice
from src.schemas.container_locations import LocationPriceInSchema, LocationPriceOutSchema


location_crud = TortoiseCRUD(
    schema=LocationPriceOutSchema,
    create_schema=LocationPriceInSchema,
    update_schema=LocationPriceInSchema,
    db_model=LocationPrice,
)


class LocationCrud(TortoiseCRUD):
    def __init__(self) -> None:
        self.schema = LocationPriceOutSchema
        self.create_schema = LocationPriceInSchema
        self.update_schema = LocationPriceInSchema
        self.db_model = LocationPrice
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=50)

    async def get_by_city(self, city_name: str) -> Model:
        model = await self.db_model.filter(city__iexact=city_name).first()
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


location_crud = LocationCrud()
