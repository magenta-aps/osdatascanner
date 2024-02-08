import pytest
import datetime

from os2datascanner.utils.system_utilities import time_now
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner import Scanner
from os2datascanner.projects.admin.adminapp.models.rules import CustomRule
from os2datascanner.projects.admin.tests.test_utilities import dummy_rule_dict

from os2datascanner.projects.admin.adminapp.management.commands.cron import should_scanner_start


@pytest.mark.django_db
class TestCron:

    @classmethod
    def setup_method(cls):
        rule = CustomRule.objects.create(**dummy_rule_dict)
        cls.scanner_daily = Scanner.objects.create(
            name="test", schedule="RRULE:FREQ=DAILY;", rule=rule)

    def test_schedule_time_19_00(self, monkeypatch):
        # Arrange
        time = time_now().replace(hour=19, minute=0)
        monkeypatch.setattr(Scanner, "schedule_datetime", time)

        current_qhr = time
        next_qhr = current_qhr + datetime.timedelta(minutes=15)

        # Act
        start = should_scanner_start(self.scanner_daily, current_qhr, next_qhr)

        # Assert
        assert start is True

    def test_schedule_time_20_15(self, monkeypatch):
        # Arrange
        time = time_now().replace(hour=20, minute=15)
        monkeypatch.setattr(Scanner, "schedule_datetime", time)

        current_qhr = time
        next_qhr = current_qhr + datetime.timedelta(minutes=15)

        # Act
        start = should_scanner_start(self.scanner_daily, current_qhr, next_qhr)

        # Assert
        assert start is True

    def test_schedule_time_21_30(self, monkeypatch):
        # Arrange
        time = time_now().replace(hour=21, minute=30)
        monkeypatch.setattr(Scanner, "schedule_datetime", time)

        current_qhr = time
        next_qhr = current_qhr + datetime.timedelta(minutes=15)

        # Act
        start = should_scanner_start(self.scanner_daily, current_qhr, next_qhr)

        # Assert
        assert start is True

    def test_schedule_time_23_45(self, monkeypatch):
        # Arrange
        time = time_now().replace(hour=23, minute=45)
        monkeypatch.setattr(Scanner, "schedule_datetime", time)

        current_qhr = time
        next_qhr = current_qhr + datetime.timedelta(minutes=15)

        # Act
        start = should_scanner_start(self.scanner_daily, current_qhr, next_qhr)

        # Assert
        assert start is True

    def test_schedule_around_midnight(self, monkeypatch):
        # Arrange
        time = time_now().replace(hour=21, minute=15)
        monkeypatch.setattr(Scanner, "schedule_datetime", time)

        current_qhr = time + datetime.timedelta(hours=3)
        next_qhr = current_qhr + datetime.timedelta(minutes=15)

        # Act
        start = should_scanner_start(self.scanner_daily, current_qhr, next_qhr)

        # Assert
        assert start is False

    def test_schedule_time_now(self, monkeypatch):
        # Arrange
        time = time_now().replace(hour=23, minute=00)
        monkeypatch.setattr(Scanner, "schedule_datetime", time)

        current_qhr = time.replace(hour=19, minute=0, second=0)
        next_qhr = current_qhr + datetime.timedelta(minutes=15)

        # Act
        start = should_scanner_start(self.scanner_daily, current_qhr, next_qhr, now=True)

        # Assert
        assert start is True

    def test_schedule_time_not_now(self, monkeypatch):
        # Arrange
        time = time_now().replace(hour=20, minute=45)
        monkeypatch.setattr(Scanner, "schedule_datetime", time)

        current_qhr = time.replace(hour=19, minute=00, second=0)
        next_qhr = current_qhr + datetime.timedelta(minutes=15)

        # Act
        start = should_scanner_start(self.scanner_daily, current_qhr, next_qhr, now=False)

        # Assert
        assert start is False
