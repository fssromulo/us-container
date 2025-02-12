# Python imports
from datetime import datetime

# Pip imports
from tortoise.expressions import Q

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.order_comission import OrderCommision
from src.schemas.order_commission import OrderCommissionIn, OrderCommissionOut


order_commission_crud = TortoiseCRUD(
    schema=OrderCommissionOut,
    create_schema=OrderCommissionIn,
    update_schema=OrderCommissionIn,
    db_model=OrderCommision,
)


class OrderCommissionCrud(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = OrderCommissionOut
        self.create_schema = OrderCommissionIn
        self.update_schema = OrderCommissionIn
        self.db_model = OrderCommision
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
        )

    async def delete_period(self, account_id: int, start_date, end_date, is_team) -> bool:
        delivered_filter = Q(account_id=account_id, delivered_at__gte=start_date, delivered_at__lte=end_date)
        completed_filter = Q(
            account_id=account_id, delivered_at__isnull=True, completed_at__gte=start_date, completed_at__lte=end_date
        )
        combined_qs = self.db_model.filter(completed_filter | delivered_filter)

        combined_qs = combined_qs.filter(is_team_commission=is_team)
        await combined_qs.delete()
        return True

    async def upgrading_agent_to_manager(self, user_id: int) -> bool:
        await self.db_model.filter(agent_id=user_id).update(can_see_profit=False)

    async def get_period(self, account_id: int, start_date, end_date, is_team, user_ids=None, user_id=None) -> bool:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%m/%d/%y")
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%m/%d/%y")

        #  set the time to midnight for start date
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        # set the time to 11:59:59 for end date
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=0)

        delivered_filter = Q(account_id=account_id, delivered_at__gte=start_date, delivered_at__lte=end_date)
        completed_filter = Q(
            account_id=account_id, delivered_at__isnull=True, completed_at__gte=start_date, completed_at__lte=end_date
        )

        combined_qs = self.db_model.filter(completed_filter | delivered_filter)

        if user_ids:
            if is_team:
                combined_qs = combined_qs.filter(team_lead_id__in=user_ids)
            else:
                combined_qs = combined_qs.filter(Q(agent_id=user_id) | Q(managing_agent_id=user_id))

        combined_qs = combined_qs.filter(is_team_commission=is_team)

        return await self.schema.from_queryset(combined_qs)


order_commission_crud = OrderCommissionCrud()
