# Pip imports
import factory
from async_factory_boy.factory.tortoise import AsyncTortoiseFactory
from faker import Faker

# Internal imports
from src.database import models


fake = Faker()


def get_product_type():
    return fake.word(ext_word_list=[ct.value for ct in models.ContainerTypes])


class ContainerPriceFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.ContainerPrice

    container_size = fake.paragraph(nb_sentences=1)
    product_type = get_product_type()
    sale_price = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=10000)
    daily_rental_price = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=10000)
    attributes = factory.Faker("json", data_columns={"id": "pyint", "high_cube": "pystr"}, num_rows=1)
    condition = fake.paragraph(nb_sentences=1)
    description = fake.paragraph(nb_sentences=1)
    location = factory.SubFactory("tests.fixture.LocationPriceFactory")
    account = factory.SubFactory("tests.fixture.AccountFactory")
