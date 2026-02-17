# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from datetime import datetime, timezone, timedelta


from os2datascanner.engine2.utilities.datetime import parse_datetime


def seconds_to_tz(sec):
    return timezone(timedelta(seconds=sec))


class TestMessages:

    @pytest.mark.parametrize("string, timestamp", [
        ("2020-01-01T04:13:16-04:00", datetime(
                2020, 1, 1, 4, 13, 16, tzinfo=seconds_to_tz(-14400))),
        ("2020-01-01T04:13:16-0230", datetime(
                2020, 1, 1, 4, 13, 16, tzinfo=seconds_to_tz(-9000))),
        ("2020-01-01T04:13:16Z", datetime(
                2020, 1, 1, 4, 13, 16, tzinfo=timezone.utc)),
        ("2020-01-01T04:13:16+0000", datetime(
                2020, 1, 1, 4, 13, 16, tzinfo=timezone.utc)),
        ("2020-01-01T04:13:16+00:00", datetime(
                2020, 1, 1, 4, 13, 16, tzinfo=timezone.utc)),
        ("2020-01-01T04:13:16+01:00", datetime(
                2020, 1, 1, 4, 13, 16, tzinfo=seconds_to_tz(3600))),
        ("2020-01-01T04:13:16+0230", datetime(
                2020, 1, 1, 4, 13, 16, tzinfo=seconds_to_tz(9000))),
        ("2020-01-01T04:13:16+04:00", datetime(
                2020, 1, 1, 4, 13, 16, tzinfo=seconds_to_tz(14400)))
    ])
    def test_parse_isoformat(self, string, timestamp):
        assert parse_datetime(string) == timestamp
