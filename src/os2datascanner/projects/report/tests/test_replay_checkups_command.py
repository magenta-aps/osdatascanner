import pytest

from django.core.management import call_command

from os2datascanner.engine2.pipeline.utilities.pika import PikaPipelineThread
from os2datascanner.projects.report.tests.test_utilities import create_reports_for
from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport


@pytest.fixture
def enqueued_messages(monkeypatch):
    """When enqueueing to a PikaPipelineThread, instead just put messages into a list
    and return that."""

    enqueued_messages = []

    def mock_enqueue_message(self, queue, message, **kwargs):
        enqueued_messages.append((queue, message))

    monkeypatch.setattr(PikaPipelineThread, "start", lambda self: None)
    monkeypatch.setattr(PikaPipelineThread, "enqueue_message", mock_enqueue_message)
    monkeypatch.setattr(PikaPipelineThread, "synchronise", lambda self: None)
    monkeypatch.setattr(PikaPipelineThread, "enqueue_stop", lambda self: None)
    monkeypatch.setattr(PikaPipelineThread, "join", lambda self: None)

    return enqueued_messages


@pytest.mark.django_db
class TestReplayCheckupsCommand:
    def test_replay_checkups_enqueues_messages(self, enqueued_messages, egon_email_alias):
        """The 'replay_checkups' command should enqueue a tuple consisting of the queue name and
        the raw_matches field of the report."""
        create_reports_for(egon_email_alias, 1)
        call_command("replay_checkups", "-f")

        assert len(enqueued_messages) == 1
        assert enqueued_messages[0][0] == "os2ds_checkups"
        assert enqueued_messages[0][1] == DocumentReport.objects.get().raw_matches

    @pytest.mark.parametrize("unhandled,handled", [
        (0, 0),
        (0, 1),
        (0, 10),
        (1, 0),
        (1, 1),
        (1, 10),
        (10, 0),
        (10, 1),
        (10, 10)
    ])
    def test_only_replay_unhandled_results(self, enqueued_messages, egon_email_alias,
                                           unhandled, handled):
        """Only reports which are unhandled should be enqueued."""
        create_reports_for(egon_email_alias, handled, resolution_status=1)
        create_reports_for(egon_email_alias, unhandled)
        call_command("replay_checkups", "-f")

        assert len(enqueued_messages) == unhandled

    @pytest.mark.parametrize("matches,problem", [
        (False, False),
        (True, False),
        (False, True),
        (True, True)
    ])
    def test_only_replay_results_with_matches_or_problem(self, enqueued_messages, egon_email_alias,
                                                         matches, problem):
        """Only reports with either a match or a problem should be enqueued."""
        create_reports_for(egon_email_alias, matched=matches, problem=problem)
        call_command("replay_checkups", "-f")

        assert bool(enqueued_messages) == (matches or problem)
