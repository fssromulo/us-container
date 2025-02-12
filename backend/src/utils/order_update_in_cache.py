# Python imports
import json
from datetime import datetime
from decimal import Decimal
from uuid import UUID

# Internal imports
import redis
from src.config import settings
from loguru import logger


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {self.default(key): self.default(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.default(item) for item in obj]
        else:
            return super().default(obj)



def clear_cache(statuses, order_type, user_ids, account_id):
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
    
    for status in statuses:
        for user_id in user_ids:
            redis_key = f"{str(user_id)}:{order_type}:{account_id}:order:{status}"
            r.delete(redis_key)
            redis_key = f"{str(user_id)}:ALL:{account_id}:order:{status}"
            r.delete(redis_key)
        redis_key = f"{order_type}:{account_id}:order:{status}"
        r.delete(redis_key)
        redis_key = f"ALL:{account_id}:order:{status}"
        r.delete(redis_key)


def _update_redis_cache(redis_key, new_line_items, action="remove"):
    """
    Helper function to update Redis cache for a specific key
    action: "remove", "append", or "swap"
    """
    r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
    cached_value = r.get(redis_key)
    
    if not cached_value:
        return

    order_cached = json.loads(cached_value)
    order_id = new_line_items[0]['order_display_order_id']
    
    if action == "remove":
        order_result = [item for item in order_cached['orders'] 
                       if item['order_display_order_id'] != order_id]
        logger.info(f"(old status) removing order id {order_id} from {redis_key}")
        result = {"orders": order_result, "count": len(order_result)}
    
    elif action == "append":
        order_cached['orders'] = new_line_items + order_cached['orders']
        logger.info(f"(new status) adding order id {order_id} to {redis_key}")
        result = order_cached
    
    else:  # swap
        order_result = [item for item in order_cached['orders'] 
                       if item['order_display_order_id'] != order_id]
        order_result = new_line_items + order_result
        logger.info(f"(same status) adding order id {order_id} to {redis_key}")
        result = {"orders": order_result, "count": len(order_result)}

    r.set(redis_key, json.dumps(result, cls=CustomJSONEncoder))

def _get_redis_keys(status, order_type, account_id, user_ids=None):
    """Generate Redis keys for given parameters"""
    status = status.replace(" ", "_")
    keys = [f"{order_type}:{account_id}:order:{status}"]
    
    if user_ids:
        keys.extend([
            f"{str(user_id)}:{order_type}:{account_id}:order:{status}"
            for user_id in user_ids
        ])
    
    return keys

def swap_cache(new_statuses, old_statuses, swap_statuses, new_line_items, 
               order_type, user_ids, account_id):
    """
    Update Redis cache when order statuses change
    """
    # Remove from old status caches
    for status in old_statuses:
        for redis_key in _get_redis_keys(status, order_type, account_id, user_ids):
            _update_redis_cache(redis_key, new_line_items, action="remove")

    # Add to new status caches
    for status in new_statuses:
        for redis_key in _get_redis_keys(status, order_type, account_id, user_ids):
            _update_redis_cache(redis_key, new_line_items, action="append")

    # Update swap status caches
    for status in swap_statuses:
        for redis_key in _get_redis_keys(status, order_type, account_id, user_ids):
            _update_redis_cache(redis_key, new_line_items, action="swap")
            
