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
from src.crud.user_crud import user_crud  # noqa: F401, E402
from src.database.config import TORTOISE_ORM  # noqa: F401, E402
from src.services.tenant_switcher import migrate_user


tenants = [
    {'name': 'ContainerCrm', 'id': 0, 'accounts': [1, 5]},
    {'name': 'ContainerCrm Shared', 'id': 1, 'accounts': [2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14]},
]


client = AsyncIOMotorClient()


async def close_orm():
    await Tortoise.close_connections()


async def register_tortise():
    logger.info("registering tortoise")

    await Tortoise.init(config=TORTOISE_ORM)


async def close_orm():
    await Tortoise.close_connections()


async def main():
    # Step 1: Ask for the user's email
    await register_tortise()
    tenant_accounts = []
    logger.info("\nAvailable tenants to choose from\n")
    for _tenant in tenants:
        logger.info(f"{_tenant.get('id')}. {_tenant.get('name')}")
        # Step 4: Let the user select an account
    selected_tenant = input("\n(Select a tenant and press enter)\n")
    if int(selected_tenant) not in [0, 1]:
        logger.info("\nWrong option selected, try again \n")
        sys.exit(1)
    tenant_accounts = tenants[int(selected_tenant)].get('accounts')

    email = input("What is the email for the user account to switch?\n")
    user = await user_crud.get_user_by_email_account_ids(email, tenant_accounts)
    if user is None:
        logger.info(
            "\n Sorry either no user with the provided email was found or the provided email cannot be found on the selected tenant account(s)\n"
        )
        sys.exit(1)
    current_account_id = user.account_id
    account: Account = await account_crud.get_one(current_account_id)
    # Step 2: Show the current account details
    if user is not None:
        current_account = {'Account No': user.account_id, 'Account Name': account.name}

        logger.info("\n Here’s the current account this user has:")
        logger.info(f"Account No: {current_account['Account No']}")
        logger.info(f"Account Name: {current_account['Account Name']}")

        # Step 3: Ask which account to switch to
        logger.info("\nWhich account do you want to switch to?")
        accounts = await account_crud.get_all()
        account_ids = []
        for account in accounts:
            if account.id in tenant_accounts:
                logger.info(f"{account.id}. {account.name}")
                account_ids.append(int(account.id))
        # Step 4: Let the user select an account
        selected_account = input("\n(select the one you want press enter)\n")
        selected_account = int(selected_account)
        # Check if the selected account is valid
        if selected_account in account_ids:
            for acc in accounts:
                if acc.id == selected_account:
                    logger.info(f"\nSwitching to account: {acc.name}")
                    await migrate_user(
                        from_account_id=current_account_id, to_account_id=int(selected_account), user_email=email
                    )
                    user = await user_crud.get_user_by_email(email)
                    current_account_id = user.account_id
                    account: Account = await account_crud.get_one(current_account_id)
                    current_account = {'Account No': user.account_id, 'Account Name': account.name}
                    logger.info("*************************************************************************")
                    logger.info("\nUpdated Account Detail:")
                    logger.info(f"Email: {email}")
                    logger.info(f"Account No: {current_account['Account No']}")
                    logger.info(f"Account Name: {current_account['Account Name']}")
                    logger.info("*************************************************************************")
                    logger.info("\nRequest completed")
                    await close_orm()
                    sys.exit(1)
        else:
            logger.info("\nInvalid account selected. Please try again.")
            sys.exit(1)
    logger.info("\nInvalid data entered. Please try again.")
    sys.exit(1)


if __name__ == "__main__":
    # # Python imports
    # import asyncio
    loop = client.get_io_loop()
    loop.run_until_complete(main())
