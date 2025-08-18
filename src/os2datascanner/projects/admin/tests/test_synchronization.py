import pytest

from os2datascanner.projects.admin.organizations.models import broadcasted_mixin

from os2datascanner.projects.admin.organizations.broadcast_bulk_events import BulkCreateEvent, \
    BulkUpdateEvent, BulkDeleteEvent
from os2datascanner.projects.admin.organizations.models.broadcasted_mixin import (
    get_broadcastable_dict)


@pytest.fixture(autouse=True)
def we_are_totally_not_in_a_test_environment(monkeypatch):

    def mock_in_test_environment():
        return False

    monkeypatch.setattr(broadcasted_mixin,
                        "in_test_environment",
                        mock_in_test_environment)


@pytest.fixture
def enqueued_events(monkeypatch):
    """When enqueueing to a PikaPipelineThread, instead just put messages into a list
    and return that."""

    enqueued_messages = []

    def mock_publish_events(events):
        enqueued_messages.append(events)

    monkeypatch.setattr(broadcasted_mixin,
                        "publish_events",
                        mock_publish_events)

    return enqueued_messages


@pytest.mark.django_db
class TestSynchronizeGrants:

    def test_smbgrant_has_grantextra(self, smb_grant):
        """Simply creating a grant in the admin module should also create a GrantExtra related to
        that grant. The value of the "should_broadcast" field of that object should be False."""

        assert hasattr(smb_grant, "grant_extra")
        assert smb_grant.grant_extra
        assert smb_grant.grant_extra.should_broadcast is False

    def test_ewsgrant_has_grantextra(self, exchange_grant):
        """Simply creating a grant in the admin module should also create a GrantExtra related to
        that grant. The value of the "should_broadcast" field of that object should be False."""

        assert hasattr(exchange_grant, "grant_extra")
        assert exchange_grant.grant_extra
        assert exchange_grant.grant_extra.should_broadcast is False

    def test_graphgrant_has_grantextra(self, msgraph_grant):
        """Simply creating a grant in the admin module should also create a GrantExtra related to
        that grant. The value of the "should_broadcast" field of that object should be False."""

        assert hasattr(msgraph_grant, "grant_extra")
        assert msgraph_grant.grant_extra
        assert msgraph_grant.grant_extra.should_broadcast is False

    def test_googleapigrant_has_grantextra(self, google_api_grant):
        """Simply creating a grant in the admin module should also create a GrantExtra related to
        that grant. The value of the "should_broadcast" field of that object should be False."""

        assert hasattr(google_api_grant, "grant_extra")
        assert google_api_grant.grant_extra
        assert google_api_grant.grant_extra.should_broadcast is False

    def test_changing_should_broadcast_false_to_true(self, smb_grant, enqueued_events):
        gextra = smb_grant.grant_extra
        gextra.should_broadcast = True
        gextra.save()

        assert len(enqueued_events) == 1
        assert enqueued_events[0][0].to_json_object() == BulkCreateEvent(
            get_broadcastable_dict(smb_grant.__class__, smb_grant)).to_json_object()

    def test_changing_should_broadcast_true_to_false(self, smb_grant, enqueued_events):
        gextra = smb_grant.grant_extra
        gextra.should_broadcast = True
        gextra.save()

        enqueued_events.clear()

        gextra.should_broadcast = False
        gextra.save()

        assert len(enqueued_events) == 1
        assert enqueued_events[0][0].to_json_object() == BulkDeleteEvent(
            get_broadcastable_dict(smb_grant.__class__, smb_grant, delete=True)).to_json_object()

    def test_changing_should_broadcast_false_to_false(self, smb_grant, enqueued_events):
        gextra = smb_grant.grant_extra
        gextra.should_broadcast = False
        gextra.save()

        assert len(enqueued_events) == 0

    def test_saving_grant_with_should_broadcast_true(self, smb_grant, enqueued_events):
        gextra = smb_grant.grant_extra
        gextra.should_broadcast = True
        gextra.save()

        # We don't care about this first message.
        enqueued_events.clear()

        smb_grant.username = "new_username_new_me"

        smb_grant.save()

        assert len(enqueued_events) == 1
        assert enqueued_events[0][0].to_json_object() == BulkUpdateEvent(
            get_broadcastable_dict(smb_grant.__class__, smb_grant)).to_json_object()
