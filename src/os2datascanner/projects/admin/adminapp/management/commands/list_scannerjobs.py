#!/usr/bin/env python
# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from django.core.management import BaseCommand

from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner import (
    Scanner, ScanStatus, ScheduledCheckup, )


class Command(BaseCommand):
    """
        This command lists all scanner jobs and the following attributes:
        PK
        Name
        Start time
        Number of objects scanned
        Scan status as bool
        Checkup messages as count()
    """

    help = "List all scannerjobs and some of their attributes."

    def handle(self, *args, **options):
        self.list_scannerjobs()

    def list_scannerjobs(self):
        scannerjobs = {}
        for scannerjob in Scanner.objects.select_subclasses().all():
            pk = scannerjob.pk
            name = scannerjob.name
            start_time = None
            scanned_objects = None
            scan_status = None
            cancelled = None
            check_up_msgs = ScheduledCheckup.objects.filter(scanner=scannerjob.pk).count()
            msg = ""

            if ScanStatus.objects.filter(scanner=scannerjob.pk).exists():
                # We are only interested in the most recent ScanStatus object,
                # but there's likely more than one, hence we filter .last()
                scan_status_obj = ScanStatus.objects.filter(scanner=scannerjob.pk).last()

                start_time = scan_status_obj.start_time
                scanned_objects = scan_status_obj.scanned_objects
                scan_status = scan_status_obj.finished
                cancelled = scan_status_obj.cancelled
                msg = scan_status_obj.message

            self.stdout.write(self.style.SUCCESS(
                f'\nScanner PK: {pk} \nScanner Name: {name} \n'
                f'Scan Type: {scannerjob.get_type()} \n'
                f'Start Time: {start_time} \nScanned Objects: {scanned_objects} \n'
                f'Scan Status Finished(T/F): {scan_status} \n'
                f'Scan Status Cancelled(T/F): {cancelled} \n'
                f'Check-up Msg Obj Count: {check_up_msgs}\n'
                f'message: {msg}\n'))
            scannerjobs[name] = {
                "pk": pk,
                "name": name,
                "start_time": start_time,
                "scanned_objects": scanned_objects}
        return scannerjobs
