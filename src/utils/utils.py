import yaml

from errors import OnStartUpError
from models import GatewayConfiguration, ServiceConfiguration


def parse_config_file(filename: str) -> GatewayConfiguration:
    """
    Parse YAML Gateway configuration file
    """
    try:
        with open(filename) as stream:
            try:
                parsed_GW = GatewayConfiguration(**yaml.safe_load(stream))
                for name, service in parsed_GW.services.items():
                    parsed_GW.services[name] = ServiceConfiguration(**service)
                return parsed_GW
            except yaml.YAMLError as exc:
                print("Incorrect configuration file format. Caused by: " + str(exc))
                raise OnStartUpError(
                    "Incorrect configuration file format. Caused by: " + str(exc))
    except FileNotFoundError:
        print("Configuration file not found.")
        raise OnStartUpError("Configuration file not found.")


# config = parse_config_file("conf/gateway-con.yml")
# print(config)
# # print("services:", config.services)
