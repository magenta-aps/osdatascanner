import logging


"""Initialize the logger for os2datascanner

If you use os2ds from a script and wants to turn off logging, do

import logging
from os2datascanner.utils import log
log.init(logging.CRITICAL)
"""

def init(default_level=logging.INFO):
    """Set the log-level for the root datascanner logger
    """

    # stop spamming our logs
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("pika").setLevel(logging.ERROR)
    # pika still prints exception messages. Stop it!
    # https://docs.python.org/3/howto/logging.html#logging-flow
    logging.getLogger("pika").propagate = False

    fmt = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
    logging.basicConfig(format=fmt, datefmt='%Y-%m-%d %H:%M:%S')

    # get root logger. Normally we would do getLogger(__package__),
    # but __package__ resolve to os2datascanner.utils
    logger = logging.getLogger("os2datascanner")

    # read the log-level from the config file.
    try:
        from os2datascanner.utils import settings
        log_level = settings.log["log_level"]
    except AttributeError:
        logger.error("There is no [log] section in the config file.", exc_info=True)
        raise
    except ImportError:
        # most likely the OS2DS_@MODULE_USER_CONFIG_PATH env is not set
        # e.g. DS is imported from a script.
        log_level = default_level

    logger.setLevel(log_level)
