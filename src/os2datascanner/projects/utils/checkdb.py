# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import structlog
import sys
import time
import pprint
from django.db import connections
from django.db.utils import OperationalError

logger = structlog.get_logger()


def waitdb(wait: int = 5):
    attempt = f"0/{wait}"
    for i in range(wait):
        attempt = f"{i+1:02d}/{wait:02d}"
        try:
            connections["default"].ensure_connection()
            logger.info("Connected to database", attempt=attempt)
            return 0
        except OperationalError:
            if i < wait - 1:
                time.sleep(1)

    logger.error("Giving up connecting to database", attempt=attempt)

    # dont log password
    censored = connections["default"].settings_dict
    censored.update({"password": "CENSORED"})
    logger.error(f"db settings:\n{pprint.pformat(censored)}")

    sys.exit(3)
