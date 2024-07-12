import pytest

from django.db import models, DataError, connection, transaction

from ..reportapp.utils import prepare_json_object, get_max_sens_prop_value
from ..reportapp.models.documentreport import DocumentReport

from os2datascanner.projects.report.tests.test_utilities import create_reports_for


class JSONHolder(models.Model):
    json = models.JSONField()

    class Meta:
        app_label = "os2datascanner_report_test"


@pytest.mark.django_db
class TestUtils:

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_get_max_sens_prop_value(self, egon_email_alias):
        """get_max_sens_prop_value is deprecated; use DocumentReport.matches directly.
        Since it is used in migration 0017_documentreport_added_sensitivity_and_probability,
        these tests are still in place."""
        create_reports_for(egon_email_alias, num=1)
        assert get_max_sens_prop_value(DocumentReport.objects.first(), 'probability') == 1.0
        assert get_max_sens_prop_value(DocumentReport.objects.first(), 'sensitivity').value == 1000

    @pytest.mark.filterwarnings("ignore::UnicodeWarning")
    def test_json_null_bytes(self):
        """PostgreSQL-backed JSONFields cannot store null bytes, but our
        utility function can address that by detecting and removing them."""
        test_json = {"This\0 is": {"a\0": "te\0st"}, "you": "see"}
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(JSONHolder)
        with (pytest.raises(DataError), transaction.atomic()):
            JSONHolder(json=test_json).save()

        o = JSONHolder(json=prepare_json_object(test_json))
        o.save()

        assert o.pk is not None
        assert o.json == {"This is": {"a": "test"}, "you": "see"}
