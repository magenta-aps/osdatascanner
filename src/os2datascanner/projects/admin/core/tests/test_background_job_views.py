# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest
from django.urls import reverse
from django.utils.timezone import now

from os2datascanner.projects.admin.core.models.background_job import (
    BackgroundJob, CounterJob, JobState)
from os2datascanner.projects.admin.core.views import JOB_ORGANIZATION_PATHS
from os2datascanner.projects.admin.import_services.models import (
    LDAPImportJob, OS2moImportJob, Realm)

# BackgroundJob subclasses that have no organization.
JOBS_WITHOUT_ORGANIZATION = {CounterJob}


def test_every_job_type_has_organization_path():
    """Each BackgroundJob subclass must either appear in
    JOB_ORGANIZATION_PATHS or be listed as having no organization."""
    covered = {path.split("__")[0] for path in JOB_ORGANIZATION_PATHS}

    for job_type in BackgroundJob.__subclasses__():
        if job_type in JOBS_WITHOUT_ORGANIZATION:
            continue
        assert job_type._meta.model_name in covered, (
            f"{job_type.__name__} has no entry in JOB_ORGANIZATION_PATHS")


@pytest.fixture
def waterdeep_job(test_org):
    return OS2moImportJob.objects.create(organization=test_org)


@pytest.fixture
def baldurs_gate_job(test_org2):
    realm = Realm.objects.create(
        realm_id=test_org2.slug, organization=test_org2, last_modified=now())
    return LDAPImportJob.objects.create(realm=realm)


def status_url(job):
    return reverse("background_job_status_widget", kwargs={"pk": job.pk})


def cancel_url(job):
    return reverse("background_job_cancel", kwargs={"pk": job.pk})


@pytest.mark.django_db
class TestBackgroundJobViews:
    def test_anonymous_is_redirected(self, client, waterdeep_job):
        assert client.get(status_url(waterdeep_job)).status_code == 302
        assert client.post(cancel_url(waterdeep_job)).status_code == 302
        assert waterdeep_job.exec_state == JobState.WAITING

    def test_own_job_status_is_shown(self, client, user_admin, waterdeep_job):
        client.force_login(user_admin)

        assert client.get(status_url(waterdeep_job)).status_code == 200

    def test_other_client_job_is_404(
            self, client, user_admin, baldurs_gate_job):
        client.force_login(user_admin)

        assert client.get(status_url(baldurs_gate_job)).status_code == 404
        assert client.post(cancel_url(baldurs_gate_job)).status_code == 404
        assert baldurs_gate_job.exec_state == JobState.WAITING

    def test_job_without_organization_is_404(self, client, user_admin):
        job = CounterJob.objects.create(count_to=20)
        client.force_login(user_admin)

        assert client.get(status_url(job)).status_code == 404

    def test_cancel_requires_post(self, client, user_admin, waterdeep_job):
        client.force_login(user_admin)

        assert client.get(cancel_url(waterdeep_job)).status_code == 405
        assert waterdeep_job.exec_state == JobState.WAITING

        assert client.post(cancel_url(waterdeep_job)).status_code == 200
        assert waterdeep_job.exec_state == JobState.CANCELLED

    def test_superuser_sees_all_jobs(
            self, client, superuser, waterdeep_job, baldurs_gate_job):
        client.force_login(superuser)

        assert client.get(status_url(waterdeep_job)).status_code == 200
        assert client.get(status_url(baldurs_gate_job)).status_code == 200
