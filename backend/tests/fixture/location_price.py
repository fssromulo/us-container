# Pip imports
import factory
from async_factory_boy.factory.tortoise import AsyncTortoiseFactory
from faker import Faker

# Internal imports
from src.database import models


fake = Faker()


def get_region():
    return fake.word(ext_word_list=[region.value for region in models.Region])


class LocationPriceFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.LocationPrice

    city = factory.Faker('city')
    state = factory.Faker('state_abbr')
    zip = factory.Faker('zipcode')
    region = get_region()
    cost_per_mile = factory.Faker('pydecimal', right_digits=2, positive=True, min_value=2, max_value=10)
    minimum_shipping_cost = factory.Faker('pydecimal', right_digits=2, positive=True, min_value=100, max_value=10000)
    account = factory.SubFactory('tests.fixture.AccountFactory')
