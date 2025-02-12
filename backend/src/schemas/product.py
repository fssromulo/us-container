# Pip imports
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.pricing.product import Product


ProductIn = pydantic_model_creator(Product, name="ProductIn", exclude_readonly=True)

ProductOut = pydantic_model_creator(Product, name="ProductOut")
