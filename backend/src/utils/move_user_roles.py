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


# production
# role_ids = [
#     {'name': 'sales_agent', 'id': 'rol_bW7wiNnEtfakpJmy', 'rate': 0  },
#     {'name': 'sales_manager', 'id': 'rol_GEbHfDVHU8D7J5c0', 'rate': 45 },
#     {'name': 'internal_sales', 'id': 'rol_OOwBC28NhG4Y9V9r', 'rate': 30 },
#     {'name': 'superadmin', 'id': 'rol_D2s4oMPSdUkaL2rH', 'rate': 50 },
#     {'name': 'sales_director', 'id': 'rol_dpWbWJ6j09RsT7NY', 'rate': 45 },
#     {'name': 'accessories_manager', 'id': 'rol_CG709seARElVBQgW', 'rate': 50 },
#     {'name': 'admin', 'id': 'rol_0U2X68cqHXgjMKA5', 'rate': 50 },
#     {'name': 'customer_service', 'id': 'rol_ZrE7B6A4spysPrjC', 'rate': 50 },
#     {'name': 'customer_service_manager', 'id': 'rol_m0RvW39N6OAP3KWm', 'rate': 50 },
#     {'name': 'delivery', 'id': 'rol_K9u41gjLMgaa5RLH', 'rate': 50 },
#     {'name': 'delivery_manager', 'id': 'rol_CIeT4CD9woFaSjBw', 'rate': 50 },
#     {'name': 'Financial Operations Manager', 'id': 'rol_KNaiHHv9NBzaOp8O', 'rate': 50 },
#     {'name': 'HR & Finance Manager', 'id': 'rol_LrOpLDqVFz2iZVtw', 'rate': 50 },
#     {'name': 'HR Manager', 'id': 'rol_hVspqVTWdE41fmUJ', 'rate': 50 },
#     {'name': 'inventory', 'id': 'rol_s9HKFGVizJvNIZwH', 'rate': 50 },
#     {'name': 'inventory-manager', 'id': 'rol_qVyiHgbzjLi37FHt', 'rate': 50 },
#     {'name': 'President', 'id': 'rol_GidIhv44Wi3HrO3X', 'rate': 50 },
#     {'name': 'VP Sales', 'id': 'rol_4Et7ws8zE3cQ4nGn', 'rate': 50 },
# ]

role_ids = [
    {'name': 'sales_agent', 'id': 'rol_bdrdf9reLqNjVX7C', 'rate': 0},
    {'name': 'sales_manager', 'id': 'rol_Y3Fqrny6KcXFTHnU', 'rate': 45},
    {'name': 'internal_sales', 'id': 'rol_VX5fKnKtv2pXOjNI', 'rate': 30},
    {'name': 'superadmin', 'id': 'rol_CAIy8AceKjETS7Hn', 'rate': 50},
    {'name': 'sales_director', 'id': 'rol_Wj564GREw93NvTyl', 'rate': 45},
]
manager_roles = ["sales_manager", "internal_sales"]


client = AsyncIOMotorClient()


async def close_orm():
    await Tortoise.close_connections()


async def register_tortise():
    logger.info("registering tortoise")

    await Tortoise.init(config=TORTOISE_ORM)


async def main():
    # Step 1: Fetch users per role and create a list of CommissionIn
    await register_tortise()
    commissions: List[CommissionIn] = []
    for role in role_ids:
        user_ids = []
        users = await user_crud.get_by_role_id(role.get('id'), 1)
        for user in users:
            user_ids.append(user.id)
        # fetch user ids already in commission_rate table and remove those ids from user_ids
        existing_users = await commission_crud.get_user_by_user_ids(user_ids)
        for existing_user in existing_users:
            if existing_user.user_id in user_ids:
                user_ids.remove(existing_user.user_id)
        for user in user_ids:
            commissions.append(
                CommissionIn(
                    commission_percentage=role.get('rate'),
                    commission_effective_date='2019-01-01 00:00:00+00',
                    user_id=user,
                )
            )

    # Step 2: Save List
    await commission_crud.bulk_create(commissions, len(commissions))
    await close_orm()
    sys.exit(1)


if __name__ == "__main__":
    # # Python imports
    # import asyncio
    loop = client.get_io_loop()
    loop.run_until_complete(main())
