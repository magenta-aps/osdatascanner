import logging
import os
from pathlib import Path
from enum import Enum
from os2datascanner.utils.toml_configuration import get_3_layer_config

logger = logging.getLogger(__name__)

"""read the settings for the different components of datascanner

by checking if any of the `ADMIN`, `ENGINE` or `REPORT` environment variable is
set, in this order. Thus, only set one of the env's.
"""

_ERROR_MSG = "OS2DS_{MODULE_NAME}_USER_CONFIG_PATH not set"


class OS2DSModule(Enum):
    ADMIN = ("admin",)
    ENGINE = ("engine",)
    REPORT = ("report",)
    SERVER = ("server",)

    @classmethod
    def determine_OS2DS_module(cls):
        # TODO: Consider a more elegant way to determine this
        if os.getenv("OS2DS_ADMIN_USER_CONFIG_PATH"):
            return cls.ADMIN
        elif os.getenv("OS2DS_ENGINE_USER_CONFIG_PATH"):
            return cls.ENGINE
        elif os.getenv("OS2DS_REPORT_USER_CONFIG_PATH"):
            return cls.REPORT
        elif os.getenv("OS2DS_SERVER_USER_CONFIG_PATH") or os.getenv(
            "OS2DS_SERVER_SYSTEM_CONFIG_PATH"
        ):
            return cls.SERVER
        else:
            raise ValueError(_ERROR_MSG)

    def __init__(self, _):
        self.sys_var = f"OS2DS_{self.name}_SYSTEM_CONFIG_PATH"
        self.user_var = f"OS2DS_{self.name}_USER_CONFIG_PATH"


def _get_default_settings_path(OS2DS_module):
    # abs path of src/os2datascanner
    path = Path(__file__).parents[1].resolve()

    # get module specific path
    if OS2DS_module == OS2DSModule.ENGINE:
        path = path / "engine2"
    elif OS2DS_module == OS2DSModule.ADMIN:
        path = path / "projects/admin"
    elif OS2DS_module == OS2DSModule.REPORT:
        path = path / "projects/report"
    elif OS2DS_module == OS2DSModule.SERVER:
        path = path / "server"

    return path / "default-settings.toml"


def get_config(key=None):
    OS2DS_module = OS2DSModule.determine_OS2DS_module()
    try:
        sys_var = OS2DS_module.sys_var
        user_var = OS2DS_module.user_var
    except:
        sys_var = ""
        user_var = ""
        logger.warning(f"sys_var and/or user_var not set ")

    default_settings_path = _get_default_settings_path(OS2DS_module)
    config = get_3_layer_config(
        default_settings_path, sys_var=sys_var, user_var=user_var
    )

    if key:
        try:
            config = config[key]
        except KeyError as e:
            raise ValueError(f"Error during loading of settings: [{key}]") from e
    config["default_settings_path"] = default_settings_path
    return config


# NEVER print or log the config object, as it will expose secrets
# Only ever print or log explicitly chosen (and safe!) settings!
_config = get_config()
for key, value in _config.items():
    if not key.startswith("_"):
        # NB! Never log the value for an unspecified key!
        if isinstance(value, list):
            logger.debug(f"Converting list value to tuple for [{key}]")
            value = tuple(value)
        logger.info(f"Adding setting: [{key}]")
        globals()[key] = value


del key, value, _config
del logger, logging
