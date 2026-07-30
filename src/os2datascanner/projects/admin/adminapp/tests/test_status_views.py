# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from datetime import timedelta

import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse_lazy
from django.utils import timezone

from ..models.scannerjobs.scanner_helpers import ScanStatus, ScanStatusSnapshot
from ..models.usererrorlog import UserErrorLog
from ..views.user_error_log_views import count_new_errors


@pytest.mark.django_db
class TestCountNewErrors:
    """Regression tests for the helper StatusBase.get_context_data relies on to
    populate the "new_error_logs" badge shown on every status page."""

    @pytest.fixture
    def errors_in_both_organizations(
            self, test_org, test_org2, basic_scanstatus, basic_scanstatus2):
        UserErrorLog.objects.create(
            scan_status=basic_scanstatus, organization=test_org,
            path="own-org-error", error_message="Something is wrong", is_new=True)
        UserErrorLog.objects.create(
            scan_status=basic_scanstatus2, organization=test_org2,
            path="other-org-error", error_message="Something is wrong", is_new=True)

    def test_user_with_view_client_permission_sees_all_organizations(
            self, user, errors_in_both_organizations):
        user.user_permissions.add(Permission.objects.get(codename='view_client'))
        assert count_new_errors(user) == 2

    def test_org_admin_sees_only_own_organization(self, user_admin, errors_in_both_organizations):
        assert count_new_errors(user_admin) == 1

    def test_user_without_administrator_relation(self, user, errors_in_both_organizations):
        """A logged-in user who is neither a permission holder nor an org
        Administrator has no accessible error logs, rather than crashing."""
        assert count_new_errors(user) == 0


@pytest.mark.django_db
class TestStatusCompletedView:
    url = reverse_lazy('status-completed')
    headers = {"HTTP_HX-Request": "true"}

    @staticmethod
    def _scan_tag(scanner, marker):
        # scan_tag has second-precision and a uniqueness constraint, so
        # several statuses for the same scanner need distinguishing.
        scan_tag = scanner._construct_scan_tag().to_json_object()
        scan_tag["marker"] = marker
        return scan_tag

    @pytest.fixture
    def completed_status(self, basic_scanner):
        """A finished, unresolved scan status - should show up in the view."""
        return ScanStatus.objects.create(
            scanner=basic_scanner,
            scan_tag=self._scan_tag(basic_scanner, "completed"),
            total_objects=1,
            scanned_objects=1,
            explored_sources=1,
            total_sources=1)

    @pytest.fixture
    def cancelled_status(self, basic_scanner):
        """A cancelled, unresolved scan status - should show up in the view."""
        return ScanStatus.objects.create(
            scanner=basic_scanner,
            scan_tag=self._scan_tag(basic_scanner, "cancelled"),
            cancelled=True)

    @pytest.fixture
    def resolved_status(self, basic_scanner):
        """A finished but already resolved scan status - should be excluded."""
        return ScanStatus.objects.create(
            scanner=basic_scanner,
            scan_tag=self._scan_tag(basic_scanner, "resolved"),
            total_objects=1,
            scanned_objects=1,
            explored_sources=1,
            total_sources=1,
            resolved=True)

    @pytest.fixture
    def resolving_admin(self, user_admin):
        """An org admin who has also been granted the separate, explicit
        permission required to resolve scan statuses. Being an org
        Administrator only scopes *which* organization's data is visible -
        it does not by itself grant the ability to resolve statuses."""
        user_admin.user_permissions.add(Permission.objects.get(codename='resolve_scanstatus'))
        return user_admin

    @pytest.fixture
    def unfinished_status(self, basic_scanner):
        """A scan status that is neither completed nor cancelled - should be excluded."""
        return ScanStatus.objects.create(
            scanner=basic_scanner,
            scan_tag=self._scan_tag(basic_scanner, "unfinished"),
            total_objects=10,
            scanned_objects=1,
            explored_sources=1,
            total_sources=10)

    def test_anonymous_user_redirected(self, client):
        response = client.get(self.url)
        assert response.status_code == 302

    def test_get_as_org_admin(self, client, user_admin, completed_status):
        client.force_login(user_admin)
        response = client.get(self.url)

        assert response.status_code == 200
        assert list(response.context["object_list"]) == [completed_status]

    def test_get_as_unrelated_user(self, client, user, completed_status):
        """A user without an Administrator relation should see no statuses."""
        client.force_login(user)
        response = client.get(self.url)

        assert response.status_code == 200
        assert list(response.context["object_list"]) == []

    def test_queryset_excludes_other_organization(
            self, client, user_admin, completed_status, basic_scanner2):
        other_org_status = ScanStatus.objects.create(
            scanner=basic_scanner2,
            scan_tag=self._scan_tag(basic_scanner2, "other-org"),
            total_objects=1,
            scanned_objects=1,
            explored_sources=1,
            total_sources=1)

        client.force_login(user_admin)
        response = client.get(self.url)

        object_list = list(response.context["object_list"])
        assert completed_status in object_list
        assert other_org_status not in object_list

    def test_queryset_excludes_unfinished_scans(
            self, client, user_admin, completed_status, unfinished_status):
        client.force_login(user_admin)
        response = client.get(self.url)

        object_list = list(response.context["object_list"])
        assert completed_status in object_list
        assert unfinished_status not in object_list

    def test_queryset_excludes_resolved_scans(
            self, client, user_admin, completed_status, resolved_status):
        client.force_login(user_admin)
        response = client.get(self.url)

        object_list = list(response.context["object_list"])
        assert completed_status in object_list
        assert resolved_status not in object_list

    def test_queryset_includes_cancelled_scans(
            self, client, user_admin, cancelled_status):
        client.force_login(user_admin)
        response = client.get(self.url)

        assert list(response.context["object_list"]) == [cancelled_status]

    def test_queryset_ordered_by_scan_tag_time_descending(self, client, user_admin, basic_scanner):
        def make_status(marker, iso_time):
            status = ScanStatus.objects.create(
                scanner=basic_scanner,
                scan_tag=self._scan_tag(basic_scanner, marker),
                total_objects=1,
                scanned_objects=1,
                explored_sources=1,
                total_sources=1)
            status.scan_tag["time"] = iso_time
            status.save(update_fields=["scan_tag"])
            return status

        older = make_status("older", "2020-01-01T00:00:00+00:00")
        newer = make_status("newer", "2021-01-01T00:00:00+00:00")

        client.force_login(user_admin)
        response = client.get(self.url)

        assert list(response.context["object_list"]) == [newer, older]

    def test_scan_time_excludes_idle_time_before_first_progress(
            self, client, user_admin, completed_status):
        """scan_time should span from the first snapshot that recorded
        progress to the last snapshot, excluding any idle time before the
        worker picked up the scan."""
        start = timezone.now()
        ScanStatusSnapshot.objects.create(
            scan_status=completed_status, time_stamp=start, scanned_objects=0)
        ScanStatusSnapshot.objects.create(
            scan_status=completed_status,
            time_stamp=start + timedelta(seconds=5), scanned_objects=1)
        ScanStatusSnapshot.objects.create(
            scan_status=completed_status,
            time_stamp=start + timedelta(seconds=65), scanned_objects=5)

        client.force_login(user_admin)
        response = client.get(self.url)

        [result] = response.context["object_list"]
        assert result.scan_time == timedelta(seconds=60)

    @pytest.fixture
    def fifteen_completed_statuses(self, basic_scanner):
        statuses = [
            ScanStatus(
                scanner=basic_scanner,
                scan_tag=self._scan_tag(basic_scanner, f"bulk-{i}"),
                total_objects=1,
                scanned_objects=1,
                explored_sources=1,
                total_sources=1)
            for i in range(15)
        ]
        ScanStatus.objects.bulk_create(statuses)

    def test_default_pagination(self, client, user_admin, fifteen_completed_statuses):
        client.force_login(user_admin)
        response = client.get(self.url)

        assert response.status_code == 200
        assert response.context["paginate_by"] == 10
        assert len(response.context["object_list"]) == 10
        assert response.context["paginator"].num_pages == 2
        # The frontend's paginate-by dropdown is built directly from this list.
        assert response.context["paginate_by_options"] == [10, 20, 50, 100, 250]

    def test_paginate_by_query_param(self, client, user_admin, fifteen_completed_statuses):
        client.force_login(user_admin)
        response = client.get(self.url, {"paginate_by": 20})

        assert response.status_code == 200
        assert response.context["paginate_by"] == 20
        assert len(response.context["object_list"]) == 15

    def test_out_of_range_page_clamps_to_last_page(
            self, client, user_admin, fifteen_completed_statuses):
        """EmptyPagePaginator clamps too-high page numbers to the last page
        instead of 404ing, so polling clients don't break when items resolve
        out from under them mid-session."""
        client.force_login(user_admin)
        response = client.get(self.url, {"page": 100})

        assert response.status_code == 200
        assert response.context["page_obj"].number == response.context["paginator"].num_pages

    def test_page_zero_returns_404(self, client, user_admin, fifteen_completed_statuses):
        client.force_login(user_admin)
        response = client.get(self.url, {"page": 0})

        assert response.status_code == 404

    def test_post_status_resolved(
            self, client, resolving_admin, completed_status, cancelled_status):
        client.force_login(resolving_admin)
        response = client.post(
            self.url,
            data={"pk": completed_status.pk},
            **self.headers,
            HTTP_HX_Trigger_Name="status-resolved")

        assert response.status_code == 200
        completed_status.refresh_from_db()
        cancelled_status.refresh_from_db()
        assert completed_status.resolved is True
        assert cancelled_status.resolved is False

    def test_post_status_resolved_selected(
            self, client, resolving_admin, completed_status, cancelled_status):
        client.force_login(resolving_admin)
        response = client.post(
            self.url,
            data={"table-checkbox": [completed_status.pk, cancelled_status.pk]},
            **self.headers,
            HTTP_HX_Trigger_Name="status-resolved-selected")

        assert response.status_code == 200
        completed_status.refresh_from_db()
        cancelled_status.refresh_from_db()
        assert completed_status.resolved is True
        assert cancelled_status.resolved is True

    def test_post_status_resolved_all(
            self, client, resolving_admin, completed_status, cancelled_status):
        client.force_login(resolving_admin)
        response = client.post(
            self.url,
            data={},
            **self.headers,
            HTTP_HX_Trigger_Name="status-resolved-all")

        assert response.status_code == 200
        completed_status.refresh_from_db()
        cancelled_status.refresh_from_db()
        assert completed_status.resolved is True
        assert cancelled_status.resolved is True

    def test_post_status_resolved_all_scoped_to_own_organization(
            self, client, resolving_admin, completed_status, basic_scanner2):
        other_org_status = ScanStatus.objects.create(
            scanner=basic_scanner2,
            scan_tag=self._scan_tag(basic_scanner2, "other-org"),
            total_objects=1,
            scanned_objects=1,
            explored_sources=1,
            total_sources=1)

        client.force_login(resolving_admin)
        client.post(
            self.url,
            data={},
            **self.headers,
            HTTP_HX_Trigger_Name="status-resolved-all")

        completed_status.refresh_from_db()
        other_org_status.refresh_from_db()
        assert completed_status.resolved is True
        assert other_org_status.resolved is False

    def test_post_without_htmx_header_does_not_resolve(
            self, client, resolving_admin, completed_status):
        client.force_login(resolving_admin)
        response = client.post(self.url, data={"pk": completed_status.pk})

        assert response.status_code == 200
        completed_status.refresh_from_db()
        assert completed_status.resolved is False

    def test_post_without_resolve_permission_is_forbidden(
            self, client, user_admin, completed_status):
        """Being an org Administrator alone must not be enough to resolve scan
        statuses - the template hides the resolve controls without
        resolve_scanstatus, and the view must enforce that server-side too,
        or a crafted request bypasses the UI entirely."""
        client.force_login(user_admin)
        response = client.post(
            self.url,
            data={"pk": completed_status.pk},
            **self.headers,
            HTTP_HX_Trigger_Name="status-resolved")

        assert response.status_code == 403
        completed_status.refresh_from_db()
        assert completed_status.resolved is False
