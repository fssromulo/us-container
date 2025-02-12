# Python imports
import logging

# Pip imports
from tortoise.expressions import Q

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.customer.old_customer import Customer
from src.schemas.customer_simple import CustomerProfileIn, CustomerProfileOut


class CustomerSimpleCRUD(TortoiseCRUD):
    def __init__(self) -> None:
        self.db_model = Customer
        self.schema = CustomerProfileOut
        self.create_schema = CustomerProfileIn
        self.update_schema = CustomerProfileIn
        self.out_schema = CustomerProfileOut
        super().__init__(self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=5)

    async def search_customers(self, account_id: int, company_name: str = None, name: str = None):
        query_set = False
        q = self.db_model.filter(account_id=account_id)

        if company_name:
            query_set = True
            q = q.filter(Q(company_name__icontains=company_name))

        if name:
            query_set = True
            q = q.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name))

        if not query_set:
            return []

        return await self.out_schema.from_queryset(q)


single_customer_crud = CustomerSimpleCRUD()
