from django.core.cache import cache
from functools import wraps

CACHE_TTL = 60 * 5  # 5 minutes default
USER_TTL = 60 * 15  # 15 minutes for user data


def cache_api_response(key_prefix, ttl=CACHE_TTL):
    """
    Decorator for caching API responses
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from prefix and arguments
            cache_key = f"{key_prefix}:{':'.join(args[1:])}"
            print('cache key', cache_key)
            result = await cache.aget(cache_key)
            if result is None:
                result = await func(*args, **kwargs)
                if result: 
                    await cache.aset(cache_key, result, ttl)
            else:
                print('cache hit', cache_key)
            return result
        return wrapper
    return decorator

