# Python imports

# Pip imports
from tortoise.contrib.pydantic import pydantic_model_creator

# Internal imports
from src.database.models.audit import Audit


AuditInSchema = pydantic_model_creator(Audit, name="AuditIn", exclude_readonly=True)

AuditOutSchema = pydantic_model_creator(Audit, name="AuditOut")
