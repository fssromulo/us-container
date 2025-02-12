
# Pip imports
from fastapi import APIRouter, Depends, status

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import country
from src.dependencies import auth
from src.schemas.country import countryOut, countryIn

router = APIRouter(
    tags=["country"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

@router.post("/country", response_model=countryOut)
async def create_country(country_in: countryIn, user: Auth0User = Depends(auth.get_user)):
    return await country.create_country(country_in, user)

@router.get("/countries")
async def create_country(user: Auth0User = Depends(auth.get_user)):
    return await country.fetch_countries(user)
