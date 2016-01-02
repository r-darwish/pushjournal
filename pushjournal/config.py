import click
import yaml

class ConfigError(click.ClickException):
    pass


def load(config):
    with open(config, "r") as f:
        config = yaml.load(f)

    if not config:
        raise ConfigError("You configuration is empty")

    return config
