import structlog
import os

from enum import Enum

from os2datascanner.utils.toml_configuration import get_3_layer_config

logger = structlog.get_logger("utils")


class OS2DSModule(Enum):
    ADMIN = ('admin',)
    ENGINE = ('engine',)
    REPORT = ('report',)

    @classmethod
    def determine_OS2DS_module(cls):
        # TODO: Consider a more elegant way to determine this
        for component, indicator in (
                (cls.REPORT, "OS2DS_REPORT_USER_CONFIG_PATH"),
                (cls.ADMIN, "OS2DS_ADMIN_USER_CONFIG_PATH"),

                # An engine config file is ~always available, so check for it
                # last
                (cls.ENGINE, "OS2DS_ENGINE_USER_CONFIG_PATH")):
            if os.getenv(indicator):
                return component
        raise LookupError

    def __init__(self, _):
        self.sys_var = f"OS2DS_{self.name}_SYSTEM_CONFIG_PATH"
        self.user_var = f"OS2DS_{self.name}_USER_CONFIG_PATH"


def _get_default_settings_path(OS2DS_module):
    project_dir = os.path.abspath(
        os.path.dirname(
            os.path.dirname(__file__)
        )
    )
    path = project_dir
    if OS2DS_module == OS2DSModule.ENGINE:
        path = os.path.join(project_dir, 'engine2')
    elif OS2DS_module == OS2DSModule.ADMIN:
        path = os.path.join(project_dir, 'projects', 'admin')
    elif OS2DS_module == OS2DSModule.REPORT:
        path = os.path.join(project_dir, 'projects', 'report')
    return os.path.join(path, 'default-settings.toml')


def _get_config(key=None):
    OS2DS_module = OS2DSModule.determine_OS2DS_module()
    default_settings = _get_default_settings_path(OS2DS_module)
    config = get_3_layer_config(default_settings,
                                sys_var=OS2DS_module.sys_var,
                                user_var=OS2DS_module.user_var)
    if key:
        config = config[key]
    return config


_config = _get_config('amqp')
AMQP_HOST = _config['AMQP_HOST']
AMQP_USER = _config['AMQP_USER']
AMQP_PWD = _config['AMQP_PWD']
AMQP_SCHEME = _config['AMQP_SCHEME']
AMQP_PORT = _config['AMQP_PORT']
AMQP_HEARTBEAT = _config['AMQP_HEARTBEAT']
AMQP_VHOST = _config['AMQP_VHOST']
AMQP_BACKOFF_PARAMS = _config.get('AMQP_BACKOFF_PARAMS', {})
