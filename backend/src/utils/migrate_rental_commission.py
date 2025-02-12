# Python imports
import sys  # noqa: F401, E402

# Pip imports
from loguru import logger


sys.path.append("..")

# Python imports
import time  # noqa: F401, E402

# Pip imports
from motor.motor_asyncio import AsyncIOMotorClient  # noqa: F401, E402
from tortoise import Tortoise  # noqa: F401, E402

# Internal imports
from src.crud.account_crud import account_crud  # noqa: F401, E402
from src.crud.commission_crud import commission_crud
from src.crud.user_crud import user_crud  # noqa: F401, E402
from src.database.config import TORTOISE_ORM  # noqa: F401, E402
from src.schemas.commission import CommissionIn


client = AsyncIOMotorClient()


async def close_orm():
    await Tortoise.close_connections()


async def register_tortise():
    logger.info("registering tortoise")

    await Tortoise.init(config=TORTOISE_ORM)


async def main():
    # Step 1: Fetch users per role and create a list of CommissionIn
    await register_tortise()
    commissions = []
    agents = []
    managers = []
    users = await user_crud.get_all_agents(1)
    for user in users:
        agents.append(user.id)
    # users not under a team leader
    non_agent_users = await user_crud.get_all_users_not_in(1, agents)
    for non_agent_user in non_agent_users:
        managers.append(non_agent_user.id)
    related_agent_commissions = await commission_crud.get_user_by_user_ids(agents)
    related_non_agent_user_commissions = await commission_crud.get_user_by_user_ids(managers)
    for tmp in related_agent_commissions:
        tmp.rental_total_flat_commission_rate = 150
    for tmp in related_non_agent_user_commissions:
        tmp.rental_total_flat_commission_rate = 200
    # Step 2: Save List
    logger.info(len(agents))
    logger.info(len(managers))
    # TODO uncomment to save updated rates in db
    await commission_crud.bulk_update(
        related_agent_commissions, ['rental_total_flat_commission_rate'], len(related_agent_commissions)
    )
    await commission_crud.bulk_update(
        related_non_agent_user_commissions,
        ['rental_total_flat_commission_rate'],
        len(related_non_agent_user_commissions),
    )
    await close_orm()
    sys.exit(1)


if __name__ == "__main__":
    # # Python imports
    # import asyncio
    loop = client.get_io_loop()
    loop.run_until_complete(main())
