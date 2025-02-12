# Python imports
from typing import Optional

# Pip imports
from pydantic import BaseModel, Extra
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.assistant import Assistant
from src.database.models.team_member import TeamMember
from src.database.models.user import User


included_fields_in = [
    "id",
    "email",
    "first_name",
    "last_name",
    "display_name",
    "is_active",
    "phone",
    "role_id",
    "account_id",
    "preferences",
]

included_fields_out = [
    "team_member",
    "assistant",
    "team_lead",
    "team_member",
    "manager",
    "created_at",
    "modified_at",
]
included_fields_out.extend(included_fields_in)


class CreateUpdateUser(BaseModel):
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    display_name: Optional[str]
    is_active: Optional[str]
    phone: Optional[str]
    role_id: Optional[str]
    # team_member_of_id: Optional[str]
    # assistant_of_id: Optional[str]
    preferences: Optional[dict]
    order_type: Optional[str]
    birthday: Optional[str]
    shirt_size: Optional[str]
    team_leader_id: Optional[str]
    mailing_address: Optional[str]


class CreateTeamMember(BaseModel):
    team_lead_id: str
    team_member_id: str


class CreateAssistant(BaseModel):
    assistant_id: str
    manager_id: str


class Config:
    extra = Extra.allow
    arbitrary_types_allowed = True


UserInSchema = pydantic_model_creator(User, name="UserIn", exclude_readonly=True, config_class=Config)


UserInUpdateSchema = pydantic_model_creator(
    User, name="UserInUpdateSchema", include=included_fields_in[1:], exclude_readonly=True, config_class=Config
)

UserOutSchema = pydantic_model_creator(
    User, name="UserOut", config_class=Config, exclude=["commission.user", "transactions"]
)

TeamMemberIn = pydantic_model_creator(
    TeamMember,
    name="TeamMemberIn",
    # exclude=["created_at", "modified_at", "account", "managed_by", "sales_assistant",  "team_member_of",],
    exclude_readonly=True,
    config_class=Config,
)

TeamMemberOut = pydantic_model_creator(
    TeamMember,
    name="TeamMemberOut",
)

AssistantOut = pydantic_model_creator(
    Assistant,
    name="AssistantOut",
)

AssistantIn = pydantic_model_creator(Assistant, name="AssistantIn", exclude_readonly=True, config_class=Config)
