# Python imports
from typing import List

# Pip imports
from tortoise.models import Model

# Internal imports
from src.crud._utils import NOT_FOUND
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.pricing.product_category import ProductCategory
from src.schemas.product_category import ProductCategoryIn, ProductCategoryOut


class ProductCategoryCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = ProductCategoryOut
        self.create_schema = ProductCategoryIn
        self.update_schema = ProductCategoryIn
        self.db_model = ProductCategory
        TortoiseCRUD.__init__(self, self.schema, self.db_model, self.create_schema, self.update_schema, max_limit=50)

    async def get_product_categories(self, account_id) :
        return await self.db_model.all()

product_category_crud = ProductCategoryCRUD()
