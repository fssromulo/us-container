
# Pip imports
from fastapi import APIRouter, Depends, status

# Internal imports
from src.auth.auth import Auth0User
from src.controllers import quote_searches
from src.dependencies import auth
from src.schemas.quote_searches import QuoteSearchesOut, QuoteSearchesIn
from typing import Dict, List, Any

router = APIRouter(
    tags=["quote_searches"],
    dependencies=[Depends(auth.implicit_scheme)],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

@router.post("/quote_searches", response_model=QuoteSearchesOut)
async def create_quote_searches(quote_searches_in: QuoteSearchesIn):
    return await quote_searches.create_quote_searches(quote_searches_in)

@router.get("/quote_searches")
async def get_quote_searches(date1: Any = None, date2: Any = None, timezone: str = None, selected_user_id: str = 'ALL', user: Auth0User = Depends(auth.get_user)):
    return await quote_searches.get_quote_searches(user, date1, date2, timezone, selected_user_id)
