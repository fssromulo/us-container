from datetime import datetime, timezone, date, time
from decimal import Decimal
from typing import List, Optional, Union, Any
from uuid import UUID

def make_json_serializable(data: Any) -> Any:
    """
    Recursively converts objects that aren't JSON serializable into serializable formats.
    Currently handles:
    - UUID -> str
    - datetime -> ISO format str
    - date -> ISO format str
    - time -> ISO format str
    - Decimal -> float
    - Sets -> Lists
    
    Args:
        data: Any Python object that might contain non-serializable types
        
    Returns:
        The same data structure with all objects converted to JSON serializable types
    """
    # Handle None
    if data is None:
        return None
        
    # Handle UUID objects
    if isinstance(data, UUID):
        return str(data)
    
    # Handle datetime objects
    if isinstance(data, datetime):
        return data.isoformat()
    
    # Handle date objects
    if isinstance(data, date):
        return data.isoformat()
    
    # Handle time objects
    if isinstance(data, time):
        return data.isoformat()
        
    # Handle Decimal objects
    if isinstance(data, Decimal):
        return float(data)
    
    # Handle dictionaries
    if isinstance(data, dict):
        return {key: make_json_serializable(value) for key, value in data.items()}
    
    # Handle sets - convert to list
    if isinstance(data, set):
        return list(make_json_serializable(item) for item in data)
    
    # Handle lists and tuples
    if isinstance(data, (list, tuple)):
        return list(make_json_serializable(item) for item in data)
    
    # Return unchanged data for other types
    return data