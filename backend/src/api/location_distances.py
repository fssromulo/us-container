# # Python imports
from typing import List

# # Pip imports
from fastapi import APIRouter, Depends, status

# # Internal imports
from src.auth.auth import Auth0User
from src.controllers import location_distance
from src.dependencies import auth


router = APIRouter(tags=["location_distance"], dependencies=[Depends(auth.implicit_scheme)])


@router.delete(
    "/location_distance/{zip_code}",
)
async def delete_location_zip(
    zip_code: str, user: Auth0User = Depends(auth.get_user)
):
   return await location_distance.delete_location_zip(zip_code, user)
