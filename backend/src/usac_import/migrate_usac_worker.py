# Python imports
import sys

# Pip imports
from loguru import logger


sys.path.append("..")
# Python imports
import asyncio  # noqa: F401, E402
import time  # noqa: F401, E402

# Pip imports
from motor.motor_asyncio import AsyncIOMotorClient  # noqa: F401, E402
from tortoise import Tortoise  # noqa: F401, E402

# Internal imports
# from bson import ObjectId
from src.crud.auth0_management import Auth0Management  # noqa: F401, E402
from src.database.config import TORTOISE_ORM  # noqa: F401, E402
from src.database.models.user import User  # noqa: F401, E402

from . import email_service  # noqa: F401, E402


ACCOUNT_ID = 2
auth0 = Auth0Management()

client = AsyncIOMotorClient()


async def close_orm():
    await Tortoise.close_connections()


async def register_tortise():
    logger.info("registering tortoise")
    TORTOISE_ORM["apps"]["models"]["models"] = ["src.database.models", "aerich.models"]
    await Tortoise.init(config=TORTOISE_ORM)


path = "/Users/tannerschmoekel/Projects/other/container-crm/backend/src/usac_import/"


def compare_lists(list1, list2):
    diff = []
    for item in list1:
        if item not in list2:
            diff.append(item)
    return diff


async def re_create_user(sendEmail=False):
    users = await User.filter(email__in=["courtney@amobilebox.com", "smcnair520@gmail.com"])
    for user in users:
        logger.info(user)
        user_created = await auth0.create_user(user, ACCOUNT_ID)
        logger.info(user_created)

        if user.role_id:
            auth_user = await auth0.assign_user_to_role(user, user.role_id)
            logger.info(auth_user)
        if sendEmail:
            r = await auth0.create_password_change_ticket(user.id, ACCOUNT_ID)
            logger.info(r)

            emailData = {
                "first_name": user.first_name,
                "company_name": "USA Containers",
                "url": r["ticket"],
                "email": user.email,
            }
            logger.info(email_service.send_change_password_email(emailData))


async def send_password_change_tickets():
    users = await User.filter(email__in=["kaylinvena@gmail.com"])
    for user in users:
        logger.info(user.email)
        # logger.info(await auth0.update_user(user, account_id=ACCOUNT_ID))
        r = await auth0.create_password_change_ticket(user.id, 1)
        logger.info(r)
        logger.info(r["ticket"])
        emailData = {
            "first_name": user.first_name,
            "company_name": "USA Containers",
            "url": r["ticket"],
            "email": user.email,
        }
        logger.info(email_service.send_change_password_email(emailData))


async def migrate_all():
    start = time.time()
    await register_tortise()
    # await send_password_change_tickets()
    await re_create_user(sendEmail=False)
    await close_orm()
    end = time.time()
    logger.info(end - start)


if __name__ == "__main__":
    # # Python imports
    # import asyncio

    loop = client.get_io_loop()
    loop.run_until_complete(migrate_all())
