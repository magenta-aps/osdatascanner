from typing import Optional
import datetime
from dateutil.parser import parse
from dateutil.tz import gettz


def make_datetime_aware(
        d: Optional[datetime.datetime],
        local: bool = False) -> Optional[datetime.datetime]:
    """Returns a timezone-aware timestamp, either relative to UTC (by default)
    or to the system's local timezone. (If the input timestamp is already
    timezone-aware, then it'll just be returned.)"""
    return (d.replace(
                    tzinfo=datetime.timezone.utc
                    if not local
                    else gettz())
            if d and (not d.tzinfo or d.tzinfo.utcoffset(d) is None)
            else d)


def parse_datetime(val: str, local: bool = False) -> datetime.datetime:
    """Parses an input string as though with dateutil.parser.parse, and returns
    a datetime.datetime guaranteed to be timezone-aware.

    If the local flag is not specified or is False, then UTC will be used as
    the default fallback timezone; if it's True, then the system's local
    timezone will be used instead."""
    return make_datetime_aware(parse(val), local)


DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def unparse_datetime(d: datetime.datetime) -> str:
    return make_datetime_aware(d).strftime(DATE_FORMAT)


# Since you ask, this is one second before the day the first digital computer
# (ENIAC) was first used in production
NOT_SCANNED_DT: datetime.datetime = parse_datetime("1945-12-09T23:59:59-05:00")
"""A special tag timestamp used to indicate that an object's content (as
opposed to its metadata) has not been scanned by OSdatascanner."""
