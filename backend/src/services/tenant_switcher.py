# Python imports
import sys # noqa: F401, E402

# Pip imports

# Internal imports
from src.crud.account_crud import account_crud # noqa: F401, E402

# from bson import ObjectId
from src.crud.auth0_management import Auth0Management  # noqa: F401, E402
from src.crud.user_crud import user_crud  # noqa: F401, E402
from src.database.models.account import Account
from src.schemas.users import UserInUpdateSchema  # noqa: F401, E402

auth0 = Auth0Management()

def compare_lists(list1, list2):
    diff = []
    for item in list1:
        if item not in list2:
            diff.append(item)
    return diff


async def change_auth(from_account_id, to_account_id, user_email):
    user = await user_crud.get_by_email(from_account_id, user_email)
    await auth0.add_metadata_to_user_account({"account_id": to_account_id, "id": str(user.id)}, user, to_account_id)
    await user_crud.update(
        from_account_id, user.id, UserInUpdateSchema(**{"account_id": to_account_id, "email": user_email})
    )

    users = await auth0.list_users(to_account_id)
    for user in users:
        if user['email'] == user_email:
            break


async def migrate_user(from_account_id, to_account_id, user_email):
    await change_auth(from_account_id=from_account_id, to_account_id=to_account_id, user_email=user_email)
