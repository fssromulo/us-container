
# Python imports
import logging
import os
import random

# Pip imports
from fastapi import HTTPException, status
from tortoise import Model
from tortoise.exceptions import DoesNotExist
from tortoise import Tortoise
from typing import Any

# Internal imports
from src.schemas.quote_searches import QuoteSearchesOut, QuoteSearchesIn
from src.crud.quote_searches_crud import quote_searches_crud
from src.auth.auth import Auth0User

async def create_quote_searches(quote_searches: QuoteSearchesIn) -> Model:
    saved_quote_searches = await quote_searches_crud.create(quote_searches)
    return saved_quote_searches

async def get_by_count(date1=None, date2=None, timezone=None, selected_user_id='ALL') -> Any:
    if not date1 and selected_user_id == 'ALL':
        query = """
            SELECT 
                postal_code, 
                COUNT(postal_code) AS occurrences,
                ARRAY_AGG(DISTINCT usr.first_name || ' ' || usr.last_name) AS users
            FROM 
                quote_searches qs
            INNER JOIN 
                users usr ON CAST(qs.user_id AS VARCHAR) = CAST(usr.id AS VARCHAR)
            GROUP BY postal_code
            ORDER BY occurrences DESC
            LIMIT 10
            """
    elif selected_user_id == 'ALL':
        query = f"""
            SELECT 
                postal_code, 
                COUNT(postal_code) AS occurrences,
                ARRAY_AGG(DISTINCT usr.first_name || ' ' || usr.last_name) AS users
            FROM 
                quote_searches qs
            INNER JOIN 
                users usr ON CAST(qs.user_id AS VARCHAR) = CAST(usr.id AS VARCHAR)
            WHERE qs.created_at >= (TO_TIMESTAMP({date1}) AT TIME ZONE '{timezone}')::DATE AND qs.created_at <= (TO_TIMESTAMP({date2}) AT TIME ZONE '{timezone}')::DATE
            GROUP BY postal_code
            ORDER BY occurrences DESC
            LIMIT 10
            """
    elif not date1 and selected_user_id != 'ALL':
        query = f"""
            SELECT 
                postal_code, 
                COUNT(postal_code) AS occurrences,
                ARRAY_AGG(DISTINCT usr.first_name || ' ' || usr.last_name) AS users
            FROM 
                quote_searches qs
            INNER JOIN 
                users usr ON CAST(qs.user_id AS VARCHAR) = CAST(usr.id AS VARCHAR)
            WHERE qs.user_id = '{selected_user_id}'
            GROUP BY postal_code
            ORDER BY occurrences DESC
            LIMIT 10
            """
    else:
        query = f"""
            SELECT 
                postal_code, 
                COUNT(postal_code) AS occurrences,
                ARRAY_AGG(DISTINCT usr.first_name || ' ' || usr.last_name) AS users
            FROM 
                quote_searches qs
            INNER JOIN 
                users usr ON CAST(qs.user_id AS VARCHAR) = CAST(usr.id AS VARCHAR)
            WHERE qs.created_at >= (TO_TIMESTAMP({date1}) AT TIME ZONE '{timezone}')::DATE AND qs.created_at <= (TO_TIMESTAMP({date2}) AT TIME ZONE '{timezone}')::DATE
                AND qs.user_id = '{selected_user_id}'
            GROUP BY postal_code
            ORDER BY occurrences DESC
            LIMIT 10
            """

    results = await Tortoise.get_connection("default").execute_query(query)
    return results

async def get_quote_searches(user: Auth0User, date1=None, date2=None, timezone=None, selected_user_id='ALL') -> Model:
    if not date1:
        searches = await get_by_count()
    else:
        if date1 == date2:
            date1 = date2 = None
        searches = await get_by_count(date1, date2, timezone, selected_user_id)
    
    return searches[1]