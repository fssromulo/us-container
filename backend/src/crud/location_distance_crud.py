# Python imports
from typing import List

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.location_distance import LocationDistances
from src.schemas.location_distances import LocationDistancesIn, LocationDistancesOut


class LocationDistanceCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = LocationDistancesOut
        self.create_schema = LocationDistancesIn
        self.update_schema = LocationDistancesIn
        self.db_model = LocationDistances
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=50)

    async def get_by_origin_zip(self, origin_zip: str) -> Model:
        query = self.db_model.filter(origin_zip=origin_zip)
        return await self.schema.from_queryset(query)

    async def get_by_destination_zip(self, zip: str) -> Model:
        model = await self.db_model.get(destination_zip=zip)
        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            raise NOT_FOUND

    async def delete_by_destination_zip(self, zip: str) -> Model:
        await self.db_model.get(destination_zip=zip).delete()

    async def get_zips_in(self, zips: List[int]) -> List[Model]:
        query = self.db_model.filter(destination_zip__in=zips)
        return await self.schema.from_queryset(query)


location_distance_crud = LocationDistanceCRUD()
