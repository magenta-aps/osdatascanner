from datetime import timedelta

import pytest

from os2datascanner.projects.admin.core.models.background_job import JobState
from .test_ldap_configuration import ldap_conf  # noqa F811, fixture
from os2datascanner.utils.system_utilities import time_now

from ..models import LDAPImportJob, MSGraphConfiguration, MSGraphImportJob, \
    OS2moConfiguration, OS2moImportJob


@pytest.fixture
def msgraph_conf(test_org, msgraph_grant):
    config = MSGraphConfiguration.objects.create(
        organization=test_org,
        grant=msgraph_grant,
        last_modified=time_now()
    )
    return config


@pytest.fixture
def os2mo_conf(test_org):
    config = OS2moConfiguration.objects.create(
        organization=test_org,
        last_modified=time_now()
    )
    return config


@pytest.fixture
def msgraph_import_running_23hrs_5min(msgraph_conf, test_org):
    job = MSGraphImportJob(
        organization=test_org,
        grant=msgraph_conf.grant,
        _exec_state=JobState.RUNNING.value,
    )
    job.save()
    # Slightly convoluted, but what you're going to do - auto_now field.
    # Has to be older than 23hrs - so, 23hrs and 5 minutes.
    job.created_at = time_now() - timedelta(hours=23, minutes=5)
    job.save(update_fields=['created_at'])


@pytest.fixture
def ldap_import_running_23hrs_5min(ldap_conf):  # noqa F811, fixture
    job = LDAPImportJob(
        realm=ldap_conf.realm,
        _exec_state=JobState.RUNNING.value,
    )
    job.save()
    job.created_at = time_now() - timedelta(hours=23, minutes=5)
    job.save(update_fields=['created_at'])


@pytest.fixture
def os2mo_import_running_23hrs_5min(os2mo_conf, test_org):
    job = OS2moImportJob(organization=test_org, _exec_state=JobState.RUNNING.value)
    job.save()
    job.created_at = time_now() - timedelta(hours=23, minutes=5)
    job.save(update_fields=['created_at'])


@pytest.fixture
def msgraph_import_job(msgraph_conf, test_org):
    return MSGraphImportJob.objects.create(
        organization=test_org,
        grant=msgraph_conf.grant,
    )


@pytest.fixture
def ldap_import_job(ldap_conf):  # noqa F811, fixture
    return LDAPImportJob.objects.create(
        realm=ldap_conf.realm,
        _exec_state=JobState.RUNNING.value,
    )


@pytest.fixture
def os2mo_import_job(os2mo_conf, test_org):
    return OS2moImportJob.objects.create(organization=test_org)


@pytest.mark.django_db
class TestStartImport:
    @pytest.mark.parametrize("config, import_job", [
        ("ldap_conf", LDAPImportJob),
        ("msgraph_conf", MSGraphImportJob),
        ("os2mo_conf", OS2moImportJob),
    ])
    def test_start_import_creates_backgroundjob(self, request, config, import_job):
        # Arrange
        conf = request.getfixturevalue(config)

        # Act
        conf.start_import()

        # Assert
        assert import_job.objects.count() == 1

    @pytest.mark.parametrize("config, import_job", [
        ("ldap_conf", LDAPImportJob),
        ("msgraph_conf", MSGraphImportJob),
        ("os2mo_conf", OS2moImportJob),
    ])
    def test_new_import_starts_if_stuck_in_running_over_23_hrs(self, request, config, import_job,
                                                               msgraph_import_running_23hrs_5min,
                                                               ldap_import_running_23hrs_5min,
                                                               os2mo_import_running_23hrs_5min
                                                               ):
        # Arrange
        conf = request.getfixturevalue(config)

        # Act/Assert

        # Verify that an existing job is there -- and in RUNNING.
        running_job = import_job.objects.get()
        assert running_job.exec_state == JobState.RUNNING

        # Try to import
        conf.start_import()

        # Verify that the running job is now cancelled and a new one is created, in WAITING state.
        assert running_job.exec_state == JobState.CANCELLED
        assert import_job.objects.count() == 2
        assert import_job.objects.latest('created_at').exec_state == JobState.WAITING

    @pytest.mark.parametrize(
        "config, import_job, allowed_states",
        [
            (
                    "ldap_conf",
                    LDAPImportJob,
                    [
                        JobState.FINISHED,
                        JobState.FINISHED_WITH_WARNINGS,
                        JobState.FAILED,
                        JobState.CANCELLED,
                    ],
            ),
            (
                    "msgraph_conf",
                    MSGraphImportJob,
                    [
                        JobState.FINISHED,
                        JobState.FAILED,
                        JobState.CANCELLED,
                    ],
            ),
            (
                    "os2mo_conf",
                    OS2moImportJob,
                    [
                        JobState.FINISHED,
                        JobState.FAILED,
                        JobState.CANCELLED,
                    ],
            ),
        ],
    )
    def test_can_start_new_job_when_existing_is_in_allowed_state(self, request, config, import_job,
                                                                 allowed_states,
                                                                 msgraph_import_job,
                                                                 ldap_import_job,
                                                                 os2mo_import_job):
        # Arrange
        conf = request.getfixturevalue(config)

        for state in allowed_states:
            job = import_job.objects.get()
            # Set the exec state to one that allows a new one to be created.
            job.exec_state = state
            job.save()

            # Act
            conf.start_import()

            # Assert
            assert import_job.objects.count() == 2
            latest_job = import_job.objects.latest('created_at')
            assert latest_job.exec_state == JobState.WAITING

            # Clean up, to not break the test's count().
            latest_job.delete()

    @pytest.mark.parametrize(
        "config, import_job, disallowed_states",
        [
            (
                    "ldap_conf",
                    LDAPImportJob,
                    [
                        JobState.WAITING,
                        JobState.RUNNING,
                        JobState.CANCELLING,
                    ],
            ),
            (
                    "msgraph_conf",
                    MSGraphImportJob,
                    [
                        JobState.WAITING,
                        JobState.RUNNING,
                        JobState.CANCELLING,
                        JobState.FINISHED_WITH_WARNINGS
                    ],
            ),
            (
                    "os2mo_conf",
                    OS2moImportJob,
                    [
                        JobState.WAITING,
                        JobState.RUNNING,
                        JobState.CANCELLING,
                        JobState.FINISHED_WITH_WARNINGS
                    ],
            ),
        ],
    )
    def test_cant_start_new_job_when_in_disallowed_state(self, request, config, import_job,
                                                         disallowed_states,
                                                         msgraph_import_job,
                                                         ldap_import_job,
                                                         os2mo_import_job):
        # Arrange
        conf = request.getfixturevalue(config)

        for state in disallowed_states:
            job = import_job.objects.get()
            # Set the exec state to one that does not allow a new one to be created.
            job.exec_state = state
            job.save()

            # Act
            conf.start_import()

            # Assert
            assert import_job.objects.count() == 1
            assert import_job.objects.get().exec_state == state
