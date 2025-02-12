# Pip imports
import factory
from async_factory_boy.factory.tortoise import AsyncTortoiseFactory

# Internal imports
from src.database import models


class DepotFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.Depot

    name = factory.Faker('company')
    street_address = factory.Faker('street_address')
    zip = factory.Faker('zipcode')
    primary_email = factory.Faker('email')
    secondary_email = factory.Faker('email')
    primary_phone = factory.Faker('phone_number')
    secondary_phone = factory.Faker('phone_number')
    city = factory.Faker('city')
    state = factory.Faker('state_abbr')
    account = factory.SubFactory('tests.fixture.AccountFactory')
