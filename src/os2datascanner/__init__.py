# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from .utils import log_levels  # noqa

import os
from . import engine2  # noqa

__version__ = "3.31.3"
__commit__ = os.getenv("COMMIT_SHA", "")
__tag__ = os.getenv("COMMIT_TAG", __version__)
__branch__ = os.getenv("CURRENT_BRANCH", "main")
