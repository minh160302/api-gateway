from typing import Dict

from pydantic_settings import BaseSettings

from models import GatewayConfiguration


class Settings(BaseSettings):
    GwConfig: GatewayConfiguration = GatewayConfiguration(services={})
    endpoint_mappings: Dict[str, str] = dict()


settings = Settings()
