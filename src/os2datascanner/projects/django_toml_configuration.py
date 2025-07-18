"""
Utility functions to support configuration through toml-files for Django.
"""

import os
import sys
import structlog

from django.utils.translation import gettext_lazy as _
from os2datascanner.utils.toml_configuration import get_3_layer_config

# For some reason this doesn't produce logs, if you're using __name__
logger = structlog.get_logger("django_toml_configuration")


def _process_relative_path(placeholder, replacement_value, path_list):
    if path_list and path_list[0] == placeholder:
        path_list[0] = replacement_value
    return os.path.join(*path_list)


def _set_constants(module, configuration):
    # NEVER print or log the config object, as it will expose secrets
    # Only ever print or log explicitly chosen (and safe!) settings!
    for key, value in configuration.items():
        if key.startswith("_"):
            logger.info("skipping", setting=key)
        elif key.isupper():
            # NB! Never log the value for an unspecified key!
            if isinstance(value, list):
                logger.debug("Converting list value to tuple for", setting=key)
                value = tuple(value)
            logger.debug("adding setting!", setting=key)
            setattr(module, key, value)
        else:
            logger.error("setting is not a valid Django setting!", setting=key)


def _process_directory_configuration(configuration, placeholder, directory):
    directories = configuration.pop("dirs", None)
    if not directories:
        logger.error(
            "the configuration is missing the required list of directories."
        )
        sys.exit(1)
    for key, value in directories.items():
        if configuration.get(key):
            logger.error("the directory has already been configured!", directory=key)
            sys.exit(1)
        else:
            configuration[key] = _process_relative_path(
                placeholder, directory, value
            )


def _process_locales(configuration, placeholder, directory):
    # Set locale paths
    path_list = configuration.pop('_LOCALE_PATHS', None)
    if path_list:
        configuration['LOCALE_PATHS'] = [
            _process_relative_path(placeholder, directory, path) for path in path_list
        ]
    # Set languages and their localized names
    language_list = configuration.pop('_LANGUAGES', None)
    if language_list:
        configuration['LANGUAGES'] = [
            (language[0], _(language[1])) for language in language_list
        ]


def process_toml_conf_for_django(parent_path, module, sys_var, user_var):
    # Specify file paths
    settings_dir = os.path.abspath(os.path.dirname(module.__file__))
    default_settings = os.path.join(settings_dir, 'default-settings.toml')

    config = get_3_layer_config(default_settings, sys_var, user_var)

    _process_directory_configuration(config, "*", parent_path)
    _process_locales(config, "*", parent_path)
    # Must come before _set_constants
    # Prepend our apps (so their templates have priority):
    # NB! Only needs to be conditional until report module is updated as well
    if config.get('OS2DATASCANNER_APPS'):
        config['INSTALLED_APPS'] = config['OS2DATASCANNER_APPS'] + config['INSTALLED_APPS']
    # Append optional apps - if any:
    if config.get('OPTIONAL_APPS'):
        config['INSTALLED_APPS'] += config['OPTIONAL_APPS']
    if config.get("OPTIONAL_MIDDLEWARE"):
        config['MIDDLEWARE'] += config['OPTIONAL_MIDDLEWARE']

    _set_constants(module, config)
