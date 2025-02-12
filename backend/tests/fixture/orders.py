# Pip imports
import factory
from async_factory_boy.factory.tortoise import AsyncTortoiseFactory
from faker import Faker

# Internal imports
from src.database import models


fake = Faker()

STATUS_VALUES = [
    "Cancelled",
    "Completed",
    "Delivered",
    "Expired",
    "Invoiced",
    "Paid",
    "Partially Paid",
    "Purchase Order",
]


def get_enum_field(enum):
    return fake.word(ext_word_list=[e.value for e in enum])


class OrderCustomerFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.OrderCustomer

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    street_address = factory.Faker("street_address")
    email = factory.Faker("email")
    phone = factory.Faker("phone_number")
    zip = factory.Faker("zipcode")
    state = factory.Faker("state_abbr")
    city = factory.Faker("city")
    county = factory.Faker("country")
    account = factory.SubFactory("tests.fixture.AccountFactory")


class OrderAddressFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.OrderAddress

    street_address = factory.Faker("street_address")
    zip = factory.Faker("zipcode")
    state = factory.Faker("state_abbr")
    city = factory.Faker("city")
    county = factory.Faker("country")


class OrderFactory(AsyncTortoiseFactory):
    class Meta:
        model = models.Order

    display_order_id = factory.Faker("uuid4")
    paid_at = str(fake.date_time_this_month())
    completed_at = str(fake.date_time_this_month())
    delivered_at = str(fake.date_time_this_month())
    payment_type = get_enum_field(enum=models.PaymentOptions)
    remaining_balance = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=10000)
    sub_total_price = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=10000)
    total_price = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=10000)
    gateway_cost = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=10000)
    profit = factory.Faker("pydecimal", right_digits=2, positive=True, min_value=1, max_value=10000)
    type = get_enum_field(enum=models.PurchaseTypes)
    status = fake.word(ext_word_list=STATUS_VALUES)
    attributes = factory.Faker("json", data_columns={"id": "pyint", "name": "name", "email": "email"}, num_rows=1)
    coming_from = fake.paragraph(nb_sentences=1)
    account = factory.SubFactory("tests.fixture.AccountFactory")
    user = factory.SubFactory("tests.fixture.UserFactory", account=account)
    address = factory.SubFactory(OrderAddressFactory)
    customer = factory.SubFactory(OrderCustomerFactory, account=account)
