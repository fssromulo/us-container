# Pip imports
from tortoise import Model

# Internal imports
from src.auth.auth import Auth0User
from src.crud.rental_history_crud import rental_history_crud

# interal imports
from src.schemas.rental_history import RentalHistoryIn, RentalHistoryUpdate


async def create_rental_history(rental_history: RentalHistoryIn, user: Auth0User) -> Model:
    saved_rental_history = await rental_history_crud.create(rental_history)
    return saved_rental_history


async def update_rental_history(id: str, rental_history: RentalHistoryUpdate) -> Model:
    saved_rental_history = await rental_history_crud.update(id, rental_history)
    return saved_rental_history
