# Python imports
import asyncio
import csv
import os

# Pip imports
from loguru import logger
from tortoise import Tortoise


# Initialize models

# Enable schemas to read relationship between models
STAGE = os.environ.get("STAGE", "dev")


def handler():
    result = asyncio.run(async_handler())
    return {'statusCode': 200, 'body': result}


async def async_handler():
    # Internal imports
    from src.database.config import TORTOISE_ORM  # noqa: E402

    await Tortoise.init(config=TORTOISE_ORM)
    # Internal imports
    from src.database.tortoise_init import init_models

    init_models()

    # Internal imports
    from src.crud.fixed_location_price_crud import fixed_location_price_crud  # noqa: E402
    from src.schemas.fixed_location_price import FixedLocationPriceInSchema

    try:
        # Filepath to the CSV (you might want to modify this part to suit your directory structure)
        csv_file_path = (
            '/Users/tannerschmoekel/Projects/other/container-crm/backend/src/utils/fixed_location_pricing.csv'
        )

        # Read and process CSV
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)
            list_of_fixed_location_price_data = []

            # Iterate through the rows in the CSV
            for row in csvreader:
                postal_code = row['postal_code']
                location_id = row['location_id']

                for index, prop in enumerate(
                    [(row['20_rental'], row['20_purchase']), (row['40_rental'], row['40_purchase'])]
                ):
                    size = ''
                    if index == 0:
                        size = '20'
                    elif index == 1:
                        size = '40'

                    if not size:
                        logger.info("this should be hit")
                        continue

                    # Validate data (make sure price is a float, for example)
                    try:
                        fixed_location_price_data = FixedLocationPriceInSchema(
                            postal_code=postal_code,
                            location_id=location_id,
                            size=size,
                            sale_shipping_price=prop[1],
                            rent_shipping_price=prop[0],
                        )

                        list_of_fixed_location_price_data.append(fixed_location_price_data)
                        # Insert into the database
                        logger.info(f"Inserted: {postal_code}, {location_id}")
                    except Exception as e:
                        logger.info(f"Error inserting row {row}: {e}")

        await fixed_location_price_crud.bulk_create(list_of_fixed_location_price_data, batch_size=1000)
    except Exception as e:
        result = f"An error occurred: {e}"
        logger.info(result)
    finally:
        await Tortoise.close_connections()

    return {"status": "Data import complete"}


if __name__ == "__main__":
    handler()
