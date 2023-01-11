"""
Utility functions to support configuration through toml-files.
"""

import traceback
import logging
import os
import sys
import toml

logger = logging.getLogger(__name__)


def read_config(config_path):
    try:
        with open(config_path) as f:
            content = f.read()
    except FileNotFoundError:
        traceback.print_exc()
        sys.exit(5)
    try:
        return toml.loads(content)
    except toml.TomlDecodeError:
        traceback.print_exc()
        sys.exit(4)


def update_config(configuration, new_settings):
    # we cannot just do dict.update, because we do not want to "pollute" the
    # namespace with anything in *new_settings*, just the variables defined in
    # **configuration**.
    for key in new_settings:
        if key in configuration:
            if isinstance(configuration[key], dict):
                update_config(configuration[key], new_settings[key])
            else:
                configuration[key] = new_settings[key]
        else:
            logger.warning("Invalid key in config: %s", key)


def update_from_env(configuration, traversed_path=None):

    if traversed_path is None:
        traversed_path = []

    for key in configuration:
        if isinstance(configuration[key], dict):
            update_from_env(configuration[key], traversed_path + [key])
        else:
            env_var = "__".join(traversed_path + [key])
            if os.environ.get(env_var) is not None:
                configuration[key] = os.environ.get(env_var)


def get_3_layer_config(default_settings, sys_var, user_var):
    # Specify file paths
    system_settings = os.getenv(sys_var, None)
    user_settings = os.getenv(user_var, None)

    # Load default configuration
    if not os.path.isfile(default_settings):
        logger.error("Invalid file path for default settings: %s",
                     default_settings)
        sys.exit(1)

    config = read_config(default_settings)
    # Load system configuration
    if system_settings:
        logger.info("Reading system config from %s", system_settings)
        update_config(config, read_config(system_settings))
    # Load user configuration
    if user_settings:
        logger.info("Reading user settings from %s", user_settings)
        update_config(config, read_config(user_settings))

    # Load environment configuration
    update_from_env(config)

    return config
