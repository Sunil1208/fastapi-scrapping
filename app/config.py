import yaml


def load_config():
    with open("app/config.yaml", "r") as config_file:
        return yaml.safe_load(config_file)


config = load_config()
TOKEN = config["token"]
BASE_URL = config["base_url"]
