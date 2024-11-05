from json import JSONDecodeError
from typing import Dict

import httpx
from fastapi import Request

from errors import IncorrectRouteError
from models import GatewayConfiguration, redis

async def ping_healthcheck():
    pass


async def route_request(GwConfig: GatewayConfiguration, endpoint_mappings: Dict[str, str], request: Request):
    try:
        print("-------PARSE REQUEST INFO-------")
        print(GwConfig)
        # Parameters
        path: str = request.url.path

        # Route
        route_prefix_lst = ['/']
        i = 1
        while i < len(path) and path[i] != '/':
            route_prefix_lst.append(path[i])
            i += 1
        route_prefix = ''.join(route_prefix_lst)
        route_path = path[i:]
        print(route_prefix)

        # Payload
        payload = None
        try:
            payload = await request.json()
        except JSONDecodeError:
            payload = None
        print("--------------")

        # Assertion
        assert route_prefix in endpoint_mappings
        service = GwConfig.services[endpoint_mappings[route_prefix]]
        assert service.prefix == route_prefix

        # Send request to service
        client = httpx.AsyncClient()
        # print(service.base_url + ":" + str(service.port) + route_path)
        target_url = service.base_url + ":" + str(service.port) + route_path
        response = await client.request(
            method=request.method,
            cookies=request.cookies,
            json=payload,
            headers=request.headers,
            params=request.query_params,
            url=target_url,
            timeout=service.timeout,
            follow_redirects=True
        )

        # Fix bug: h11._util.LocalProtocolError: Too little data for declared Content-Length
        if 'content-length' in response.headers:
            del response.headers['content-length']
                    
        return response

    except AssertionError:
        raise IncorrectRouteError(
            "Incorrect route prefix.")
