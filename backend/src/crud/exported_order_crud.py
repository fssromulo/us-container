# Python imports
import pytz
from datetime import datetime
from typing import Any, Dict, List, Optional, cast
from uuid import UUID

# Pip imports
from loguru import logger
from pydantic import BaseModel

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.orders.order import Order
from src.crud.partial_order_crud import get_by_status_type
from src.schemas.orders import ExportedOrderOut
from loguru import logger
from pydantic import BaseModel
from uuid import UUID

from ._types import PAGINATION



class ExportedOrderCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = ExportedOrderOut
        self.db_model = Order
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
        )

    async def get_by_status_type(
        self,
        account_id: int,
        status: str,
        order_type: str,
        user_ids: List[str],
        pagination: PAGINATION,
        get_all: bool = False,
    ) -> Dict[str, Any]:
        query, count = await get_by_status_type(self, account_id, status, order_type, user_ids, pagination)

        results = await self.schema.from_queryset(query)
        
        return {
            "orders": results,
            "count": count,
        }
    
    async def get_by_display_order_ids(self, account_id, displayOrderIds, user_ids):
        query = self.db_model.all().filter(account_id=account_id)

        if user_ids:
            query = query.filter(user_id__in=user_ids)

        if displayOrderIds:
            query = query.filter(display_order_id__in=displayOrderIds)

        results = await self.schema.from_queryset(query)
    
        return {
            "orders": results,
        }

exported_order_crud = ExportedOrderCRUD()
