import structlog
from os2datascanner.utils import debug
from django.core.management import BaseCommand
from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.pipeline.utilities.pika import PikaPipelineThread


from prometheus_client import Summary, start_http_server
from os2datascanner.engine2.model.msgraph import MSGraphMailMessageHandle
from os2datascanner.projects.grants.models.graphgrant import GraphGrant
from ...models.documentreport import DocumentReport
from ...views.utilities.msgraph_utilities import get_handle_from_document_report, \
    categorize_email_from_report

logger = structlog.get_logger("email_tagger")
SUMMARY = Summary("os2datascanner_email_tagger",
                  "Messages through os2ds_email_tags")


def get_grant(dr: DocumentReport) -> GraphGrant | None:
    try:
        return GraphGrant.objects.get(organization=dr.scanner_job.organization)
    except GraphGrant.DoesNotExist:
        logger.warning("No GraphGrant found! Can't categorize mail!")
    except GraphGrant.MultipleObjectsReturned:
        logger.warning("Too many GraphGrants found! Can't categorize mail!")
    return None


class EmailTaggerRunner(PikaPipelineThread):
    def __init__(self, source_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_manager = source_manager
        start_http_server(9091)

    def handle_message(self, routing_key, body):
        with SUMMARY.time():
            logger.debug(
                "raw message received",
                routing_key=routing_key,
                body=body)
            if routing_key == "os2ds_email_tags":
                dr_pk, category_to_add = body
                try:
                    document_report = DocumentReport.objects.get(pk=dr_pk)
                    mail_handle = get_handle_from_document_report(
                        document_report,
                        MSGraphMailMessageHandle)
                    mail_source = mail_handle.source

                    if not (graph_grant := get_grant(document_report)):
                        return

                    # We censor these when going through our pipeline, hence we need to set them
                    # again from settings.
                    mail_source.handle.source._client_id = graph_grant.app_id
                    mail_source.handle.source._client_secret = graph_grant.client_secret

                    # Use Source's source manager to reuse connection.
                    gc = self.source_manager.open(mail_source)
                    categorize_email_from_report(document_report,
                                                 category_to_add,
                                                 gc)

                except DocumentReport.DoesNotExist:
                    logger.warning("Can't categorize email, document report not found", dr_pk=dr_pk)

                yield from []


class Command(BaseCommand):
    """Starts an email tagger process."""
    help = __doc__

    def handle(self, *args, **options):
        debug.register_debug_signal()

        with SourceManager() as source_manager:
            EmailTaggerRunner(
                read=["os2ds_email_tags"],
                prefetch_count=8,
                source_manager=source_manager).run_consumer()
