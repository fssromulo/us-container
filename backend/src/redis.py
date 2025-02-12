import redis

client = redis.Redis(host="redis-server")

def limiter(key:str, limit:int, ttl):
    """
    A function that limits the number of calls a user can make to an endpoint in a minute.

    Args:
        key (str): The key to use for the Redis cache.
        limit (int): The maximum number of calls allowed in {ttl}.
        ttl (int): The time to live for each call

    Returns:
        dict: A dictionary with the following keys:
            call: Whether the call was allowed.
            ttl: The remaining time to live for the key.
    """
    req = client.incr(key)
    if req == 1:    
        client.expire(key, ttl)
        ttl = ttl
    else:
        ttl = client.ttl(key)

    if req > limit:
        return{
            "call": False,
            "ttl":ttl
        }
    else:
        return {
            "call": True,
            "ttl": ttl
        }