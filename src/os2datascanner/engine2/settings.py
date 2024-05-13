import structlog
from pathlib import Path
import logging.config

from os2datascanner.utils.toml_configuration import get_3_layer_config
from os2datascanner.utils.log_levels import log_levels  # noqa
from structlog.processors import CallsiteParameter

logger = structlog.get_logger()

# NEVER print or log the config object, as it will expose secrets
# Only ever print or log explicitly chosen (and safe!) settings!
for key, value in get_3_layer_config(
        Path(__file__).parent.joinpath("default-settings.toml"),
        "OS2DS_ENGINE_SYSTEM_CONFIG_PATH",
        "OS2DS_ENGINE_USER_CONFIG_PATH").items():
    if not key.startswith('_'):
        # NB! Never log the value for an unspecified key!
        if isinstance(value, list):
            logger.debug("converting list value to tuple for", setting=key)
            value = tuple(value)
        logger.debug("adding setting!", setting=key)
        globals()[key] = value

del key, Path, value, logger, get_3_layer_config

LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            "json": {
                "()": "structlog.stdlib.ProcessorFormatter",
                "processor": structlog.processors.JSONRenderer(),
            },
            "console": {
                "()": "structlog.stdlib.ProcessorFormatter",
                "processor": structlog.dev.ConsoleRenderer(),
            },
            "key_value": {
                "()": "structlog.stdlib.ProcessorFormatter",
                "processor": structlog.processors.KeyValueRenderer(key_order=[
                    'timestamp',
                    'level',
                    'event',
                    'logger',
                ]),
            },
            'verbose': {
                'format': (
                    '%(levelname)s %(asctime)s %(module)s %(process)d '
                    '%(thread)d %(message)s'
                ),
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'handlers': {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "console",
            },
        },
        'root': {
            'handlers': ['console'],
            'level': globals()['LOG_LEVEL'],
            'propagate': True,
        },
        'loggers': {
            'os2datascanner': {
                'handlers': ['console'],
                'level': globals()['LOG_LEVEL'],
                'propagate': True,
            },
        }
    }


# Use the configuration above.
logging.config.dictConfig(LOGGING)

# pika is very loud
logging.getLogger("pika").setLevel(logging.WARNING)

# Configure log level trace
structlog.stdlib.TRACE = TRACE = 2
structlog.stdlib._NAME_TO_LEVEL['trace'] = TRACE
structlog.stdlib._LEVEL_TO_NAME[TRACE] = 'trace'


def trace(self, msg, *args, **kw):
    return self.log(TRACE, msg, *args, **kw)


# Set above method as the logger.trace()
structlog.stdlib.BoundLogger.trace = trace

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        # Includes module and function name in log messages.
        structlog.processors.CallsiteParameterAdder(
            [CallsiteParameter.MODULE,
             CallsiteParameter.FUNC_NAME],
        ),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,

    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
