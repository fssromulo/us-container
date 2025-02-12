# Python imports
import logging
from typing import List

# Pip imports
from loguru import logger
from tortoise.expressions import Q
from tortoise.models import Model

# Internal imports
from src.crud._types import PAGINATION
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.customer.order_customer import OrderCustomer
from src.schemas.customer import CustomerDetailOut, CustomerIn, CustomerOut


class CustomerCRUD(TortoiseCRUD):
    def __init__(self) -> None:
        self.db_model = OrderCustomer
        self.schema = CustomerOut
        self.create_schema = CustomerIn
        self.update_schema = CustomerIn
        self.out_schema = CustomerDetailOut
        super().__init__(self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=5)

    async def get_latest(self, account_id: int, item_id: str) -> Model:
        results = await self.get_one(account_id, item_id)
        sorted_orders = sorted(results.order, key=lambda x: x.created_at, reverse=True)
        results.order = [sorted_orders[0]]
        return results

    async def search_customers_by_params(
        self, account_id, email: str = None, phone: str = None, company_name: str = None, name: str = None
    ) -> List[Model]:
        query_set = False
        q = self.db_model.filter(account_id=account_id)
        if email:
            # q = q.filter(email__icontains=email)
            query_set = True
            q = q.filter(Q(email__icontains=email) | Q(email__icontains=email.lower()))
        if name:
            query_set = True
            q = q.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name))
        if phone:
            query_set = True
            only_digits = ''.join(filter(str.isdigit, phone))
            phone_format_1 = f"({only_digits[:3]}) {only_digits[3:6]}-{only_digits[6:]}"
            q = q.filter(
                Q(phone__icontains=phone) | Q(phone__icontains=phone_format_1) | Q(phone__icontains=only_digits)
            )
        if company_name:
            query_set = True
            q = q.filter(Q(company_name__icontains=company_name))
        if not query_set:
            return []
        return await self.out_schema.from_queryset(q)

    async def search_customers(
        self,
        account_id,
        customer_email: str,
        customer_phone: str,
        customer_name: str,
        customer_company_name: str,
        pagination: PAGINATION = {},
    ) -> List[Model]:
        # skip, limit = pagination.get("skip"), pagination.get("limit")

        query_set = False
        q = self.db_model.filter(account_id=account_id)
        if customer_email and customer_email != 'null':
            logger.info(f"customer_email: {customer_email}")
            query_set = True

            q = q.filter(email__icontains=customer_email)
            q = q.filter(Q(email__icontains=customer_email) | Q(email__icontains=customer_email.lower()))

        if customer_phone and customer_phone != 'null':
            logger.info(f"customer_phone: {customer_phone}")
            query_set = True
            # search phone by multiple formats
            only_digits = ''.join(filter(str.isdigit, customer_phone))
            phone_format_1 = f"({only_digits[:3]}) {only_digits[3:6]}-{only_digits[6:]}"

            q = q.filter(
                Q(phone__icontains=customer_phone)
                | Q(phone__icontains=phone_format_1)
                | Q(phone__icontains=only_digits)
            )

        if customer_name and customer_name != 'null':
            logger.info(f"customer_name: {customer_name}")
            query_set = True
            q = q.filter(Q(first_name__icontains=customer_name) | Q(last_name__icontains=customer_name))
            # q = q.filter(last_name__icontains=customer_name)

        if customer_company_name and customer_company_name != 'null':
            query_set = True
            q = q.filter(Q(company_name__icontains=customer_company_name))

        if not query_set:
            return []

        # q = q.offset(cast(int, skip))

        # if limit:
        #     q = q.limit(min(limit, self.max_limit))

        return await self.schema.from_queryset(q)

    async def get_one_without_exception(self, account_id: int, item_id: str) -> Model:
        if self.has_account_id():
            model = await self.db_model.filter(account_id=account_id).filter(id=item_id).first()
        else:
            model = await self.db_model.get(id=item_id)
        if model:
            return await self.schema.from_tortoise_orm(model)
        else:
            return None

    async def delete_one_without_exception(self, account_id: int, item_id: str) -> Model:
        model: Model = await self.get_one_without_exception(account_id, item_id)
        if not model:
            return None
        await self.db_model.filter(id=item_id).delete()

        return model

    async def delete_all_in_list(self, account_id: int, ids_list_to_delete: List[int]) -> List[Model]:
        await self.db_model.filter(account_id=account_id).filter(id__in=ids_list_to_delete).delete()
        return


customer_crud = CustomerCRUD()
