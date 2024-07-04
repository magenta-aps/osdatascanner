import hashlib
import pytest

from os2datascanner.utils.system_utilities import time_now
from os2datascanner.engine2.model.file import (
        FilesystemHandle, FilesystemSource)
from os2datascanner.engine2.rules.regex import RegexRule
from os2datascanner.engine2.rules.dimensions import DimensionsRule
from os2datascanner.engine2.rules.logical import AndRule
from os2datascanner.engine2.rules.last_modified import LastModifiedRule
from os2datascanner.engine2.rules.rule import Sensitivity
from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.utilities.datetime import parse_datetime
from os2datascanner.engine2.model.smb import SMBSource, SMBHandle

from ..reportapp.models.documentreport import DocumentReport
from ..reportapp.management.commands import result_collector

from .generate_test_data import record_match, record_problem


@pytest.fixture
def time0():
    return "2020-10-28T13:51:49+01:00"


@pytest.fixture
def time1():
    return "2020-10-28T14:21:27+01:00"


@pytest.fixture
def time2():
    return "2020-10-28T14:36:20+01:00"


@pytest.fixture
def org_frag():
    return messages.OrganisationFragment(
        name="test_org", uuid="d92ff0c9-f066-40dc-a57e-541721b6c23e")


@pytest.fixture
def scan_tag0(time0, org_frag):
    return messages.ScanTagFragment(
        scanner=messages.ScannerFragment(
                pk=22, name="Dummy test scanner"),
        time=parse_datetime(time0),
        user=None, organisation=org_frag)


@pytest.fixture
def scan_tag1(time1, org_frag):
    return messages.ScanTagFragment(
        scanner=messages.ScannerFragment(
                pk=22, name="Dummy test scanner"),
        time=parse_datetime(time1),
        user=None, organisation=org_frag)


@pytest.fixture
def scan_tag2(time2, org_frag):
    return messages.ScanTagFragment(
        scanner=messages.ScannerFragment(
                pk=22, name="Dummy test scanner"),
        time=parse_datetime(time2), user=None, organisation=org_frag)


@pytest.fixture
def scan_tag3(time1, org_frag):
    return messages.ScanTagFragment(
        scanner=messages.ScannerFragment(
            pk=22, name="Dummy test scanner", keep_fp=True),
        time=parse_datetime(time1),
        user=None, organisation=org_frag)


@pytest.fixture
def scan_tag4(time1, org_frag):
    return messages.ScanTagFragment(
        scanner=messages.ScannerFragment(
            pk=22, name="Dummy test scanner", keep_fp=False),
        time=parse_datetime(time1),
        user=None, organisation=org_frag)


@pytest.fixture
def scan_tag5(time0, org_frag):
    return messages.ScanTagFragment(
        scanner=messages.ScannerFragment(
                pk=22, name="Dummy test scanner", test=True),
        time=parse_datetime(time0), user=None, organisation=org_frag)


@pytest.fixture
def scan_tag6(time1, org_frag):
    return messages.ScanTagFragment(
        scanner=messages.ScannerFragment(
                pk=22, name="Dummy test scanner", test=True),
        time=parse_datetime(time1), user=None, organisation=org_frag)


@pytest.fixture
def common_handle():
    return FilesystemHandle(
        FilesystemSource("/mnt/fs01.magenta.dk/brugere/af"),
        "OS2datascanner/Dokumenter/Verdensherredømme - plan.txt")


@pytest.fixture
def common_handle_corrupt():
    return FilesystemHandle(
        FilesystemSource("/mnt/fs01.magenta.dk/brugere/af"),
        "/logo/Flag/Gr\udce6kenland.jpg")


@pytest.fixture
def common_rule():
    return RegexRule("Vores hemmelige adgangskode er",
                     sensitivity=Sensitivity.WARNING)


@pytest.fixture
def dimension_rule():
    return DimensionsRule()


@pytest.fixture
def common_scan_spec(common_handle, common_rule):
    return messages.ScanSpecMessage(
        scan_tag=None,  # placeholder
        source=common_handle.source,
        rule=common_rule,
        configuration={},
        filter_rule=None,
        progress=None)


@pytest.fixture
def common_scan_spec_corrupt(common_handle_corrupt, common_rule):
    return messages.ScanSpecMessage(
        scan_tag=None,  # placeholder
        source=common_handle_corrupt.source,
        rule=common_rule,
        configuration={},
        filter_rule=None,
        progress=None)


@pytest.fixture
def positive_match(common_scan_spec, scan_tag0, common_handle, common_rule):
    return messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(scan_tag=scan_tag0),
        handle=common_handle,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])
        ])


@pytest.fixture
def positive_match_keep_fp(common_scan_spec, scan_tag3, common_handle, common_rule):
    return messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(scan_tag=scan_tag3),
        handle=common_handle,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])
        ])


@pytest.fixture
def positive_match_dont_keep_fp(common_scan_spec, scan_tag4, common_handle, common_rule):
    return messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(scan_tag=scan_tag4),
        handle=common_handle,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])
        ])


@pytest.fixture
def positive_match_corrupt(common_scan_spec_corrupt, scan_tag0, common_handle_corrupt, common_rule):
    return messages.MatchesMessage(
        scan_spec=common_scan_spec_corrupt._replace(scan_tag=scan_tag0),
        handle=common_handle_corrupt,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])
        ])


@pytest.fixture
def positive_match_with_dimension_rule_probability_and_sensitivity(
        common_scan_spec, scan_tag0, common_handle, common_rule, dimension_rule):
    return messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(scan_tag=scan_tag0),
        handle=common_handle,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object",
                          "probability": 0.6, "sensitivity": 750},
                         {"dummy1": "match object",
                          "probability": 0.0, "sensitivity": 1000},
                         {"dummy2": "match object",
                          "probability": 1.0, "sensitivity": 500}]),
            messages.MatchFragment(
                rule=dimension_rule,
                matches=[{"match": [2496, 3508]}])
        ])


@pytest.fixture
def positive_match_only_notify_superadmin(common_scan_spec, scan_tag5, common_handle, common_rule):
    return messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(scan_tag=scan_tag5),
        handle=common_handle,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])
        ])


@pytest.fixture
def positive_match_only_notify_superadmin_later(
        common_scan_spec, scan_tag6, common_handle, common_rule):
    return messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(scan_tag=scan_tag6),
        handle=common_handle,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])
        ])


@pytest.fixture
def negative_match(common_scan_spec, scan_tag1, common_handle, common_rule):
    return messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(
            scan_tag=scan_tag1),
        handle=common_handle,
        matched=False,
        matches=[messages.MatchFragment(
                rule=common_rule,
                matches=[])
        ])


@pytest.fixture
def deletion(scan_tag1, common_handle):
    return messages.ProblemMessage(
        scan_tag=scan_tag1,
        source=None,
        handle=common_handle,
        message="There was a file here. It's gone now.",
        missing=True)


@pytest.fixture
def transient_handle_error(scan_tag1, common_handle):
    return messages.ProblemMessage(
        scan_tag=scan_tag1,
        source=None,
        handle=common_handle,
        message="Bad command or file name")


@pytest.fixture
def transient_source_error(scan_tag1, common_handle):
    return messages.ProblemMessage(
        scan_tag=scan_tag1,
        source=common_handle.source,
        handle=None,
        message="Not ready reading drive A: [A]bort, [R]etry, [F]ail?")


@pytest.fixture
def late_rule(time2):
    return LastModifiedRule(parse_datetime(time2))


@pytest.fixture
def late_negative_match(common_scan_spec, scan_tag2, late_rule, common_rule, common_handle):
    return messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(
                scan_tag=scan_tag2,
                rule=AndRule(
                        late_rule,
                        common_rule)),
        handle=common_handle,
        matched=False,
        matches=[messages.MatchFragment(
                rule=late_rule,
                matches=[])])


@pytest.fixture
def smb_source_1():
    return SMBSource('//some/path', user='egon_olsen', driveletter='Q')


@pytest.fixture
def smb_source_2():
    return SMBSource('//some/path', user='dynamit_harry', driveletter='Q')


@pytest.fixture
def smb_source_3():
    return SMBSource('//some/path', user='egon_olsen', driveletter='W')


@pytest.fixture
def smb_handle_1(smb_source_1):
    return SMBHandle(smb_source_1, 'filename.file')


@pytest.fixture
def smb_handle_2(smb_source_2):
    return SMBHandle(smb_source_2, 'filename.file')


@pytest.fixture
def smb_handle_3(smb_source_3):
    return SMBHandle(smb_source_3, 'filename.file')


@pytest.fixture
def smb_match_1(common_scan_spec, scan_tag0, common_rule, smb_handle_1):
    return messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(scan_tag=scan_tag0),
        handle=smb_handle_1,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])
        ]
    )


@pytest.fixture
def smb_match_2(common_scan_spec, scan_tag1, common_rule, smb_handle_2):
    return messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(scan_tag=scan_tag1),
        handle=smb_handle_2,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])
        ]
    )


@pytest.fixture
def smb_match_3(common_scan_spec, scan_tag2, common_rule, smb_handle_3):
    return messages.MatchesMessage(
        scan_spec=common_scan_spec._replace(scan_tag=scan_tag2),
        handle=smb_handle_3,
        matched=True,
        matches=[
            messages.MatchFragment(
                rule=common_rule,
                matches=[{"dummy": "match object"}])
        ]
    )


@pytest.mark.django_db
class TestPipelineCollector:

    def test_rejection(self, negative_match):
        """Failed match messages shouldn't be stored in the database."""
        new = record_match(negative_match)
        assert new is None

    @pytest.mark.parametrize('match,expected', [
        ('positive_match',
         [1, None, 'time0',
          'file']),
        ('positive_match_corrupt',
         [2, None, 'time0',
          'file']),
    ])
    @pytest.mark.filterwarnings("ignore:stripping illegal surrogates for PostgreSQL compatibility")
    # We expect to get a warning because of the corrupted match
    def test_acceptance(self, request, match, expected):
        """Successful match messages should be stored in the database."""
        match = request.getfixturevalue(match)

        new = record_match(match)
        assert new.pk == expected[0]
        assert new.resolution_status == expected[1]
        assert new.scan_time == parse_datetime(request.getfixturevalue(expected[2]))
        assert new.source_type == expected[3]

    def test_edit(self, positive_match, negative_match):
        """Removing matches from a file should update the status of the
        previous match message, and should set the resolution time."""
        start = time_now()

        saved_match = record_match(positive_match)
        record_match(negative_match)
        saved_match.refresh_from_db()

        assert saved_match.resolution_status == DocumentReport.ResolutionChoices.EDITED.value
        assert saved_match.resolution_time >= start

    def test_removal(self, positive_match, deletion):
        """Deleting a file should update the status of the previous match
        message, and should set the resolution time."""
        start = time_now()

        saved_match = record_match(positive_match)
        record_problem(deletion)
        saved_match.refresh_from_db()

        assert saved_match.resolution_status == DocumentReport.ResolutionChoices.REMOVED.value
        assert saved_match.resolution_time >= start

    def test_removal_problem(self, transient_handle_error, deletion):
        """Deleting a file, which was previously the source of a problem but
        not a match, should delete the previously created DocumentReport."""
        problem_report = record_problem(transient_handle_error)
        record_problem(deletion)

        with pytest.raises(DocumentReport.DoesNotExist):
            problem_report.refresh_from_db()

    def test_transient_handle_errors(self, transient_handle_error):
        """Source types should be correctly extracted from Handle errors."""
        new = record_problem(transient_handle_error)

        assert new.source_type == transient_handle_error.handle.source.type_label

    def test_transient_source_errors(self, transient_source_error):
        """Source types should be correctly extracted from Source errors."""
        new = record_problem(transient_source_error)

        assert new.source_type == transient_source_error.source.type_label

    def test_recycler(self, positive_match, late_negative_match, time2):
        """Receiving a failed match message which failed because of the
        Last-Modified check should update the timestamp of the previous match
        message, but should not create a new database object."""
        saved_match = record_match(positive_match)
        new = record_match(late_negative_match)

        assert new is None

        saved_match.refresh_from_db()

        assert saved_match.scan_time == parse_datetime(time2)
        assert saved_match.resolution_status is None

    def test_decycler(self, positive_match, transient_handle_error):
        """Receiving a failed match for an object that already had matches
        should blank out those matches, as they are no longer readable."""
        saved_match = record_match(positive_match)
        new = record_problem(transient_handle_error)

        assert new == saved_match
        assert new.raw_metadata is None

    def test_filter_internal_rules_matches(
            self,
            common_scan_spec,
            scan_tag0,
            common_handle,
            common_rule,
            dimension_rule,
            positive_match_with_dimension_rule_probability_and_sensitivity):
        match_to_match = messages.MatchesMessage(
            scan_spec=common_scan_spec._replace(scan_tag=scan_tag0),
            handle=common_handle,
            matched=True,
            matches=[
                messages.MatchFragment(
                    rule=common_rule,
                    matches=[{"dummy2": "match object",
                              "probability": 1.0, "sensitivity": 500},
                             {"dummy": "match object",
                              "probability": 0.6, "sensitivity": 750},
                             {"dummy1": "match object",
                              "probability": 0.0, "sensitivity": 1000}]),
                messages.MatchFragment(
                    rule=dimension_rule,
                    matches=[{"match": [2496, 3508]}])
            ])

        assert result_collector.sort_matches_by_probability(
                positive_match_with_dimension_rule_probability_and_sensitivity.to_json_object()
            )["matches"] == match_to_match.to_json_object()["matches"]

    @pytest.mark.filterwarnings("ignore:stripping illegal surrogates for PostgreSQL compatibility")
    # We expect to get a warning because of the corrupted match
    def test_path_format_of_matches(
            self,
            positive_match,
            positive_match_corrupt,
            positive_match_with_dimension_rule_probability_and_sensitivity):
        """Check that recording the matches correctly crunches the handles
        to the `path`-field."""
        pos_match = record_match(positive_match)
        cor_match = record_match(positive_match_corrupt)
        dps_match = record_match(positive_match_with_dimension_rule_probability_and_sensitivity)

        assert pos_match.path == hashlib.sha512(
            "FilesystemHandle(_source=(FilesystemSource(_path=/mnt/fs01.magenta.dk/brugere/af));"
            "_relpath=OS2datascanner/Dokumenter/Verdensherred\xf8mme - plan.txt)".encode(
                "unicode_escape")).hexdigest()
        assert cor_match.path == hashlib.sha512(
            "FilesystemHandle(_source=(FilesystemSource(_path=/mnt/fs01.magenta.dk/brugere/af));"
            "_relpath=/logo/Flag/Gr\udce6kenland.jpg)".encode(
                "unicode_escape")).hexdigest()
        assert dps_match.path == hashlib.sha512(
            "FilesystemHandle(_source=(FilesystemSource(_path=/mnt/fs01.magenta.dk/brugere/af));"
            "_relpath=OS2datascanner/Dokumenter/Verdensherred\xf8mme - plan.txt)".encode(
                "unicode_escape")).hexdigest()

    def test_crunching_handles(self, smb_handle_1, smb_handle_2, smb_handle_3):
        """Check that handles are crunched correctly."""
        smb_crunched_1 = smb_handle_1.crunch(hash=True)
        smb_crunched_2 = smb_handle_2.crunch(hash=True)
        smb_crunched_3 = smb_handle_3.crunch(hash=True)

        assert smb_crunched_1 == hashlib.sha512(
            "SMBHandle(_source=(SMBSource(_unc=//some/path;_user=egon_olsen));"
            "_relpath=filename.file)".encode("unicode_escape")).hexdigest()
        assert smb_crunched_2 == hashlib.sha512(
            "SMBHandle(_source=(SMBSource(_unc=//some/path;_user=dynamit_harry));"
            "_relpath=filename.file)".encode("unicode_escape")).hexdigest()
        assert smb_crunched_3 == hashlib.sha512(
            "SMBHandle(_source=(SMBSource(_unc=//some/path;_user=egon_olsen));"
            "_relpath=filename.file)".encode("unicode_escape")).hexdigest()

    def test_same_path_updates_document_report(self, smb_match_1, smb_match_2, smb_match_3):
        """Ensure that recording matches with handles, where only the _user or
        _driveletter differs, updates the existing report, instead of creating
        a new one."""

        smb_dr_1 = record_match(smb_match_1._replace(handle=smb_match_1.handle.censor()))

        assert DocumentReport.objects.count() == 1

        smb_dr_2 = record_match(smb_match_2._replace(handle=smb_match_2.handle.censor()))

        assert DocumentReport.objects.count() == 1
        assert smb_dr_1 == smb_dr_2

        smb_dr_3 = record_match(smb_match_3._replace(handle=smb_match_3.handle.censor()))

        assert DocumentReport.objects.count() == 1
        assert smb_dr_1.path == smb_dr_3.path

    def test_missing_file_with_no_previous_report(self, deletion):
        """ A problem message containing information about a missing file, with
        no unresolved or resolution_status=0 DocumentReport,
        has no relevance, should be thrown away and not create a new DR."""
        record_problem(deletion)
        assert DocumentReport.objects.count() == 0

    def test_requeued_problem_with_existing_report(self, transient_handle_error):
        """ If exactly the same problem message enters the queue again,
        it should not cause two reports nor crash. """

        record_problem(transient_handle_error)
        # Imagine a world, where the same message enters the queue again:
        record_problem(transient_handle_error)

        # Check that we've only got one DocumentReport
        assert DocumentReport.objects.count() == 1

    def test_requeued_match_with_existing_report(self, positive_match):
        """ If exactly the same match message enters the queue again,
         it should not cause two reports nor crash. """

        record_match(positive_match)
        # Imagine a world, where the same message enters the queue again:
        record_match(positive_match)

        assert DocumentReport.objects.count() == 1

    def test_reqeued_match_with_existing_false_positive_report(
            self, positive_match, positive_match_keep_fp, positive_match_dont_keep_fp):
        """If a report has been handled as false positive, receiving the same
        match message again should keep or override the resolution_status,
        dependant on the 'keep_fp'-value received."""

        # Initial match message
        record_match(positive_match)

        # Handle the report as a false positive
        dr = DocumentReport.objects.last()
        dr.resolution_status = DocumentReport.ResolutionChoices.FALSE_POSITIVE.value
        dr.save()

        # Another message
        record_match(positive_match_keep_fp)

        # Resolution status should still be the same.
        assert DocumentReport.objects.last().resolution_status ==\
            DocumentReport.ResolutionChoices.FALSE_POSITIVE.value

        # Another message, this time with keep_fp=False
        record_match(positive_match_dont_keep_fp)

        # Resolution status should be None now.
        assert DocumentReport.objects.last().resolution_status is None

    def test_conserve_false_positive_same_message_twice(
            self, positive_match, positive_match_keep_fp):
        """When performing a thorough scan, previously handled reports, which
        are marked as false positive, will be received by the result collector
        twice, because the engine will visit it twice (due to ScheduledCheckups.)
        The status should still be conserved."""

        # Initial match message
        record_match(positive_match)

        # Handle the report as a false positive
        dr = DocumentReport.objects.last()
        dr.resolution_status = DocumentReport.ResolutionChoices.FALSE_POSITIVE.value
        dr.save()

        # Another message -- twice
        record_match(positive_match_keep_fp)
        record_match(positive_match_keep_fp)

        # Resolution status should still be the same.
        assert DocumentReport.objects.last().resolution_status ==\
            DocumentReport.ResolutionChoices.FALSE_POSITIVE.value

    def test_override_only_notify_superadmin_with_last_modified_on(
            self, positive_match_only_notify_superadmin, late_negative_match):
        """If a match has been scanned with only_notify_superadmin, and later is scanned without it,
        the DocumentReport should be updated accordingly."""

        record_match(positive_match_only_notify_superadmin)
        before = DocumentReport.objects.last().only_notify_superadmin

        record_match(late_negative_match)
        after = DocumentReport.objects.last().only_notify_superadmin

        assert before
        assert not after

    def test_only_override_when_only_notify_superadmin_turned_off(
            self,
            positive_match_only_notify_superadmin,
            positive_match_only_notify_superadmin_later):
        """If a match has been scanned with only_notify_superadmin, scanning it again later,
        shouldn't change only_notify_superadmin."""

        record_match(positive_match_only_notify_superadmin)
        before = DocumentReport.objects.last().only_notify_superadmin

        record_match(positive_match_only_notify_superadmin_later)
        after = DocumentReport.objects.last().only_notify_superadmin

        assert before
        assert after

    def test_take_back_results_when_using_only_notify_superadmin(
            self, positive_match, positive_match_only_notify_superadmin_later):
        """Scanning with only_notify_superadmin on, should update previously scanned matches."""

        record_match(positive_match)
        before = DocumentReport.objects.last().only_notify_superadmin

        record_match(positive_match_only_notify_superadmin_later)
        after = DocumentReport.objects.last().only_notify_superadmin

        assert not before
        assert after
