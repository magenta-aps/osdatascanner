import logging

from os2datascanner.utils import settings

"""This initialize the logger for os2datascanner,

If you use os2ds from a script, use it like
  from os2datascanner.utils import log
  log.init()

"""


def init():
    # stop spamming our logs
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("pika").setLevel(logging.ERROR)
    # pika still prints exception messages. Stop it!
    # https://docs.python.org/3/howto/logging.html#logging-flow
    logging.getLogger("pika").propagate = False

    # get root logger
    # __package__ resolve to os2datascanner.utils
    logger = logging.getLogger("os2datascanner")

    # read the log-level from the config file.
    try:
        log_level = settings.log["log_level"]
    except AttributeError as e:
        logger.error("There is no [log] section in the config file.")
        raise

    # set log level (it is not enough to set the level for the handler below)
    logger.setLevel(log_level)
    # create console handler
    ch = logging.StreamHandler()
    # XXX set log level (does this matter?)
    ch.setLevel(log_level)

    # add formatter
    formatter = logging.Formatter(
        "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
