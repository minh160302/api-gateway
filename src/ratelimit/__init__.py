from aioredis import Redis
from errors import RateLimitExceededError


LIMIT = 100
TTL = 5

async def check_rate_limit(redis_client: Redis, token: str):
    """
    Rate limit: default 600 requests in 10 seconds
    """    
    counter = await redis_client.get(token)
    if not counter:
        await redis_client.set(token, 0, ex=TTL)
    elif int(counter) >= LIMIT:
        raise RateLimitExceededError("Rate limit exceeded.")


async def endpoint_hit(redis_client: Redis, token: str):
    await redis_client.incrby(token, 1)
