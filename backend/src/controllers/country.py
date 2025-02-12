
# Python imports
#import logging
#import os
#import random

# Pip imports
#from fastapi import HTTPException, status
#from tortoise import Model
#from tortoise.exceptions import DoesNotExist

# Internal imports
from src.schemas.country import countryOut, countryIn
from src.crud.country_crud import country_crud
from src.auth.auth import Auth0User
from typing import List


async def create_country(country: countryIn, user: Auth0User) -> countryOut:
    country.account_id = user.app_metadata["account_id"]
    saved_country = await country_crud.create(country)
    return saved_country

async def fetch_countries(user: Auth0User):
    return await country_crud.get_all(user.app_metadata["account_id"])
