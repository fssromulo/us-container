# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.logistics_zones import LogisticsZones
from src.schemas.logistics_zones import LogisticsZonesInSchema, LogisticsZonesOutSchema


class LogisticsZonesCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = LogisticsZonesOutSchema
        self.create_schema = LogisticsZonesInSchema
        self.update_schema = LogisticsZonesInSchema
        self.db_model = LogisticsZones
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=50,
        )

logistics_zones_crud = LogisticsZonesCRUD()