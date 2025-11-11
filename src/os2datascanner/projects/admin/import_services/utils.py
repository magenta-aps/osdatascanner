#!/usr/bin/env python
# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# OS2datascanner was developed by Magenta in collaboration with OS2 the
# Danish community of open source municipalities (https://os2.eu/).
#
# The code is currently governed by OS2 the Danish community of open
# source municipalities ( https://os2.eu/ )
from datetime import timedelta

import structlog

from django.conf import settings

from os2datascanner.projects.admin.core.models.background_job import JobState
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner import Scanner
from os2datascanner.projects.admin.adminapp.utils import CleanAccountMessage
from .models.google_workspace_configuration import GoogleWorkspaceConfig
from os2datascanner.utils.system_utilities import time_now

logger = structlog.get_logger("import_services")


def _start_import_job(
    importjob_model,
    lookup_filter: dict,
    job_kwargs: dict,
    allowed_states: tuple,
    log_name: str,
):
    """
    Internal helper for ImportService.start_import() methods.
    Given conditions, checks if a new import job should be started and does so accordingly.

    :param importjob_model: The importjob model, f.e. MSGraphImportJob.
    :param lookup_filter: Constraint for importjob_model lookup, f.e. realm for LDAPImportJob.
    :param job_kwargs: Additional kwargs to pass to importjob_model, needed to create a new one.
    :param allowed_states: Allowed states for previous job to be in for a new job to be created.
    :param log_name: Usually configuration object name and primary key - for logging statements.
    """

    try:
        latest_job = importjob_model.objects.filter(**lookup_filter).latest("created_at")
        now = time_now()

        # No import job should run a day - but it _can_ happen, that a job gets stuck in "RUNNING"
        # for various reasons. For a margin of error to be allowed, limit on "RUNNING"
        # is set to be 23 hours.
        if latest_job.exec_state == JobState.RUNNING:
            if latest_job.created_at < now - timedelta(hours=23):
                latest_job.exec_state = JobState.CANCELLED
                latest_job.save(update_fields=["_exec_state"])
                logger.warning(
                    "Previous RUNNING job was older than 23h and was cancelled",
                    config=log_name,
                )
                importjob_model.objects.create(**job_kwargs)
                logger.info("Import job created for", config=log_name)
                return

            logger.info(
                "Import not possible: latest job is still RUNNING",
                config=log_name
            )
            return

        if latest_job.exec_state in allowed_states:
            importjob_model.objects.create(**job_kwargs)
            logger.info("Import job created for", config=log_name)
        else:
            logger.info("Import is not possible right now, due to exec_state of the last job.",
                        config=log_name, exec_state=latest_job.exec_state)

    except importjob_model.DoesNotExist:
        importjob_model.objects.create(**job_kwargs)
        logger.info("Import job created for", config=log_name)


def construct_dict_from_scanners_stale_accounts() -> dict:
    """Builds a CleanAccountMessage cleanup dict for all stale accounts across all
    scanners. (See CleanAccountMessage.send for more details.)"""
    all_scanners = Scanner.objects.all()
    scanners_accounts_dict = {}

    for scanner in all_scanners:
        if scanner.statuses.last() and scanner.statuses.last().is_running:
            logger.info(f"Scanner “{scanner.name}” is currently running.")
        else:
            if stale_accounts := scanner.compute_stale_accounts():
                acc_dict = CleanAccountMessage.make_account_dict(stale_accounts)
                scanners_accounts_dict[scanner.pk] = acc_dict
                logger.info(
                        "Cleaning up accounts:"
                        f" {', '.join(acc_dict['usernames'])}"
                        f" for scanner: {scanner}.")

    return scanners_accounts_dict


def post_import_cleanup() -> None:
    """If the AUTOMATIC_IMPORT_CLEANUP-setting is enabled, this function
    initiates cleanup of all accounts, which will no longer be covered by
    future scans, but have been in the past."""

    from ..adminapp.models.scannerjobs.scanner_helpers import (  # noqa
            CoveredAccount)

    if settings.AUTOMATIC_IMPORT_CLEANUP:

        logger.info("Performing post import cleanup...")

        scanners_accounts_dict = construct_dict_from_scanners_stale_accounts()

        CleanAccountMessage.send(scanners_accounts_dict, publisher="post_import")
        for pk, acc_dict in scanners_accounts_dict.items():
            CoveredAccount.objects.filter(
                    scanner_id=pk,
                    account_id__in=acc_dict["uuids"]).delete()

        logger.info("Post import cleanup message sent to report module!")


def start_google_import(config: GoogleWorkspaceConfig):
    """
    Google Workspace Import Job start utility.
    Only allow job creation if no current job is running for this config.
    """
    from ..core.models.background_job import JobState
    from .models.google_workspace_import_job import GoogleWorkspaceImportJob

    org = config.organization

    try:
        latest_importjob = GoogleWorkspaceImportJob.objects.filter(
            organization=org,
            grant=config.grant
        ).latest("created_at")

        if latest_importjob.exec_state in (
                JobState.FINISHED,
                JobState.FAILED,
                JobState.CANCELLED,
                JobState.FINISHED_WITH_WARNINGS,
        ):
            GoogleWorkspaceImportJob.objects.create(
                organization=org,
                grant=config.grant,
                delegated_admin_email=config.delegated_admin_email,
            )
        else:
            logger.info(f"Google Workspace import already in progress for config {config.pk}")
    except GoogleWorkspaceImportJob.DoesNotExist:
        GoogleWorkspaceImportJob.objects.create(
            organization=org,
            grant=config.grant,
            delegated_admin_email=config.delegated_admin_email,
        )
