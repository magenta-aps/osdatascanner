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
from django.db import IntegrityError, transaction
from django.core.management.base import BaseCommand
from django.db.transaction import TransactionManagementError
from rest_framework.serializers import ValidationError
from os2datascanner.utils import debug
from os2datascanner.core_organizational_structure.utils import get_serializer
from os2datascanner.engine2.pipeline.utilities.pika import PikaPipelineThread
from os2datascanner.projects.report.organizations.models import (Account, Alias, Organization,
                                                                 OrganizationalUnit, Position)
from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport
from prometheus_client import Summary, start_http_server
from ...utils import create_alias_and_match_relations

logger = structlog.get_logger("event_collector")
SUMMARY = Summary("os2datascanner_event_collector_report",
                  "Messages through event collector report")

# OBS: Must be updated if new org-structure models are added,
# or if the order of which creation/deletion is possible changes.
ORDER_OF_CREATION = (Organization, OrganizationalUnit, Account, Alias, Position)
ORDER_OF_DELETION = list(reversed(ORDER_OF_CREATION))


def event_message_received_raw(body):  # noqa: CCR001 C901
    event_type = body.get("type")
    classes = body.get("classes")
    try:
        with transaction.atomic():
            if event_type == "bulk_event_create":
                logger.info("Initiating broadcast create transaction...")
                for model in ORDER_OF_CREATION:
                    serializer = get_serializer(model)
                    if raw_model_data := classes.get(model.__name__):
                        serialized_objects = serializer(data=raw_model_data, many=True)
                        logger.info("Serializing and attempting to create objects of",
                                    model=model.__name__)

                        # Exception raised from is_valid will be a rest_framework ValidationError,
                        # we catch that below and return to abort transaction if one is raised.
                        serialized_objects.is_valid(raise_exception=True)
                        serialized_objects.save()
                        logger.info("Successfully ran broadcast create!")

                    else:
                        logger.info("No objects to create of", model=model.__name__)

            elif event_type == "bulk_event_update":
                logger.info("Initiating broadcast update transaction...")
                for model in ORDER_OF_CREATION:
                    pk_list = []
                    serializer = get_serializer(model)
                    if raw_model_data := classes.get(model.__name__):
                        logger.info("Received instructions to bulk update objects of",
                                    model=model.__name__)

                        for instance in raw_model_data:
                            # OBS: In this case we're converting pks to str
                            # We do that to support both type UUID and int in our sorting function.
                            pk_list.append(str(instance.get("pk")))

                        objects_to_update = model.objects.filter(pk__in=pk_list)

                        # We have to be careful, there is no guarantee that we're getting
                        # objects from the database in the same order as raw_model_data.
                        # Sort that out here, before passing objects on to the serializer.
                        objects_to_update = sorted(
                            objects_to_update,
                            key=lambda x: pk_list.index(str(x.pk))
                        )

                        serialized_objects = serializer(objects_to_update,
                                                        data=raw_model_data, many=True)

                        serialized_objects.is_valid(raise_exception=True)
                        serialized_objects.save()

                        if model == Alias:
                            # TODO: move it to alias manager?
                            for alias_obj in serialized_objects.validated_data:
                                create_alias_and_match_relations(
                                    Alias.objects.get(pk=alias_obj.get("pk")))

                        logger.info("Successfully ran broadcast update!")
                    else:
                        logger.info("Nothing to update for", model=model.__name__)

            elif event_type == "bulk_event_delete":
                for model in ORDER_OF_DELETION:
                    if model.__name__ in classes:
                        model.objects.filter(pk__in=classes.get(model.__name__)).delete()
                        logger.info("Deleted instances of", model=model.__name__,
                                    count=len(classes.get(model.__name__))
                                    )

            elif event_type == "bulk_event_purge_all":
                for model in ORDER_OF_DELETION:
                    if model.__name__ in classes:
                        deleted = model.objects.all().delete()
                        logger.info("Deleting all objects of",
                                    model=model.__name__, count=deleted)

            elif event_type == "clean_document_reports":
                handle_clean_account_message(body)
            elif event_type == "clean_problem_reports":
                handle_clean_problem_message(body)

            yield from []

    except ValidationError:
        logger.warning("Error in serialized object!",
                       model=model.__name__, error=serialized_objects.errors)

    except TransactionManagementError:
        logger.exception("Transaction Management Error! \n"
                         "You'll likely need to purge before retrying!")
    except IntegrityError:
        logger.exception("Integrity Error! \n "
                         "Some objects probably already exist! \n"
                         "You'll likely need to purge before retrying!")


def handle_clean_account_message(body):
    """Accepts a CleanAccountMessage JSON-object, and deletes all document reports
    related to the given account and scanner job."""
    logger.info("CleanAccountMessage published by",
                publisher=body.get('publisher'), published_time=body.get('time'))

    data_struct = body.get("scanners_accounts_dict", {})

    for scanner_pk, account_dict in data_struct.items():
        account_uuids = account_dict.get("uuids")
        account_usernames = account_dict.get("usernames")

        related_reports = DocumentReport.objects.filter(
            alias_relation__account__in=account_uuids, scanner_job_pk=scanner_pk)

        _, deleted_reports_dict = related_reports.delete()
        deleted_reports = deleted_reports_dict.get("os2datascanner_report.DocumentReport", 0)

        logger.info(
            "Deleted DocumentReport objects!",
            count=deleted_reports, scanner_job_pk=scanner_pk,
            associated_accounts=', '.join(account_usernames))


def handle_clean_problem_message(body):
    """Accepts a CleanProblemMessage JSON-object, and deletes all problem reports
    related to the given scannerjob pks."""
    logger.info("CleanProblemMessage published by",
                publisher=body.get('publisher'), published_time=body.get('time'))

    scanners = body.get("scanners", [])

    related_problems = DocumentReport.objects.filter(
        number_of_matches=0, scanner_job_pk__in=scanners)
    _, deleted_problems_dict = related_problems.delete()
    deleted_problems = deleted_problems_dict.get(
        "os2datascanner_report.DocumentReport", 0)

    logger.info(
        "Deleted DocumentReport objects without matches ",
        count=deleted_problems, scanner_job_pk=scanners)


class EventCollectorRunner(PikaPipelineThread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        start_http_server(9091)

    def handle_message(self, routing_key, body):
        with SUMMARY.time():
            logger.debug(
                "Event collector received a raw message ",
                routing_key=routing_key,
                body=body)
            if routing_key == "os2ds_events":
                yield from event_message_received_raw(body)


class Command(BaseCommand):
    """Command for starting an event collector process."""
    help = __doc__

    def handle(self, *args, **options):
        debug.register_debug_signal()

        EventCollectorRunner(
            read=["os2ds_events"],
            prefetch_count=8).run_consumer()
