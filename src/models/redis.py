import os

import aioredis
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.


async def init():
    redis = await aioredis.Redis(
        host=os.environ.get("REDIS_SERVER"),
        port=int(os.environ.get("REDIS_PORT")),
        decode_responses=True
    )
    return redis
