# Python imports
from typing import Any, Dict, List

# Pip imports
from fastapi import HTTPException, status
from fastapi_cache import Coder
from fastapi_cache.decorator import cache
from tortoise.exceptions import DoesNotExist
from tortoise.models import Model

# Internal imports
from src.auth.auth import Auth0User
from src.crud.tortise_crud_mapper import TortoiseCRUD
from src.database.models.user import User
from src.schemas.users import CreateUpdateUser, UserInSchema, UserInUpdateSchema, UserOutSchema


def remove_user_preferences(user: User) -> User:
    user.preferences = None
    return user


class UserListCoder(Coder):
    @classmethod
    def encode(cls, value: Any) -> bytes:
        # Serialize the list of UserOutSchema objects to bytes
        return b"".join(UserOutSchema(**user).json().encode("utf-8") for user in value)

    @classmethod
    def decode(cls, value: bytes) -> List[UserOutSchema]:
        # Deserialize bytes to a list of UserOutSchema objects
        return [UserOutSchema.parse_raw(user.decode("utf-8")) for user in value.split(b"\n")]


class UserCRUD(TortoiseCRUD):
    def __init__(
        self,
    ) -> None:
        self.schema = UserOutSchema
        self.create_schema = UserInSchema
        self.update_schema = UserInUpdateSchema
        self.db_model = User
        TortoiseCRUD.__init__(
            self,
            self.schema,
            self.db_model,
            self.create_schema,
            self.update_schema,
            max_limit=50,
        )

    # @cache(namespace="users", expire=60 * 10, coder=UserListCoder)
    async def get_all(self, account_id: int) -> List[UserOutSchema]:
        account_ids = [account_id]
        if account_id == 1:
            account_ids.append(5)
        if account_id == 5:
            account_ids.append(1)

        query = self.db_model.filter(account_id__in=account_ids).order_by("-created_at")
        query_result = await self.schema.from_queryset(query)
        query_result = [remove_user_preferences(user) for user in query_result]
        return query_result

    async def get_all_team_leads(self, account_id: int) -> Any:
        query = self.db_model.filter(account_id=account_id).filter(team_lead__not_isnull=True).order_by("-created_at")
        query_result = await self.schema.from_queryset(query)
        return query_result

    async def create(self, model: Model) -> Model:
        if isinstance(model, self.create_schema):
            model = model.dict()
            db_model = self.db_model(**model)
            await db_model.save()
            saved_user = await self.schema.from_tortoise_orm(db_model)
            return saved_user

    async def update(self, account_id: int, item_id: int, model: Model) -> Model:  # type: ignore
        if isinstance(model, self.update_schema):
            model = model.dict(exclude_unset=True)
            if self.has_account_id:
                query = self.db_model.filter(account_id=account_id).filter(id=item_id)
            else:
                query = self.db_model.filter(id=item_id)
            await query.update(**model)
            return await self.schema.from_queryset_single(self.db_model.get(id=item_id))

    async def get_all_active_by_role(self, account_id: int, role_id: str) -> List[Model]:
        query = self.db_model.filter(account_id=account_id).filter(role_id=role_id).filter(is_active=True)
        query_result = await self.schema.from_queryset(query)
        return query_result

    async def update_user_preference(
        self, user_id: str, userData: CreateUpdateUser, preferences: Dict
    ) -> UserOutSchema:
        if userData.order_type == 'purchase':
            preferences['purchase'] = userData.preferences
        elif userData.order_type == 'rent':
            preferences['rent'] = userData.preferences
        elif userData.order_type == 'rent_to_own':
            preferences['rent_to_own'] = userData.preferences
        elif userData.order_type == 'all':
            preferences['all'] = userData.preferences
        await self.db_model.filter(id=user_id).update(preferences=preferences)

        new_user = await self.db_model.filter(id=user_id)
        return new_user

    async def get_by_first_created(self, account_id: int) -> Model:
        return await self.db_model.filter(account_id=account_id).order_by("created_at").first()

    async def get_user_by_email(self, email: str) -> Model:
        return await self.db_model.filter(email=email).first()

    async def get_user_by_email_account_ids(self, email: str, account_ids: list =[]) -> Model:
        return await self.db_model.filter(email=email, account_id__in=account_ids).first()
    async def get_by_role_id(self, role_id: str, account_id: int) :
        query = self.db_model.filter(account_id=account_id).filter(role_id=role_id)
        query_result = await self.schema.from_queryset(query)
        return query_result

    async def get_all_agents(self, account_id: int) -> Any:
        query = self.db_model.filter(account_id=account_id).filter(assistant__not_isnull=True).order_by("-created_at")
        query_result = await self.schema.from_queryset(query)
        return query_result
    async def get_all_users_not_in(self, account_id: int, user_ids: list) -> Any:
        query = self.db_model.filter(account_id=account_id).filter(id__not_in=user_ids).order_by("-created_at")
        query_result = await self.schema.from_queryset(query)
        return query_result

user_crud = UserCRUD()
