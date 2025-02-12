# Python imports
from typing import Optional

# Pip imports
from pydantic import BaseModel


class UpdateRole(BaseModel):
    name: Optional[str]
    description: Optional[str]
    account_id: Optional[int]


class DuplicateRole(BaseModel):
    role_id: Optional[str]
    role_name: Optional[str]


class UpdateRolePermission(BaseModel):
    role_id: Optional[int]
    permission_id: Optional[int]
    account_id: Optional[int]


class UpdatePermission(BaseModel):
    name: Optional[str]
    type: Optional[str]
    action: Optional[str]
    subject: Optional[str]
    account_id: Optional[int]
