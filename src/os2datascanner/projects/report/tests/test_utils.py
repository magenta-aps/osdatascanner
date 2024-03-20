import pytest

from django.db import models, DataError, connection, transaction
from django.test import TestCase

from ..reportapp.utils import prepare_json_object, get_max_sens_prop_value
from ..reportapp.models.documentreport import DocumentReport

from .generate_test_data import (
        get_positive_match_with_probability_and_sensitivity, record_match)


class JSONHolder(models.Model):
    json = models.JSONField()

    class Meta:
        app_label = "os2datascanner_report_test"


class UtilsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(JSONHolder)

    @classmethod
    def tearDownClass(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(JSONHolder)
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        record_match(get_positive_match_with_probability_and_sensitivity())

    @pytest.mark.filterwarnings("ignore::DeprecationWarning")
    def test_get_max_sens_prop_value(self):
        """get_max_sens_prop_value is deprecated; use DocumentReport.matches directly.
        Since it is used in migration 0017_documentreport_added_sensitivity_and_probability,
        these tests are still in place."""
        self.assertEqual(1.0,
                         get_max_sens_prop_value(
                             DocumentReport.objects.first(),
                             'probability')
                         )
        self.assertEqual(1000,
                         get_max_sens_prop_value(
                             DocumentReport.objects.first(),
                             'sensitivity').value
                         )

    @pytest.mark.filterwarnings("ignore::UnicodeWarning")
    def test_json_null_bytes(self):
        """PostgreSQL-backed JSONFields cannot store null bytes, but our
        utility function can address that by detecting and removing them."""
        test_json = {"This\0 is": {"a\0": "te\0st"}, "you": "see"}
        with (self.subTest(),
                self.assertRaises(DataError),
                transaction.atomic()):
            JSONHolder(json=test_json).save()
        with self.subTest():
            o = JSONHolder(json=prepare_json_object(test_json))
            o.save()
            self.assertIsNotNone(
                    o.pk,
                    "saving stripped JSON object failed")
            self.assertEqual(
                    o.json,
                    {"This is": {"a": "test"}, "you": "see"},
                    "JSON stripping did not behave as expected")
