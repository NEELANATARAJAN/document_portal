import yaml
import os
from logger import GLOBAL_LOGGER as log

print(f"os.getcwd(): {os.getcwd()} ")
def load_config(config_path: str="./config/config.yaml") -> dict:
    with open(config_path, "r") as file:
        config=yaml.safe_load(file)
    log.info(config)
    return config

load_config("./config/config.yaml")
