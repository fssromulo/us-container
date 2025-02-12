# Pip imports
import factory
from async_factory_boy.factory.tortoise import AsyncTortoiseFactory

# Internal imports
from src.database import models


class DriverFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.Driver

    company_name = factory.Faker('company')
    city = factory.Faker('city')
    state = factory.Faker('state_abbr')
    phone_number = factory.Faker('phone_number')
    email = factory.Faker('email')
    cost_per_mile = factory.Faker('pydecimal', right_digits=2, positive=True, min_value=2, max_value=10)
    cost_per_100_miles = factory.Faker('pydecimal', right_digits=2, positive=True, min_value=100, max_value=10000)
    account = factory.SubFactory('tests.fixture.AccountFactory')
