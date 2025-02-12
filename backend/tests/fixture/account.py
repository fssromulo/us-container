# Pip imports
import factory
from async_factory_boy.factory.tortoise import AsyncTortoiseFactory

# Internal imports
from src.database import models


class AccountFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.Account

    id = factory.Faker('random_int')
    name = factory.Faker('company')
