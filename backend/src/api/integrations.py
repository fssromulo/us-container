# Pip imports
from fastapi import APIRouter, Depends, status

# Internal imports
from src.dependencies import auth


router = APIRouter(
    tags=["integrations"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)
