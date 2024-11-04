from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"


@dataclass
class ServiceConfiguration:
    base_url: str
    port: int
    healthcheck: str
    prefix: str
    endpoints: Dict[HTTPMethod, List[str]]
    secret_key: str
    timeout: int


@dataclass
class GatewayConfiguration:
    services: Dict[str, ServiceConfiguration]
