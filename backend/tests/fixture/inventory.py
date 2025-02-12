# Pip imports
import factory
from async_factory_boy.factory.tortoise import AsyncTortoiseFactory
from faker import Faker

# Internal imports
from src.database import models


fake = Faker()


def get_rent_started_on() -> str:
    return str(fake.date_time_this_month(before_now=True, after_now=False, tzinfo=None))


def get_purchase_type() -> str:
    return fake.word(ext_word_list=[purchase_type.value for purchase_type in models.PurchaseTypes])


class InventoryFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.Inventory

    id = factory.Faker("uuid4", cast_to=str)
    rent_started_on = get_rent_started_on()
    total_cost = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=10000)
    total_rental_revenue = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=10000)
    days_in_yard = factory.Faker("pyint", min_value=1, max_value=100)
    rental_periods_count = factory.Faker("pyint", min_value=1, max_value=100)
    condition = factory.Faker("paragraph", nb_sentences=1)
    container_number = factory.Faker("paragraph", nb_sentences=1)
    container_release_number = factory.Faker("paragraph", nb_sentences=1)
    status = factory.Faker("paragraph", nb_sentences=1)
    container_size = factory.Faker("paragraph", nb_sentences=1)
    type = factory.Faker("json", data_columns={"id": "pyint", "name": "name", "email": "email"}, num_rows=1)
    purchase_type = get_purchase_type()
    vendor = factory.SubFactory("tests.fixture.VendorsFactory")
    depot = factory.SubFactory("tests.fixture.DepotFactory")
    account = factory.SubFactory('tests.fixture.AccountFactory')
