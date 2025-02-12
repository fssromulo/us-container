from typing import List
import requests
from fastapi import APIRouter, Depends, HTTPException
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist
import json

from src.schemas.token import Status
from src.auth.auth import Auth0User
from src.dependencies import auth
from src.controllers import google_maps
from src.controllers.google_maps import MatrixRequest
from pydantic import BaseModel

router = APIRouter(
    tags=["google_maps"],
    dependencies=[Depends(auth.implicit_scheme)],
)


@router.post(
    "/google_maps",
)
async def get_directions_matrix(matrixRequest: MatrixRequest, user: Auth0User = Depends(auth.get_user)):
    return await google_maps.get_directions_matrix(matrixRequest, user)