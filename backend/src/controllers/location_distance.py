# Pip imports
from fastapi import Depends

# Internal imports
from src.auth.auth import Auth0User
from src.crud.location_distance_crud import location_distance_crud
from src.dependencies import auth


async def delete_location_zip(zip_code: str, user: Auth0User = Depends(auth.get_user)):
    return await location_distance_crud.delete_by_destination_zip(zip_code)
