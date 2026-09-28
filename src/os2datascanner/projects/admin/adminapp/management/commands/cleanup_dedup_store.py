# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Delete claims and results left behind in the deduplication store.

This walks the keyspace rather than the per-scan indices, an index being one of
the things that can go missing, and deletes every key that does not belong to a
scan still running; --all deletes the lot.

Keys outside the three deduplication families are never touched, --all
included."""

from django.core.management.base import BaseCommand, CommandError

from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.pipeline.utilities import deduplication
from ...models.scannerjobs.scanner_helpers import ScanStatus


# The key families the store holds: a lease per in-flight conversion, a result
# per finished one, and the index a scan's own purge reads.
KEY_PREFIXES = ("claim:", "result:", "keys:")

# Keys per SCAN round trip and per UNLINK, matching ClaimStore.purge().
BATCH = 1000


def _scan_ids(queryset) -> set[str]:
    """The deduplication namespaces the scans in @queryset write under.

    A scan whose tag does not name both a scanner and a start time is left out:
    the pipeline does not coordinate over it, so it has no keys."""
    return {
            scan_id
            for tag in queryset.values_list("scan_tag", flat=True)
            if (scan_id := deduplication.scan_identity(
                    messages.ScanTagFragment.from_json_object(tag)))}


def _split(key: str) -> tuple[str, str] | None:
    """The family prefix of @key and what follows it, or None for a key
    belonging to something other than deduplication.

    That remainder is the scan identity for an index key, and the scan identity
    followed by the content key for a claim or a result."""
    for prefix in KEY_PREFIXES:
        if key.startswith(prefix):
            return prefix, key[len(prefix):]
    return None


def _under(namespace: str, scan_id: str) -> bool:
    """Whether @namespace belongs to the scan @scan_id names.

    Equality covers the index key, which is the scan identity and nothing
    else."""
    return namespace == scan_id or namespace.startswith(f"{scan_id}:")


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument(
                "--all",
                dest="everything",
                action="store_true",
                help="delete every deduplication key in the store, whichever"
                     " scan wrote it and whether or not that scan is still"
                     " running")
        parser.add_argument(
                "--scanner",
                metavar="PK",
                type=int,
                help="only consider keys written by scans of this scanner job",
                default=None)
        parser.add_argument(
                "--include-running",
                action="store_true",
                help="delete the keys of running scans as well, which costs"
                     " those scans the conversions they had shared")
        parser.add_argument(
                "--dry-run",
                action="store_true",
                help="report what would be deleted and delete nothing")

    def handle(  # noqa: CCR001 too high cognitive complexity
            self, everything, scanner, include_running, dry_run, *args,
            **options):
        if everything and (scanner is not None or include_running):
            raise CommandError(
                    "--all already covers --scanner and --include-running")

        conf = deduplication._dedup_settings()
        if (client := deduplication.build_client(conf)) is None:
            raise CommandError(
                    "no deduplication store configured: set"
                    " pipeline.worker.dedup.host")

        spared = set() if everything or include_running else _scan_ids(
                ScanStatus.objects.exclude(ScanStatus._completed_or_cancelled_Q))

        # Restricting to one scanner job is a prefix test of its own: a scan
        # identity opens with the scanner's primary key.
        wanted = f"{scanner}:" if scanner is not None else ""

        deleted = {prefix: 0 for prefix in KEY_PREFIXES}
        orphans = set()
        batch = []

        def flush():
            if batch and not dry_run:
                client.unlink(*batch)
            batch.clear()

        try:
            for raw in client.scan_iter(count=BATCH):
                key = raw.decode("utf-8", "replace") if isinstance(raw, bytes) else raw
                if (split := _split(key)) is None:
                    continue
                prefix, namespace = split
                if not namespace.startswith(wanted):
                    continue
                if any(_under(namespace, scan_id) for scan_id in spared):
                    continue

                deleted[prefix] += 1
                if prefix == "keys:":
                    # An index key is named by its scan and nothing else, so it
                    # is the one place an orphan's identity can be read off.
                    orphans.add(namespace)

                batch.append(raw)
                if len(batch) >= BATCH:
                    flush()
            flush()
        except Exception as ex:
            raise CommandError(f"could not reach the deduplication store: {ex}")

        total = sum(deleted.values())
        verb = "would delete" if dry_run else "deleted"
        self.stdout.write(
                f"{verb} {total} key(s): "
                + ", ".join(f"{deleted[p]} {p.rstrip(':')}" for p in KEY_PREFIXES))
        if spared:
            self.stdout.write(f"spared {len(spared)} running scan(s)")
        for scan_id in sorted(orphans):
            self.stdout.write(f"  {scan_id}")
