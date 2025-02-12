# Python imports
import uuid
from typing import Any, Dict, List

# Pip imports
from faker import Faker


fake = Faker()


def mock_user_data() -> Dict[str, Any]:
    user_id = str(uuid.uuid4())
    return {
        "email": "jane@doe.com",
        "nickname": "JaneDoe",
        "name": "Jane Doe",
        "user_metadata": {},
        "blocked": False,
        "email_verified": True,
        "app_metadata": {"account_id": str(uuid.UUID), "id": user_id},
        "given_name": "Jane",
        "family_name": "Doe",
        "user_id": user_id,
        "connection": "Username-Password-Authentication",
        "password": "DSkjlasda&^$!",
    }


class Auth0MockData:
    def __init__(self) -> None:
        self.AUTH0_TOKEN = self.token
        self.AUTH0_CREATE_USER = self.create_user
        self.AUTH0_LIST_USERS = self.list_users
        self.AUTH0_UPDATE_USER = self.update_user
        self.AUTH0_CREATE_PASSWORD_CHANGE_TICKET = self.ticket_data
        self.AUTH0_USER_ROLE = self.user_role
        self.AUTH0_RESOURCE_SERVER_BY_ID = self.resource_server_by_id
        self.AUTH0_ROLES_PERMISSIONS = self.roles_permissions
        self.AUTH0_CREATE_ROLE = self.create_role
        self.AUTH0_PERMISSIONS = self.permissions

    def token(self) -> Dict[str, Any]:
        return {"access_token": fake.password(length=12), "token_type": "Bearer", "expires_in": 86400}

    def user_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "user_id": f"auth0|{data.get('user_id')}",
            "email": data.get("email"),
            "email_verified": bool(data.get("email_verified", "False")),
            "username": data.get("nickname"),
            "phone_number": data.get("phone"),
            "phone_verified": bool(data.get("phone_verified", "False")),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
            "identities": [
                {
                    "connection": "Initial-Connection",
                    "user_id": data.get("user_id"),
                    "provider": data.get("auth0", "auth0"),
                    "isSocial": bool(data.get("isSocial", "False")),
                }
            ],
            "app_metadata": data.get("app_metadata"),
            "user_metadata": data.get("user_metadata"),
            "picture": data.get("picture", ""),
            "name": data.get('name'),
            "nickname": data.get("nickname"),
            "multifactor": data.get("multifactor", [""]),
            "last_ip": data.get("last_ip", ""),
            "last_login": data.get("last_login", ""),
            "logins_count": data.get("logins_count", 0),
            "blocked": bool(data.get("blocked", "False")),
            "given_name": data.get("given_name"),
            "family_name": data.get("family_name"),
        }

    def role_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return dict(id=str(uuid.uuid4()), name=data.get("name"), description="USAC Role")

    def ticket_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return dict(ticket=f"https://login.auth0.com/lo/reset?client_id={data.get('client_id')}&tenant=mdos&bew=bmN")

    def resource_server_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": data.get("id", "Test_ID"),
            "name": data.get("name", "Test Name"),
            "is_system": bool(data.get("is_system", "False")),
            "identifier": data.get("identifier", "Test_Identifier"),
            "scopes": data.get("scopes", ["approve:team_members", "create:product", "read:all_orders"]),
            "signing_alg": data.get("signing_alg", "Test_Signing_Alg"),
            "signing_secret": data.get("signing_secret", "Test_Signing_Secret"),
            "allow_offline_access": bool(data.get("allow_offline_access", "False")),
            "skip_consent_for_verifiable_first_party_clients": False,
            "token_lifetime": int(data.get("0", "0")),
            "token_lifetime_for_web": int(data.get("0", "0")),
            "enforce_policies": bool(data.get("enforce_policies", "False")),
            "token_dialect": data.get("token_dialect", "Test_Token_Dialect"),
            "client": {},
        }

    def role_permission(self) -> Dict[str, Any]:
        return {
            "resource_server_identifier": "usac.us",
            "permission_name": "read:all_orders",
            "resource_server_name": "USAC",
            "description": "Read all orders",
        }

    def create_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.user_data(data=data)

    def list_users(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [self.user_data(data=data)]

    def update_user(self, data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        data["user_id"] = user_id
        data["name"] = f"{data.get('given_name')} {data.get('family_name')}"
        return self.user_data(data=data)

    def create_password_change_ticket(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.ticket_data(data=data)

    def user_role(self) -> List[Dict[str, Any]]:
        return [self.role_data({"name": "create:product"})]

    def resource_server_by_id(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.resource_server_data(data=data)

    def roles_permissions(self) -> List[Dict[str, Any]]:
        return [self.role_permission()]

    def create_role(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return self.role_data(data=data)

    def permissions(self) -> Dict[str, Any]:
        return {"permissions": self.roles_permissions()}
