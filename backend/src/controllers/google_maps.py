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
from pydantic import BaseModel


class MatrixRequest(BaseModel):
    origins: List[str]
    destinations: List[str]


async def get_directions_matrix(matrixRequest: MatrixRequest, user: Auth0User = Depends(auth.get_user)):
    try:
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": matrixRequest.origins,
            "destinations": '|'.join(matrixRequest.destinations),
            "units": "imperial",
            "key": "",
            "travelMode": "DRIVING",
        }

        response = requests.request("GET", url, params=params)
        google_response = response.json()
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

    return google_response
