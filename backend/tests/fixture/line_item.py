# Pip imports
import factory
from async_factory_boy.factory.tortoise import AsyncTortoiseFactory

# Internal imports
from src.database import models


class LineItemFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.LineItem

    minimum_shipping_cost = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=200)
    potential_dollar_per_mile = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=500)
    potential_miles = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=10000)
    product_cost = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=10000)
    revenue = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=10000)
    shipping_revenue = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=100)
    shipping_cost = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=100)
    tax = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=750)
    potential_driver_charge = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=750)
    convenience_fee = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=250)
    rent_period = factory.Faker("pyint", min_value=1, max_value=100)
    interest_owed = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=10000)
    total_rental_price = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=10000)
    monthly_owed = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=10000)
    attributes = factory.Faker("json", data_columns={"id": "pyint", "name": "name", "email": "email"}, num_rows=1)
    # inventory = factory.SubFactory("tests.fixture.InventoryFactory")
    driver = factory.SubFactory("tests.fixture.DriverFactory")
    potential_driver = factory.SubFactory("tests.fixture.DriverFactory")
    order = factory.SubFactory("tests.fixture.OrderFactory")
