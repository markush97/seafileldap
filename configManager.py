
from functools import reduce

import logging
import yaml

from collections import namedtuple
from schema import Schema, SchemaError, Or, Optional

from interfaces.config import Config

config_schema = Schema({
    "seafile": {
        "username": str,
        "password": str,
        "server": str
    },
    "ldap": {
        "server": str,
        "people": str,
        "base": str
    }


})


class ConfigManager:
    def __init__(self, logger: logging.Logger, config):
        self.logger = logger
        with open(config) as f:
            config = yaml.load(f, Loader=yaml.SafeLoader)
            self.validateConfig(config)
            self.config = config

    def validateConfig(self, config): 
        try:
            config_schema.validate(config)
            self.logger.info('Configuration loaded sucessfully')

        except SchemaError as se:
            self.logger.error('Configuration is invalid. Exiting..')
            self.logger.error(se)
            exit(2)
