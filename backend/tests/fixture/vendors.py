# Pip imports
import factory
from async_factory_boy.factory.tortoise import AsyncTortoiseFactory

# Internal imports
from src.database import models


class VendorsFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.Vendor

    name = factory.Faker('company')
    address = factory.Faker('street_address')
    city = factory.Faker('city')
    state = factory.Faker('state_abbr')
    zip = factory.Faker('zipcode')
    primary_email = factory.Faker('email')
    secondary_email = factory.Faker('email')
    primary_phone = factory.Faker('phone_number')
    secondary_phone = factory.Faker('phone_number')
    account = factory.SubFactory('tests.fixture.AccountFactory')
