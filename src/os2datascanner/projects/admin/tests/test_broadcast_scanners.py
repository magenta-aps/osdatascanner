import pytest

from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner import Scanner
from os2datascanner.projects.admin.organizations.models import broadcasted_mixin


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

    enqueued_events = []

    def mock_publish_events(events):
        enqueued_events.append(events)

    monkeypatch.setattr(broadcasted_mixin,
                        "publish_events",
                        mock_publish_events)

    return enqueued_events


@pytest.mark.django_db
class TestBroadcastScanners:
    def test_create_scanner(self, enqueued_events, basic_rule, test_org):
        """Creating a scanner should add a creation event to the ppt,
        containing the fields pk, name, organization, scan_entire_org and only_notify_superadmin."""
        # Arrange
        enqueued_events.clear()

        # Act
        Scanner.objects.create(
            pk=17,
            name='Test scanner',
            rule=basic_rule,
            organization=test_org,
            scan_entire_org=True,
            only_notify_superadmin=True,
        )

        # Assert
        assert len(enqueued_events) == 1

        event = enqueued_events[0][0].to_json_object()
        assert event['type'] == 'bulk_event_create'
        assert len(event['classes']['Scanner']) == 1

        scanner_dict = event['classes']['Scanner'][0]
        assert scanner_dict['pk'] == 17
        assert scanner_dict['name'] == 'Test scanner'
        assert scanner_dict['organization'] == str(test_org.uuid)
        assert scanner_dict['scan_entire_org'] is True
        assert scanner_dict['only_notify_superadmin'] is True

    def test_save_scanner(self, enqueued_events, basic_rule, test_org, test_org2):
        """Saving a scanner should add a creation event to the ppt,
        containing the fields pk, name, organization, scan_entire_org and only_notify_superadmin."""
        # Arrange
        scanner = Scanner.objects.create(
            pk=17,
            name='Test scanner',
            rule=basic_rule,
            organization=test_org,
            scan_entire_org=True,
            only_notify_superadmin=True,
        )
        enqueued_events.clear()

        # Act
        scanner.name = 'New name'
        scanner.organization = test_org2
        scanner.scan_entire_org = False
        scanner.only_notify_superadmin = False
        scanner.save()

        # Assert
        assert len(enqueued_events) == 1

        event = enqueued_events[0][0].to_json_object()
        assert event['type'] == 'bulk_event_update'
        assert len(event['classes']['Scanner']) == 1

        scanner_dict = event['classes']['Scanner'][0]
        assert scanner_dict['pk'] == 17
        assert scanner_dict['name'] == 'New name'
        assert scanner_dict['organization'] == str(test_org2.uuid)
        assert scanner_dict['scan_entire_org'] is False
        assert scanner_dict['only_notify_superadmin'] is False

    def test_add_orgunit(self, enqueued_events, basic_rule, olsen_banden):
        """Adding a organizational unit to the m2m relation `org_unit` on a scanner,
        should be broadcasted."""
        # Arrange
        scanner = Scanner.objects.create(
            rule=basic_rule,
        )
        enqueued_events.clear()

        # Act
        scanner.org_unit.add(olsen_banden)

        # Assert
        assert len(enqueued_events) == 1

        event = enqueued_events[0][0].to_json_object()
        assert event['type'] == 'bulk_event_update'
        assert len(event['classes']['Scanner']) == 1

        scanner_dict = event['classes']['Scanner'][0]
        assert len(scanner_dict['org_unit']) == 1
        assert scanner_dict['org_unit'][0] == str(olsen_banden.uuid)

    def test_set_orgunits(self, enqueued_events, basic_rule, olsen_banden, familien_sand,
                          nisserne):
        """Adding multiple organizational units to the m2m relation `org_unit` on a scanner,
        should be broadcasted."""
        # Arrange
        scanner = Scanner.objects.create(
            rule=basic_rule,
        )
        enqueued_events.clear()

        # Act
        scanner.org_unit.set([olsen_banden, familien_sand, nisserne])

        # Assert
        assert len(enqueued_events) == 1

        event = enqueued_events[0][0].to_json_object()
        assert event['type'] == 'bulk_event_update'
        assert len(event['classes']['Scanner']) == 1

        scanner_dict = event['classes']['Scanner'][0]
        assert len(scanner_dict['org_unit']) == 3
        ou_uuids = sorted([str(ou.uuid) for ou in [olsen_banden, familien_sand, nisserne]])
        assert sorted(scanner_dict['org_unit']) == ou_uuids
