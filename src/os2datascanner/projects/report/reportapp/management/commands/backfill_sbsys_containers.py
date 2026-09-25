# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import structlog

from django.core.management.base import BaseCommand

from os2datascanner.engine2.model.core import UnknownSchemeError
from os2datascanner.engine2.model.core.errors import DeserialisationError

from ...models.documentreport import DocumentReport
from .result_collector import get_or_create_container

logger = structlog.get_logger("reportapp")


class Command(BaseCommand):
    """Retroactively attaches a ContainerReport to every SBSYS DocumentReport
    created before container support existed. Purely additive: only ever
    fills a null `container` field, never touches anything else."""
    help = __doc__

    def handle(self, **kwargs):
        qs = DocumentReport.objects.filter(
                source_type="sbsys-db", container__isnull=True)
        attached = 0
        skipped = 0
        for report in qs.iterator():
            try:
                message = report.matches or report.problem or report.metadata
                if message is None or message.handle is None:
                    logger.warning(
                            "skipping report with no matches/problem/metadata",
                            report_pk=report.pk)
                    skipped += 1
                    continue
                container = get_or_create_container(
                        report.scanner_job, message.handle)
            except (UnknownSchemeError, DeserialisationError):
                # A single malformed row must never stop the rest of the run:
                # the command would otherwise abort at the same row forever.
                logger.warning(
                        "skipping report that could not be deserialised",
                        report_pk=report.pk, exc_info=True)
                skipped += 1
                continue

            if container is None:
                logger.warning(
                        "skipping report that isn't part of an SBSYS case",
                        report_pk=report.pk)
                skipped += 1
                continue

            # A queryset update, rather than report.save(), to sidestep
            # DocumentReport.save()'s recount of number_of_matches: it assumes
            # update_fields is a set, so it would raise AttributeError on any
            # row whose stored count disagrees with a fresh recount.
            DocumentReport.objects.filter(pk=report.pk).update(container=container)
            attached += 1
        logger.info("sbsys container backfill complete",
                    attached=attached, skipped=skipped)
