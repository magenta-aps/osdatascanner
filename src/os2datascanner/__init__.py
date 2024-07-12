from .utils import log_levels  # noqa

import os
from . import engine2  # noqa

__version__ = "3.24.0"
__commit__ = os.getenv("COMMIT_SHA", "")
__tag__ = os.getenv("COMMIT_TAG", __version__)
__branch__ = os.getenv("CURRENT_BRANCH", "main")
