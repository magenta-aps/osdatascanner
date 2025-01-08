"""Convenience imports for using OS2datascanner interactively. (Note that the
shell_plus management command of the two Django projects has been configured to
import everything from this file by default.)"""
# flake8: noqa

from os2datascanner.engine2._interactive import *
from os2datascanner.utils.system_utilities import time_now
import os2datascanner.engine2.rules.logical_operators
