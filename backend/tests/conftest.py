# Python imports
from typing import Generator

# Pip imports
import boto3
import pytest
from httpx import AsyncClient
from moto import mock_s3
from tortoise import Tortoise

# Internal imports
from src.auth.auth import Auth0UnauthorizedException, Auth0User
from src.database.models.user import User
from src.dependencies import auth
from src.main import app


JWT_TEST_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkJydWNlIFdheW5lIiwiaWF0IjoxNTE2MjM5MDIyfQ."
    "AQpbqtNAnwDlm80uZz8oKe97Fn0Ygm9Z1JoTWLxsH5Y"
)


@pytest.fixture(scope="module")
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="module")
async def db() -> Generator:
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["src.database.models"]})
    await Tortoise.generate_schemas()
    yield Tortoise
    await Tortoise.close_connections()


class AsyncClientCustom(AsyncClient):
    def force_login(self, user: User):
        if not user:
            raise Auth0UnauthorizedException(detail="Unauthorized")

        if not getattr(user, "account", None):
            raise Auth0UnauthorizedException(detail="Unauthorized")

        app.dependency_overrides[auth.get_user] = lambda: Auth0User(
            sub=f"auth0|{user.id}", email=user.email, app_metadata={"id": user.id, "account_id": user.account.id}
        )


@pytest.fixture(scope="function")
async def client(db: Generator) -> AsyncClientCustom:
    async with AsyncClientCustom(app=app, base_url="http://container-cmr-test-auth") as ac:
        yield ac
        app.dependency_overrides = {}
        await ac.aclose()


@pytest.fixture
def s3() -> Generator:
    with mock_s3():
        client = boto3.client('s3')
        client.create_bucket(Bucket='mock-bucket')
        client.put_object(Bucket='mock-bucket', Key='test_mock_image.jpg', Body='{"name": "mock-body"}')
        yield client
