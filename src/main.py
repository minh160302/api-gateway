import sys
from contextlib import asynccontextmanager
from http import HTTPStatus

from aioredis import Redis
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

import ratelimit
import routing
from config import settings
from errors import IncorrectRouteError, OnStartUpError, RateLimitExceededError
from models import GatewayConfiguration, database, redis
from utils import utils

import asyncio
from typing import Dict

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Application startup
        # 1.  Init Gateway configuration
        config: GatewayConfiguration = utils.parse_config_file(
            '/Users/nguyencanhminh/Downloads/code/infra/api-gateway/conf/gateway-conf.yml')
        # 2. save into settings for global usage
        # TODO: sort for subsequent matchings
        # TODO: healthcheck before making connection
        settings.GwConfig = config
        for name, service in config.services.items():
            settings.endpoint_mappings[service.prefix] = name

        # 3. Create database for persistent API infos
        await database.init()
        app.state.redis = await redis.init()
        
        # Dictionary to hold queues for each token
        queues: Dict[str, asyncio.Queue] = {}
        app.state.request_queues = queues
        ###########
        yield
        ###########
        # Application shutdown
        await database.destroy()
    except OnStartUpError as exc:
        print("OnStartUpError", exc)
        sys.exit(1)


app = FastAPI(lifespan=lifespan)
app.debug = True


"""
TODO: 
- validate input file
- Encode/Decode with API key?
- Save things in SQLite, which includes:
    - api key/hash/sth to identify
- API calls tracing
- Redis to save hit counter
- Circuit breaker?
"""


# Authentication example
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    token: str = request.headers.get('Authorization')
    if token != "your-secret-token":
        return JSONResponse(status_code=HTTPStatus.UNAUTHORIZED, content={'reason': "Unauthorized"})

    try:
        redis_client: Redis = app.state.redis
        
        # Rate Limit
        await ratelimit.check_rate_limit(redis_client, token)        
        await ratelimit.endpoint_hit(redis_client, token)

        
        response = await routing.route_request(settings.GwConfig, settings.endpoint_mappings, request)
        content = response.json() if response.headers.get(
            "content-type") == "application/json" else response.text

        return JSONResponse(status_code=response.status_code, content=content, headers=response.headers)
    except IncorrectRouteError as exc:
        return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={'reason': str(exc)})
    except RateLimitExceededError as exc:
        return JSONResponse(status_code=HTTPStatus.TOO_MANY_REQUESTS, content={'reason': str(exc)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
