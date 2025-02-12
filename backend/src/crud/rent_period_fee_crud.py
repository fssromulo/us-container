# ...
from typing import List
from tortoise.models import Model

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.rent_period_fee import RentPeriodFee
from src.schemas.rent_period_fee import RentPeriodFeeIn, RentPeriodFeeOut



class RentPeriodFeeCrud(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = RentPeriodFeeOut
        self.create_schema = RentPeriodFeeIn
        self.update_schema = RentPeriodFeeIn
        self.db_model = RentPeriodFee
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=50,
        )

    async def delete_all_by_rent_period_ids(
        self,
        rent_period_ids: List[str],
    ) -> None:
        res = await self.db_model.filter(rent_period_id__in=rent_period_ids).delete()
        return res
    async def delete_all_by_rent_period_ids_fee_type(
        self,
        rent_period_ids: List[str],
        fee_type_id: str,
    ) -> None:
        res = await self.db_model.filter(rent_period_id__in=rent_period_ids, type_id=fee_type_id).delete()
        return res


    async def get_all_by_rent_period_id(
        self,
        rent_period_id: str,
    ) -> None:
        return await self.db_model.filter(rent_period_id=rent_period_id).all()
    async def get_all_by_rent_period_id_fee_type(self, rent_period_id, fee_type_id)-> None:
        return await self.db_model.filter(rent_period_id=rent_period_id, type_id=fee_type_id).all()

rent_period_fee_crud = RentPeriodFeeCrud()
