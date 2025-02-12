# Pip imports
from loguru import logger
from tortoise.expressions import Q
from tortoise.models import Model

# Internal imports
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.customer.customer_contact import CustomerContact
from src.schemas.customer_contact import CustomerContactIn, CustomerContactOut


class CustomerContactCRUD(TortoiseCRUD):
    def __init__(self) -> None:
        self.db_model = CustomerContact
        self.schema = CustomerContactOut
        self.create_schema = CustomerContactIn
        self.update_schema = CustomerContactIn
        self.out_schema = CustomerContactOut
        super().__init__(self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=5)

    async def get_by_email(self, account_id: int, email: str) -> Model:
        if self.schema.schema().get("properties").get("email"):
            model = await self.db_model.filter(account_id=account_id).filter(email=email).first()
        if self.schema.schema().get("properties").get("primary_email"):
            model = await self.db_model.filter(account_id=account_id).filter(primary_email=email).first()
        if model:
            results = await self.schema.from_tortoise_orm(model)
            return results
        else:
            raise Exception("Not found")

    async def get_by_filters_all(
        self, account_id: int, email: str = None, phone: str = None, name: str = None
    ) -> Model:
        model = None
        if email:
            model = self.db_model.filter(account_id=account_id).filter(email__icontains=email).all()
        if phone:
            model = self.db_model.filter(account_id=account_id).filter(phone__icontains=phone).all()
        if name:
            model = self.db_model.filter(Q(first_name__icontains=name) | Q(last_name__icontains=name)).all()
        if model:
            results = await self.schema.from_queryset(model)
            logger.info(f"Found {len(results)} customer contacts")
            return results
        else:
            logger.info("No customer contacts found")
            return []

    async def get_by_customer_id(self, account_id: int, customer_id: str):
        model = self.db_model.filter(account_id=account_id).filter(customer_id=customer_id).all()
        results = await self.schema.from_queryset(model)
        return results


customer_contact_crud = CustomerContactCRUD()
