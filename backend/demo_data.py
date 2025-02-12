# Python imports
from decimal import Decimal
from enum import Enum

# Internal imports
from src.schemas.accounts import UpdateAccount


account = UpdateAccount(
    name="Test Account",
    is_active=True,
)


class ContainerTypes(str, Enum):
    SHIPPING_CONTAINER = "SHIPPING_CONTAINER"
    PORTABLE_CONTAINER = "PORTABLE_CONTAINER"


users = [
    {
        "email": "tanner.cordovatech@gmail.com",
        "first_name": "Tanner",
        "last_name": "Schmoekel",
        "is_active": True,
        "phone": "+1-555-555-5555",
        "role_id": "rol_u7DHp4fH7nM6I0fP",
    },
    {
        "email": "johndoe@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_active": True,
        "phone": "+1-555-555-5555",
        "role_id": None,
    },
    {
        "email": "janedoe@example.com",
        "first_name": "Jane",
        "last_name": "Doe",
        "is_active": True,
        "phone": "+1-555-555-1234",
        "role_id": None,
        "preferences": {"language": "es", "timezone": "America/Los_Angeles"},
    },
    {
        "email": "jimsmith@example.com",
        "first_name": "Jim",
        "last_name": "Smith",
        "is_active": False,
        "phone": None,
        "role_id": None,
        "preferences": None,
    },
    {
        "email": "sarahbrown@example.com",
        "first_name": "Sarah",
        "last_name": "Brown",
        "is_active": True,
        "phone": "+1-555-555-9876",
        "role_id": None,
        "preferences": {"language": "fr", "timezone": "Europe/Paris"},
    },
]

vendors = [
    {
        "name": "ABC Inc.",
        "address": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip": "10001",
        "primary_phone": "+1-555-555-5555",
        "primary_email": "info@abcinc.com",
        "secondary_phone": None,
        "secondary_email": None,
    },
    {
        "name": "XYZ Corp",
        "address": "456 Broad St",
        "city": "Los Angeles",
        "state": "CA",
        "zip": "90001",
        "primary_phone": "+1-555-555-1234",
        "primary_email": "info@xyzcorp.com",
        "secondary_phone": "+1-555-555-4321",
        "secondary_email": "support@xyzcorp.com",
    },
    {
        "name": "Acme Ltd",
        "address": "789 Oak St",
        "city": "Chicago",
        "state": "IL",
        "zip": "60601",
        "primary_phone": "+1-555-555-6789",
        "primary_email": "sales@acmeltd.com",
        "secondary_phone": "+1-555-555-7890",
        "secondary_email": "support@acmeltd.com",
    },
    {
        "name": "Main Vendor",
        "state": "TX",
        "city": "Houston",
        "address": "1234",
        "zip": 75407,
        "primary_email": "tschmoek@gmail.com",
        "secondary_email": "tschmoek@gmail.com",
        "primary_phone": 88888888888,
        "secondary_phone": 99999999999,
    },
]

locations = [
    {
        "city": "Dallas",
        "cost_per_mile": 0.8,
        "zip": "75201",
        "minimum_shipping_cost": 20.0,
        "state": "NY",
        "region": "WEST",
    },
    {
        "city": "Brazoria",
        "cost_per_mile": 5,
        "zip": "77422",
        "minimum_shipping_cost": 400,
        "state": "TX",
        "region": "WEST",
    },
    {
        "city": "Houston",
        "cost_per_mile": 5,
        "zip": "77001",
        "minimum_shipping_cost": 450,
        "state": "TX",
        "region": "WEST",
    },
]


containers = [
    {
        "container_size": "20",
        "product_type": ContainerTypes.SHIPPING_CONTAINER,
        "sale_price": Decimal("1500.00"),
        "attributes": {
            "standard": True,
            "high_cube": False,
            "double_door": False,
        },
        "condition": "Used",
        "description": "A used 20ft shipping container in good condition.",
        "location_id": None,
    },
    {
        "container_size": "40",
        "product_type": ContainerTypes.PORTABLE_CONTAINER,
        "sale_price": Decimal("2500.00"),
        "attributes": {
            "standard": True,
            "high_cube": False,
            "double_door": False,
        },
        "condition": "One-Trip",
        "description": "A brand new 40ft portable container with added ventilation.",
        "location_id": None,
    },
    {
        "container_size": "20",
        "product_type": ContainerTypes.SHIPPING_CONTAINER,
        "sale_price": Decimal("1000.00"),
        "attributes": {
            "standard": True,
            "high_cube": False,
            "double_door": False,
        },
        "condition": "Used",
        "description": "A used 10ft shipping container with minor cosmetic damage.",
        "location_id": None,
    },
    {
        "container_size": "40",
        "product_type": ContainerTypes.PORTABLE_CONTAINER,
        "sale_price": Decimal("2500.00"),
        "attributes": {
            "standard": True,
            "high_cube": False,
            "double_door": False,
        },
        "condition": "One-Trip",
        "description": "A brand new 40ft portable container with added ventilation.",
        "location_id": None,
    },
]

depot_records = [
    {
        "name": "Depot A",
        "street_address": "123 Main Street",
        "zip": 90210,
        "primary_email": "depot_a@example.com",
        "secondary_email": "depot_a2@example.com",
        "primary_phone": "555-555-1212",
        "secondary_phone": "555-555-1213",
        "city": "Beverly Hills",
        "state": "CA",
    },
    {
        "name": "Depot B",
        "street_address": "321 Oak Avenue",
        "zip": 60606,
        "primary_email": "depot_b@example.com",
        "secondary_email": None,
        "primary_phone": "555-555-2323",
        "secondary_phone": None,
        "city": "Chicago",
        "state": "IL",
    },
    {
        "name": "Depot C",
        "street_address": "456 Elm Street",
        "zip": 80202,
        "primary_email": "depot_c@example.com",
        "secondary_email": None,
        "primary_phone": "555-555-3434",
        "secondary_phone": None,
        "city": "Denver",
        "state": "CO",
    },
]

driver_records = [
    {
        "company_name": "Driver A's Trucking",
        "cost_per_mile": 2.25,
        "cost_per_100_miles": 220.00,
        "phone_number": "555-555-1111",
        "email": "driver_a@example.com",
        "city": "Miami",
        "state": "FL",
    },
    {
        "company_name": "Driver B's Logistics",
        "cost_per_mile": 1.75,
        "cost_per_100_miles": 175.00,
        "phone_number": "555-555-2222",
        "email": "driver_b@example.com",
        "city": "New York",
        "state": "NY",
    },
    {
        "company_name": "Driver C's Hauling",
        "cost_per_mile": 3.00,
        "cost_per_100_miles": 280.00,
        "phone_number": "555-555-3333",
        "email": "driver_c@example.com",
        "city": "Los Angeles",
        "state": "CA",
    },
]

inventory = [
    {
        "type": {
            "standard": False,
            "high_cube": False,
            "dimensions": "20 x 8 x 8",
            "double_door": False,
        },
        "container_number": None,
        "container_release_number": "test-release-1234",
        "vendor_id": "63a86964-4acb-483a-83d4-185a23be30b2",
        "depot_id": "ab98d142-95f9-42c5-9e08-17d5aef5b85d",
        "total_cost": 3000,
        "container_size": "20",
        "condition": "One-Trip",
        "days_in_yard": 0,
        "rental_periods_count": 0,
        "quantity": 1,
    },
    {
        "type": {
            "standard": False,
            "high_cube": False,
            "dimensions": "20 x 8 x 8",
            "double_door": False,
        },
        "container_number": None,
        "container_release_number": "test-release-2",
        "vendor_id": "dcc890c6-0783-4beb-9b64-9e0f5cfc1e3e",
        "depot_id": "13cd4ffb-67f7-413a-bef6-64587850209c",
        "total_cost": 5000,
        "container_size": "40",
        "condition": "Used",
        "days_in_yard": 0,
        "rental_periods_count": 0,
        "door_type": [],
    },
    {
        "type": {
            "standard": False,
            "high_cube": False,
            "dimensions": "20 x 8 x 8",
            "double_door": False,
        },
        "container_number": None,
        "container_release_number": "test-release-2",
        "vendor_id": "dcc890c6-0783-4beb-9b64-9e0f5cfc1e3e",
        "depot_id": "13cd4ffb-67f7-413a-bef6-64587850209c",
        "total_cost": 5000,
        "container_size": "40",
        "condition": "Used",
        "days_in_yard": 0,
        "rental_periods_count": 0,
    },
]

customers = [
    {
        "first_name": "test",
        "last_name": "test",
        "email": "tschmoek@gmail.com",
        "company_name": "",
        "phone": "(888) 888-8888",
        "street_address": "",
        "city": "",
        "state": "",
        "zip": "",
        "due_date": "",
        "notes": "",
        "order": {
            "line_items": [
                {
                    "potential_miles": 38.64,
                    "revenue": 2500,
                    "shipping_revenue": 600,
                    "tax": 248,
                    "convenience_fee": 0,
                    "door_orientation": "Facing Cab",
                    "product_city": "Brazoria",
                    "product_state": "TX",
                    "container_size": "20",
                    "condition": "Used",
                    "attributes": {
                        "standard": True,
                        "high_cube": False,
                        "dimensions": "20 x 8 x 8",
                        "double_door": False,
                    },
                },
                {
                    "potential_miles": 38.64,
                    "revenue": 2500,
                    "shipping_revenue": 600,
                    "tax": 248,
                    "convenience_fee": 0,
                    "door_orientation": "Facing Cab",
                    "product_city": "Brazoria",
                    "product_state": "TX",
                    "container_size": "20",
                    "condition": "Used",
                    "attributes": {
                        "standard": True,
                        "high_cube": False,
                        "dimensions": "20 x 8 x 8",
                        "double_door": False,
                    },
                },
            ],
            "address": {
                "city": "Pleasant Grove",
                "state": "UT",
                "zip": "84062",
                "county": "Utah",
                "street_address": "test",
            },
            "type": "PURCHASE",
            "remaining_balance": 6696,
            "sub_total_price": 6696,
            "total_price": 6696,
            "attributes": {},
        },
    }
]
