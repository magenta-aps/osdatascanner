"""Remove all problems associated with non-existant scannerjobs in the
report module."""

from django.core.management.base import BaseCommand

from ...models.scannerjobs.scanner import Scanner
from ...utils import CleanProblemMessage
from ...models.rules import Rule


class Command(BaseCommand):

    help = __doc__

    def handle(self, *args, **options):

        # We need to clean up reports associated with scanners, which no longer
        # exist. We cannot query for deleted scanners, so instead, we figure
        # out which primary key is the next one, and then create a list of all
        # numbers less than that number, which is not currently in use as a pk.
        next_id = self.get_next_scanner_id()
        if next_id:
            in_use_ids = Scanner.objects.values_list('pk', flat=True)
            not_in_use_ids = [num for num in range(next_id) if num not in in_use_ids]

            self.stdout.write(f"Removing problems related to scanners: {not_in_use_ids}")

            CleanProblemMessage.send(not_in_use_ids, publisher="cleanup_problems")

    def get_next_scanner_id(self):
        """Creates a temporary Scanner, checks the primary key, then deletes it
        again."""

        try:
            dummy_scanner = Scanner.objects.create(name="dummy", rule_id=1)
        except Rule.DoesNotExist:
            self.stderr.write("No rules in the database, cannot create dummy scanner")
            return None
        pk = dummy_scanner.pk
        dummy_scanner.delete()

        return pk
