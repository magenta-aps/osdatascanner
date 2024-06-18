import pytest

from os2datascanner.projects.admin.adminapp.management.commands import status_collector


def record_status(status):
    """Records a status message to the database as though it were received by
    the administration system's pipeline collector."""
    return list(status_collector.status_message_received_raw(
            status.to_json_object()))


@pytest.mark.django_db
class TestStatus:

    @pytest.mark.parametrize(
        ('total_sources,explored_sources,total_objects,scanned_objects,'
         'fraction_explored,fraction_scanned,finished'), [
            (0, 0, 0, 0, None, None, False),
            (2, 0, 0, 0, 0.0, None, False),
            (2, 1, 20, 0, 0.5, None, False),
            (2, 2, 20, 0, 1.0, 0.0, False),
            (2, 2, 20, 10, 1.0, 0.5, False),
            (2, 2, 20, 20, 1.0, 1.0, True),
            ])
    def test_estimates(
            self,
            basic_scanstatus,
            total_sources,
            explored_sources,
            total_objects,
            scanned_objects,
            fraction_explored,
            fraction_scanned,
            finished):

        basic_scanstatus.total_sources = total_sources
        basic_scanstatus.explored_sources = explored_sources
        basic_scanstatus.total_objects = total_objects
        basic_scanstatus.scanned_objects = scanned_objects
        basic_scanstatus.save()

        assert basic_scanstatus.fraction_explored == fraction_explored
        assert basic_scanstatus.fraction_scanned == fraction_scanned
        assert basic_scanstatus.finished == finished

    def test_broken(self, basic_scanstatus):
        """Trying to derive properties for broken ScanStatus objects should
        fail cleanly."""
        basic_scanstatus.total_sources = 5
        basic_scanstatus.explored_sources = 5
        basic_scanstatus.save()

        assert basic_scanstatus.fraction_scanned is None

    def test_no_updates_on_save(self, basic_scanstatus, basic_scanner):
        basic_scanner.save()
        basic_scanstatus.save()
        last_modified = basic_scanstatus.last_modified
        # save should not update last_modified field on scannerStatus
        basic_scanstatus.save()

        assert basic_scanstatus.last_modified == last_modified

    def test_counting_broken_sources(
            self,
            basic_scan_tag,
            basic_scanstatus,
            status_message_10_objects,
            status_message_with_error):

        basic_scanstatus.total_sources = 5
        basic_scanstatus.save()

        record_status(status_message_10_objects)

        for _ in range(0, 4):
            record_status(status_message_with_error)

        basic_scanstatus.refresh_from_db()
        assert basic_scanstatus.explored_sources == 5
