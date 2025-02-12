# Python imports
import asyncio

# Pip imports
from faker import Faker
from loguru import logger
from tortoise import Tortoise

# Internal imports
from src.database.config import TORTOISE_ORM


fake = Faker()


async def close_orm():
    await Tortoise.close_connections()


async def register_tortoise():
    logger.info("Registering tortoise")
    await Tortoise.init(config=TORTOISE_ORM)


# Bulk update function
async def bulk_update_pii():
    # Connect to the database
    await register_tortoise()

    # before running, pause a moment to make sure the db is the correct instance.
    # display a countdown
    for i in range(5, 0, -1):
        logger.info(f"Starting in {i} seconds...")
        await asyncio.sleep(1)

    connection = Tortoise.get_connection("default")

    # Generate fake data and update order_customer
    logger.info("Updating order_customer")
    fake_order_customer_data = [
        (
            fake.first_name(),
            fake.last_name(),
            fake.email(),
            fake.phone_number(),
            fake.zipcode(),
            fake.state(),
            fake.city(),
            'None',
            fake.company(),
            row["id"],
        )
        for row in await connection.execute_query_dict("SELECT id FROM order_customer")
    ]

    await connection.execute_many(
        """
        UPDATE order_customer
        SET
            first_name = $1,
            last_name = $2,
            email = $3,
            phone = $4,
            zip = $5,
            state = $6,
            city = $7,
            county = $8,
            company_name = $9
        WHERE id = $10
        """,
        fake_order_customer_data,
    )

    # Generate fake data and update order_address
    logger.info("Updating order_address")
    fake_order_address_data = [
        (fake.zipcode(), fake.state(), fake.city(), 'None', row["id"])
        for row in await connection.execute_query_dict("SELECT id FROM order_address")
    ]

    await connection.execute_many(
        """
        UPDATE order_address
        SET
            zip = $1,
            state = $2,
            city = $3,
            county = $4
        WHERE id = $5
        """,
        fake_order_address_data,
    )

    # Generate fake data and update customer_contact
    logger.info("Updating customer_contact")
    fake_customer_contact_data = [
        (fake.first_name(), fake.last_name(), fake.email(), fake.phone_number(), row["id"])
        for row in await connection.execute_query_dict("SELECT id FROM customer_contact")
    ]

    await connection.execute_many(
        """
        UPDATE customer_contact
        SET
            first_name = $1,
            last_name = $2,
            email = $3,
            phone = $4
        WHERE id = $5
        """,
        fake_customer_contact_data,
    )

    logger.info("PII data successfully updated.")


# Main function to execute the script
if __name__ == "__main__":
    asyncio.run(bulk_update_pii())
