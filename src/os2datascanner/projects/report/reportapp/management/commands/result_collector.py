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

import structlog
from django.db import transaction
from django.core.management.base import BaseCommand
from django.db.models import Q, Count

from os2datascanner.utils import debug
from os2datascanner.engine2.conversions.types import OutputType
from os2datascanner.engine2.model.core import (
        Handle, Source, UnknownSchemeError)
from os2datascanner.engine2.model.msgraph import MSGraphMailSource
from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.pipeline.utilities.pika import PikaPipelineThread
from os2datascanner.engine2.rules.last_modified import LastModifiedRule
from os2datascanner.projects.report.organizations.models import Alias, AliasType, Organization
from os2datascanner.utils.system_utilities import time_now
from prometheus_client import Summary, start_http_server


from ...models.documentreport import DocumentReport
from ...utils import prepare_json_object
from ....organizations.models import AccountOutlookSetting
from ...views.utilities.msgraph_utilities import outlook_settings_from_owner

logger = structlog.get_logger("result_collector")
SUMMARY = Summary("os2datascanner_result_collector_report",
                  "Messages through result collector report")

ResolutionChoices = DocumentReport.ResolutionChoices


def result_message_received_raw(body):
    """Method for restructuring and storing result body.

    The agreed structure is as follows:
    {'scan_tag': {...}, 'matches': null, 'metadata': null, 'problem': null}
    """
    reference = body.get("handle") or body.get("source")
    tag, queue = _identify_message(body)
    if not reference or not tag or not queue:
        extra_logger_args = {}
        match queue:
            case "os2ds_problem":
                extra_logger_args["problem_message"] = body["message"]

        logger.warning(
                "result_collector got an unidentifiable message, ignoring",
                reference=reference, tag=tag, queue=queue,
                **extra_logger_args)
        return

    tag = messages.ScanTagFragment.from_json_object(tag)

    # XXX: ideally we would only log once in this file. When all is done, log the
    # following AND what actions were taken.
    logger.debug(
        "msg received",
        queue=queue,
        tag=tag.scanner.to_json_object(),
        handle=Handle.from_json_object(reference).censor().to_json_object()
        if body.get("handle") else None,
        source=Source.from_json_object(reference).censor().to_json_object()
        if not body.get("handle") else None,
    )

    with transaction.atomic():
        if queue == "matches":
            handle_match_message(tag, body)
        elif queue == "problem":
            handle_problem_message(tag, body)
        elif queue == "metadata":
            yield from handle_metadata_message(tag, body)

    yield from []


def owner_from_metadata(message: messages.MetadataMessage) -> str:
    match message.metadata:
        case {"user-principal-name": upn}:
            return upn
        case {"email-account": addr} | {"msgraph-owner-account": addr}:
            return addr
        case {"filesystem-owner-sid": adsid}:
            return adsid
        case {"web-domain": domain}:
            return domain
        case _:
            return ""


def outlook_categorize_enabled(owner: str) -> bool:
    """ Checks if categorize_email is enabled for an account with an alias corresponding to owner
    value and verifies categories are created (creates them if needed)
     Returns bool"""
    aos = AccountOutlookSetting.objects.filter(account__email=owner,
                                               categorize_email=True)
    if not aos:
        return False

    aos_with_too_few_categories = aos.annotate(
        num_categories=Count('outlook_categories')).filter(num_categories__lt=2)

    if aos_with_too_few_categories:
        logger.warning(f"{owner} has too few categories! Trying to create them..")
        # populate_setting uses distinct(), which doesn't mix with annotating, so we have to filter
        # the original qs.
        aos.filter(pk__in=aos_with_too_few_categories.values('pk')).populate_setting()

    return aos.annotate(num_categories=Count('outlook_categories')
                        ).filter(num_categories__gte=2).exists()


def handle_metadata_message(scan_tag, result):
    # Evaluate the queryset that is updated later to lock it.
    message = messages.MetadataMessage.from_json_object(result)
    path = message.handle.crunch(hash=True)
    owner = owner_from_metadata(message)

    previous_report = DocumentReport.objects.select_for_update(
        of=('self',)
    ).filter(
        path=path,
        scanner_job_pk=scan_tag.scanner.pk
    ).first()

    resolution_status = None
    lm = None
    if "last-modified" in message.metadata:
        lm = OutputType.LastModified.decode_json_object(
                message.metadata["last-modified"])
    else:
        # If no scan_tag time is found, default value to current time as this
        # must be some-what close to actual scan_tag time.
        # If no datasource_last_modified value is ever set, matches will not be
        # shown.
        lm = scan_tag.time or time_now()

    # Specific to Outlook matches - if they have a "False Positive" category set, resolve them.
    outlook_categories = message.metadata.get("outlook-categories", [])
    settings = outlook_settings_from_owner(owner)
    if outlook_categories and settings and settings.false_positive_category:
        outlook_false_positive = (settings.false_positive_category.category_name in
                                  outlook_categories)
    else:
        outlook_false_positive = False

    # If the report is already handled as a false positive, keep it handled in that way.
    previous_false_positive = (scan_tag.scanner.keep_fp and previous_report and
                               previous_report.resolution_status ==
                               ResolutionChoices.FALSE_POSITIVE.value)
    if outlook_false_positive or previous_false_positive:
        resolution_status = ResolutionChoices.FALSE_POSITIVE.value

    dr, _ = DocumentReport.objects.update_or_create(
            path=path, scanner_job_pk=scan_tag.scanner.pk,
            defaults={
                "scan_time": scan_tag.time,
                "raw_scan_tag": prepare_json_object(
                        scan_tag.to_json_object()),

                "raw_metadata": prepare_json_object(result),
                "datasource_last_modified": lm,
                "scanner_job_name": scan_tag.scanner.name,
                "only_notify_superadmin": scan_tag.scanner.test,
                "resolution_status": resolution_status,
                "organization": get_org_from_scantag(scan_tag),
                "owner": owner,
            })

    # We've encountered an Outlook match that isn't categorized False Positive.
    if dr.source_type == MSGraphMailSource.type_label and not outlook_false_positive:
        if (settings := outlook_settings_from_owner(owner)) and outlook_categorize_enabled(owner):
            message_body = (dr.pk, settings.match_category.category_name)
            yield ("os2ds_email_tags", message_body)
            logger.debug(f"Enqueued categorize email request containing body: {message_body}")
        else:
            logger.debug(f"Categorizing mail not enabled for {owner}")

    create_aliases(dr)


def create_aliases(dr: DocumentReport):
    """ Given a DocumentReport, creates relevant alias-match relations.
    Though in most cases there'll be a One-To-One, multiple users can have
    identical aliases (think shared mailboxes or websites). Thus, relations are handled by
    bulk operations.
    """
    tm = Alias.match_relation.through
    new_objects = []
    owner = dr.owner
    try:
        metadata = dr.metadata
    except UnknownSchemeError:
        logger.error(f"failed to unpack metadata for {dr}", exc_info=True)
        return

    # Return early scenarios: No metadata yet, nothing to do.
    if not metadata:
        logger.warning(f"Create aliases invoked with a DocumentReport with no metadata: {dr}")
        return

    # Look for relevant alias(es) and append relation(s) to new_objects.
    aliases = (Alias.objects.filter(_value__iexact=owner)
               if owner else Alias.objects.none())
    # If there aren't any, we must look for remediators
    if not aliases:
        # Alias type must be remediator and value either 0 (all scannerjobs) or remediator
        # for this specific scannerjob.
        aliases = Alias.objects.filter(Q(_alias_type=AliasType.REMEDIATOR) &
                                       (Q(_value=0) | Q(_value=dr.scanner_job_pk)))
    else:
        # This means we've found an alias that fits the owner - delete remediator relations if any.
        tm.objects.filter(documentreport_id=dr.pk,
                          alias___alias_type=AliasType.REMEDIATOR).delete()

    add_new_relations(aliases, new_objects, dr, tm)

    try:
        # Bulk create relations as there might be more than one.
        tm.objects.bulk_create(new_objects, ignore_conflicts=True)
    except Exception:
        logger.error("Failed to create match_relation", exc_info=True)


def add_new_relations(aliases, new_objects, dr, tm):
    for alias in aliases:
        new_objects.append(
            tm(documentreport_id=dr.pk, alias_id=alias.pk))


def handle_match_message(scan_tag, result):  # noqa: CCR001, E501 too high cognitive complexity
    locked_qs = DocumentReport.objects.select_for_update(of=('self',))
    new_matches = messages.MatchesMessage.from_json_object(result)
    path = new_matches.handle.crunch(hash=True)
    # The queryset is evaluated and locked here.
    previous_report = (locked_qs.filter(
            path=path, scanner_job_pk=scan_tag.scanner.pk).order_by("-scan_time").first())

    matches = [(match.rule.presentation, match.matches) for match in new_matches.matches]
    logger.debug(
        "new matchMsg",
        handle=str(new_matches.handle),
        msgtype="matches",
        matches=matches,
    )
    if previous_report and previous_report.resolution_status is None:
        # There are existing unresolved results; resolve them based on the new
        # message
        if not new_matches.matched:
            # No new matches. Be cautiously optimistic, but check what
            # actually happened
            if (len(new_matches.matches) == 1
                and isinstance(new_matches.matches[0].rule,
                               LastModifiedRule)):
                # The file hasn't been changed, so the matches are the same
                # as they were last time. Instead of making a new entry,
                # just update the timestamp on the old one
                logger.debug("Resource not changed: updating scan timestamp",
                             report=previous_report)
                DocumentReport.objects.filter(pk=previous_report.pk).update(
                        scan_time=scan_tag.time,
                        # If there is a problem associated with this report, we
                        # no longer care about it
                        raw_problem=None)

                if previous_report.only_notify_superadmin != scan_tag.scanner.test:
                    # If the previous report doesn't have the same value for
                    # only_notify_superadmin as the new scan, update the report
                    DocumentReport.objects.filter(pk=previous_report.pk).update(
                        only_notify_superadmin=scan_tag.scanner.test)
            else:
                # The file has been edited and the matches are no longer
                # present
                logger.debug("Resource changed: no matches, status is EDITED",
                             report=previous_report)
                DocumentReport.objects.filter(pk=previous_report.pk).update(
                        resolution_status=ResolutionChoices.EDITED.value,
                        resolution_time=time_now(),
                        raw_problem=None)
        else:
            # The file has been edited, but matches are still present.
            # Resolve the previous ones
            logger.debug("matches still present, status is EDITED",
                         report=previous_report)
            DocumentReport.objects.filter(pk=previous_report.pk).update(
                    resolution_status=ResolutionChoices.EDITED.value,
                    resolution_time=time_now(),
                    raw_problem=None)

    if new_matches.matched:
        # Collect and store the top-level type label from the matched object
        source = new_matches.handle.source
        while source.handle:
            source = source.handle.source

        if (scan_tag.scanner.keep_fp and previous_report and
                previous_report.resolution_status == ResolutionChoices.FALSE_POSITIVE.value):
            new_status = ResolutionChoices.FALSE_POSITIVE.value
        else:
            new_status = None

        dr, _ = DocumentReport.objects.update_or_create(
                path=path, scanner_job_pk=scan_tag.scanner.pk,
                defaults={
                    "scan_time": scan_tag.time,
                    "raw_scan_tag": prepare_json_object(
                            scan_tag.to_json_object()),

                    "source_type": source.type_label,
                    "name": prepare_json_object(
                            new_matches.handle.presentation_name),
                    "sort_key": prepare_json_object(
                            new_matches.handle.sort_key),
                    "sensitivity": new_matches.sensitivity.value,
                    "probability": new_matches.probability,
                    "raw_matches": prepare_json_object(
                            sort_matches_by_probability(result)),
                    "scanner_job_name": scan_tag.scanner.name,
                    "only_notify_superadmin": scan_tag.scanner.test,
                    "resolution_status": new_status,
                    "organization": get_org_from_scantag(scan_tag),

                    "raw_problem": None,
                })

        logger.debug("matches, saved DocReport", report=dr)
        return dr
    else:
        logger.debug("No new matches.")
        return None


def sort_matches_by_probability(body):
    """The scanner engine have some internal rules
    and the matches they produce are also a part of the message.
    These matches are not necessary in the report module.
    An example of an internal rule is, images below a certain size are
    ignored."""

    # Rules are under no obligation to produce matches in any
    # particular order, but we want to display them in
    # descending order of probability
    for match_fragment in body["matches"]:
        if match_fragment["matches"]:
            match_fragment["matches"].sort(
                key=lambda match_dict: match_dict.get(
                    "probability", 0.0),
                reverse=True)
    return body


def handle_problem_message(scan_tag, result):
    locked_qs = DocumentReport.objects.select_for_update(of=('self',))
    problem = messages.ProblemMessage.from_json_object(result)
    obj = (problem.handle if problem.handle else problem.source)
    path = obj.crunch(hash=True)

    # Queryset is evaluated and locked here.
    previous_report = (locked_qs.filter(
            path=path, scanner_job_pk=scan_tag.scanner.pk).
            order_by("-scan_time").first())

    handle = problem.handle if problem.handle else None
    presentation = str(handle) if handle else "(source)"

    match (previous_report, problem):
        case (None, messages.ProblemMessage(missing=True)):
            # We've received a report that a resource is missing, but we have
            # nothing associated with it. Nothing to do
            logger.debug("Problem message of no relevance. Throwing away.")
            pass
        case (DocumentReport() as prev, messages.ProblemMessage(missing=True))\
                if prev.number_of_matches == 0:
            # A resource for which we only have a previous problem report has
            # been deleted. No need to keep the report.
            logger.debug(
                "Resource deleted, no previous matches, report deleted",
                report=previous_report,
                handle=presentation,
                msgtype="problem",
            )
            prev.delete()
        case (DocumentReport() as prev, messages.ProblemMessage(missing=True)) \
                if not prev.resolution_status:
            # A resource for which we have some unresolved reports has been
            # deleted.
            # If resolution status is "OTHER" or None: (I.e. 0 or None)
            # Mark it as removed and remove its raw_problem message.

            logger.debug(
                "Resource deleted, status is REMOVED",
                report=previous_report,
                handle=presentation,
                msgtype="problem",
            )
            DocumentReport.objects.filter(pk=prev.pk).update(
                resolution_status=ResolutionChoices.REMOVED.value,
                resolution_time=time_now(),
                raw_problem=None)
        case (DocumentReport() as prev,
              messages.ProblemMessage(missing=False)) if prev.resolution_status is not None:
            # A known resource, which isn't missing, has a problem, but has already been resolved.
            # Nothing to do, problem is not relevant anymore.
            if prev.scan_time == scan_tag.time:
                logger.warning(
                        "detected duplicated ProblemMessage for scan"
                        f" {scan_tag}: has the system been restarted?")
            else:
                logger.debug(
                        "Resource already resolved."
                        " Problem message of no relevance. ")
        case (DocumentReport() as prev,
              messages.ProblemMessage(missing=True)) if prev.resolution_status:
            # A resource for which we have some reports has been deleted, but
            # it's also been resolved. Nothing to do
            pass

        # (simple recap of the previous four cases for irrelevant=True)
        case (None, messages.ProblemMessage(irrelevant=True)):
            pass
        case (DocumentReport() as prev, messages.ProblemMessage(irrelevant=True)) \
                if prev.number_of_matches == 0:
            logger.debug(
                    "deleting as irrelevant contentless report",
                    report=prev, handle=presentation, msgtype="problem")
            prev.delete()
        case (DocumentReport() as prev, messages.ProblemMessage(irrelevant=True)) \
                if not prev.resolution_status:
            logger.debug(
                    "resource no longer relevant, status is IRRELEVANT",
                    report=prev, handle=presentation, msgtype="problem")
            DocumentReport.objects.filter(pk=prev.pk).update(
                    resolution_status=ResolutionChoices.IRRELEVANT.value,
                    resolution_time=time_now(),
                    raw_problem=None)
        case (DocumentReport() as prev, messages.ProblemMessage(irrelevant=True)) \
                if prev.resolution_status is not None:
            pass

        case (None, messages.ProblemMessage()):
            # A resource not previously known to us has a problem. Store it
            source = (
                    problem.handle.source
                    if problem.handle else problem.source)
            while source.handle:
                source = source.handle.source

            dr = DocumentReport.objects.create(
                    path=path,
                    scanner_job_pk=scan_tag.scanner.pk,

                    scan_time=scan_tag.time,
                    raw_scan_tag=prepare_json_object(
                            scan_tag.to_json_object()),

                    source_type=source.type_label,
                    name=prepare_json_object(
                            handle.presentation_name) if handle else "",
                    sort_key=prepare_json_object(
                            handle.sort_key if handle else "(source)"),
                    raw_problem=prepare_json_object(result),
                    scanner_job_name=scan_tag.scanner.name,
                    only_notify_superadmin=scan_tag.scanner.test,
                    resolution_status=None,
                    organization=get_org_from_scantag(scan_tag))

            logger.debug(
                "Unresolved, created new report",
                report=dr,
                handle=presentation,
                msgtype="problem",
            )
            return dr
        case (DocumentReport() as prev, messages.ProblemMessage()):
            # A resource known to us (either because of its matches or because
            # of a pre-existing problem) has a new problem, but we can't say
            # for sure that it's been deleted. Put the new problem in the
            # existing report
            DocumentReport.objects.filter(pk=prev.pk).update(
                    raw_problem=prepare_json_object(problem.to_json_object()))
            return prev


def _identify_message(result):
    origin = result.get('origin')

    if origin == 'os2ds_problems':
        return result.get("scan_tag"), "problem"
    elif origin == 'os2ds_metadata':
        return result.get("scan_tag"), "metadata"
    elif origin == "os2ds_matches":
        return result["scan_spec"].get("scan_tag"), "matches"
    else:
        return None, None


def get_org_from_scantag(scan_tag):
    return Organization.objects.filter(uuid=scan_tag.organisation.uuid).first()


class ResultCollectorRunner(PikaPipelineThread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        start_http_server(9091)

    def handle_message(self, routing_key, body):
        with SUMMARY.time():
            logger.debug(
                "raw message received",
                routing_key=routing_key,
                body=body)
            if routing_key == "os2ds_results":
                with transaction.atomic():
                    yield from result_message_received_raw(body)


class Command(BaseCommand):
    """Command for starting a result collector process."""
    help = __doc__

    def handle(self, *args, **options):
        debug.register_debug_signal()

        ResultCollectorRunner(
            read=["os2ds_results"],
            write=["os2ds_email_tags"],
            prefetch_count=8).run_consumer()
