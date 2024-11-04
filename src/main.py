import sys
from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from config import settings
from errors import IncorrectRouteError, OnStartUpError
from models import GatewayConfiguration
from routing import route_request
from utils import utils


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # Init Gateway configuration
        config: GatewayConfiguration = utils.parse_config_file(
            '/Users/nguyencanhminh/Downloads/code/infra/api-gateway/conf/gateway-conf.yml')
        # save into settings for global usage
        # TODO: sort for subsequent matchings
        # TODO: healthcheck before making connection
        settings.GwConfig = config
        for name, service in config.services.items():
            settings.endpoint_mappings[service.prefix] = name
        # Application startup
        yield
        # TODO: Application shutdown
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
        response = await route_request(settings.GwConfig, settings.endpoint_mappings, request)
        content = response.json() if response.headers.get(
            "content-type") == "application/json" else response.text
        return JSONResponse(status_code=response.status_code, content=content, headers=response.headers)
    except IncorrectRouteError as exc:
        return JSONResponse(status_code=HTTPStatus.NOT_FOUND, content={'reason': str(exc)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
