# Pip imports
import factory
from async_factory_boy.factory.tortoise import AsyncTortoiseFactory

# Internal imports
from src.database import models


class UserFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.User

    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = factory.Faker('password', length=12)
    account = factory.SubFactory('tests.fixture.AccountFactory')
