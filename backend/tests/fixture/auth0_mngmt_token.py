# Pip imports
import factory
from async_factory_boy.factory.tortoise import AsyncTortoiseFactory

# Internal imports
from src.database import models


class Auth0TokenFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.AuthManagementToken

    token = factory.Faker('password', length=12)
    account = factory.SubFactory('tests.fixture.AccountFactory')
