
from django.urls import reverse_lazy
from os2datascanner.core_organizational_structure.models.organization import SBSYSTabConfigChoices
from os2datascanner.engine2.model._staging.sbsysdb import SBSYSDBHandles
from os2datascanner.projects.report.reportapp.views.base_views import DocumentReport
from os2datascanner.projects.report.tests.test_utilities import create_reports_for
import pytest
from ..reportapp.models.container_report import ContainerReport, ScannerReference


@pytest.mark.django_db
class TestSBSYSReportView:

    @pytest.mark.parametrize("handled", [False, True])
    def test_case_shows_on_matching_tab(
            self, handled, client, settings, egon_account, egon_email_alias, sbsys_db_source
    ):
        """A case shows up only on the tab matching its state, with its documents in it."""
        settings.HANDLED_TAB = True
        egon_account.organization.sbsystab_access = SBSYSTabConfigChoices.ALL
        egon_account.organization.save()
        status = DocumentReport.ResolutionChoices.HANDLED if handled else None
        create_reports_for(egon_email_alias, num=2, source_type="sbsys-db",
                           resolution_status=status)
        container = ContainerReport.objects.create(
            scanner_job=ScannerReference.objects.get(), path="case", source_type="sbsys-db",
            handle=SBSYSDBHandles.Case(sbsys_db_source, "22.13.01-K02-3-13", "Test case", None)
            .to_json_object())
        DocumentReport.objects.update(container=container)

        matching, other_tab = (
            ("handled:sbsys-personal", "results:sbsys-personal") if handled
            else ("results:sbsys-personal", "handled:sbsys-personal"))

        client.force_login(egon_account.user)
        [shown] = client.get(reverse_lazy(matching)).context["container_reports"]
        assert shown == container
        assert {r.pk for r in shown.visible_reports} == set(
                DocumentReport.objects.values_list("pk", flat=True))
        assert not client.get(reverse_lazy(other_tab)).context["container_reports"]
