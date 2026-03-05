# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import structlog
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.contrib.auth.models import User
from django.conf import settings
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

from os2datascanner.projects.report.reportapp.models.documentreport import DocumentReport
from os2datascanner.utils.system_utilities import time_now

logger = structlog.get_logger("db_metric_pusher")

PUSHGATEWAY_HOST = settings.PUSHGATEWAY_HOST


class Command(BaseCommand):
    """Command used to send database related metrics to Prometheus Pushgateway."""

    help = __doc__

    def handle(self, *args, **options):
        registry = CollectorRegistry()

        report_gauge = Gauge(
            'osds_reports_total',
            'Total number of reports, with at least one match, per resolution status',
            ['status', 'is_withheld'],
            registry=registry
        )

        user_gauge = Gauge(
            'osds_users_total',
            'Total number of active users and their activity status the past 30 days',
            ['active_this_month'],
            registry=registry
        )

        logger.info("Collecting metric data")

        # Collect data related to DocumentReports
        reports_with_status = DocumentReport.objects.filter(
            number_of_matches__gte=1).values(
            'resolution_status',
            'only_notify_superadmin').annotate(
            total=Count('id'))

        resolution_choices = dict(DocumentReport.ResolutionChoices.choices)

        for report in reports_with_status:
            resolution_value = report['resolution_status']
            status_label = resolution_choices.get(resolution_value, "unhandled").lower()

            withheld_label = "true" if report['only_notify_superadmin'] else "false"

            report_gauge.labels(
                status=status_label,
                is_withheld=withheld_label).set(
                report['total'])

        # Collect data related to Users
        past_month = time_now() - timedelta(days=30)

        active_users_total = User.objects.filter(is_active=True).count()
        active_users_past_month = User.objects.filter(
            is_active=True, last_login__gte=past_month).count()

        user_gauge.labels(active_this_month="true").set(active_users_past_month)
        user_gauge.labels(
            active_this_month="false").set(
            active_users_total -
            active_users_past_month)

        # Push to gateway
        try:
            push_to_gateway(PUSHGATEWAY_HOST, job='push_db_metrics', registry=registry)
            logger.info("Metrics sent to Pushgateway")
        except Exception as ex:
            logger.error(f"Failed to push metrics: {ex}")
