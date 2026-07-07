# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from datetime import timedelta

import structlog

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone

from os2datascanner.utils.system_utilities import time_now
from os2datascanner.core_organizational_structure.models.aliases import AliasType
from os2datascanner.projects.report.organizations.models import Organization, Alias
from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport
from os2datascanner.projects.report.reportapp.models.leader_statistic_snapshot import (
    LeaderStatisticSnapshot, AccountResultSnapshot)


logger = structlog.get_logger("reportapp")


def status_window_start():
    """The start of the three-week window used by handle_status.

    Mirrors AccountQuerySet.with_status: the window ends at the start of next
    Monday, so an account's status is stable across a given week."""
    now = timezone.now()
    next_monday = now + timedelta(weeks=1) - timedelta(
        days=now.weekday(), hours=now.hour, minutes=now.minute, seconds=now.second)
    return next_monday - timedelta(weeks=3)


def build_account_result_rows(snapshot, org, retention_days):
    """Yields AccountResultSnapshot rows for @org, one per non-empty
    (account, scanner_job, source_type) bucket.

    Every count is a distinct-report count, and the buckets partition an
    account's reports by scanner_job and source_type, so summing a field across
    an account's buckets reproduces the same total the live leader-overview
    annotations produce."""
    tw_ago = status_window_start()
    fp = DocumentReport.ResolutionChoices.FALSE_POSITIVE

    # Report-level constraints shared by every bucket count. The alias-level
    # constraints (non-shared, non-remediator, in-org account) are applied on the
    # Alias queryset below, where — being columns on Alias itself — they can't
    # introduce a spurious second join to the reports relation.
    count_base = Q(
        reports__number_of_matches__gte=1,
        reports__scanner_job__organization=org,
    )
    not_withheld = Q(reports__only_notify_superadmin=False)
    unhandled = Q(reports__resolution_status__isnull=True)

    annotations = {
        "unhandled_results": Count(
            "reports", filter=count_base & unhandled & not_withheld, distinct=True),
        "withheld_results": Count(
            "reports",
            filter=count_base & unhandled & Q(reports__only_notify_superadmin=True),
            distinct=True),
        "handled_recent": Count(
            "reports",
            filter=count_base & not_withheld & Q(
                reports__resolution_status__isnull=False,
                reports__resolution_time__gte=tw_ago),
            distinct=True),
        "new_recent": Count(
            "reports",
            filter=count_base & not_withheld & Q(reports__created_timestamp__gte=tw_ago),
            distinct=True),
        "handled_total": Count(
            "reports",
            filter=count_base & not_withheld & Q(reports__resolution_status__isnull=False),
            distinct=True),
        "fp_total": Count(
            "reports",
            filter=count_base & not_withheld & Q(reports__resolution_status=fp),
            distinct=True),
    }
    if retention_days is not None:
        cutoff = time_now() - timedelta(days=retention_days)
        annotations["old_results"] = Count(
            "reports",
            filter=count_base & unhandled & not_withheld & Q(
                reports__datasource_last_modified__lte=cutoff),
            distinct=True)

    buckets = (
        Alias.objects.filter(account__organization=org, shared=False)
        .exclude(_alias_type=AliasType.REMEDIATOR)
        .values("account", "reports__scanner_job", "reports__source_type")
        .annotate(**annotations)
    )

    for bucket in buckets.iterator():
        # Aliases with no reports produce a NULL-scanner row from the outer join.
        if bucket["reports__scanner_job"] is None:
            continue
        counts = {field: bucket.get(field, 0) for field in annotations}
        # Buckets whose reports all fail every count filter (e.g. a report with
        # no matches) carry no information and would only bloat the snapshot.
        if not any(counts.values()):
            continue
        yield AccountResultSnapshot(
            snapshot=snapshot,
            account_id=bucket["account"],
            scanner_job_id=bucket["reports__scanner_job"],
            source_type=bucket["reports__source_type"] or "",
            **counts,
        )


class Command(BaseCommand):
    """Regenerate the leader-overview statistics snapshot for organizations
    whose configured snapshot interval has elapsed."""
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
            "--org",
            metavar="UUID",
            help="only (re)generate the snapshot for this organization")
        parser.add_argument(
            "--force",
            action="store_true",
            help="regenerate even if the configured interval has not yet elapsed")

    def handle(self, org=None, force=False, **kwargs):
        organizations = Organization.objects.all()
        if org:
            organizations = organizations.filter(pk=org)

        for organization in organizations:
            if not force and not self.is_due(organization):
                logger.info("leader snapshot not due, skipping",
                            organization=str(organization))
                continue
            self.snapshot_organization(organization)

    def is_due(self, org):
        interval = org.leader_snapshot_interval
        if not interval:
            # An interval of 0 disables scheduled regeneration for this org.
            return False
        latest = org.leader_snapshots.first()
        if latest is None:
            return True
        return time_now() - latest.created_at >= timedelta(hours=interval)

    @transaction.atomic
    def snapshot_organization(self, org):
        retention_days = org.retention_days if org.retention_policy else None
        snapshot = LeaderStatisticSnapshot.objects.create(organization=org)
        AccountResultSnapshot.objects.bulk_create(
            build_account_result_rows(snapshot, org, retention_days),
            batch_size=2000)
        # Supersede older snapshots (their rows cascade). Because this runs in a
        # transaction, a concurrent page load reads the old snapshot until commit.
        org.leader_snapshots.exclude(pk=snapshot.pk).delete()
        logger.info("leader snapshot created", organization=str(org),
                    rows=snapshot.account_results.count())
