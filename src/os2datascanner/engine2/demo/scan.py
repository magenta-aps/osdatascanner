"""A simple command-line interface to the OS2datascanner scanner engine."""

from json import loads
from uuid import uuid4
import click
from pathlib import Path

from os2datascanner.utils.system_utilities import time_now
from os2datascanner.engine2.model.core import Source, SourceManager
from os2datascanner.engine2.model.http import WebSource
from os2datascanner.engine2.rules.rule import Rule
from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.pipeline.explorer import (
        message_received_raw as explorer_mrr)
from os2datascanner.engine2.pipeline.worker import (
        message_received_raw as worker_mrr)
from os2datascanner.engine2.pipeline.exporter import (
        message_received_raw as exporter_mrr)


def scan(source, rule):
    print(":D")
    message = messages.ScanSpecMessage(
            scan_tag=messages.ScanTagFragment(
                    time=time_now(),
                    user=None,
                    scanner=messages.ScannerFragment(
                            pk=0,
                            name="CLI demand scan"),
                    organisation=messages.OrganisationFragment(
                            name="CLI",
                            uuid=uuid4())),
            source=source,
            rule=rule,
            filter_rule=None,
            configuration={},
            progress=None).to_json_object()

    with SourceManager() as sm:
        for c1, m1 in explorer_mrr(message, "os2ds_scan_specs", sm):
            if c1 in ("os2ds_conversions",):
                for c2, m2 in worker_mrr(m1, c1, sm):
                    if c2 in ("os2ds_matches",
                              "os2ds_metadata", "os2ds_problems",):
                        yield from (m3 for _, m3 in exporter_mrr(m2, c2, sm))
            elif c1 in ("os2ds_problems",):
                yield from (m2 for _, m2 in exporter_mrr(m1, c1, sm))


@click.group()
def cli():
    pass


@cli.command()
@click.option("-s", "--sitemap", default=None)
@click.argument("url")
@click.argument("rule",
        default='{"type": "cpr"}',
        type=lambda k: Rule.from_json_object(loads(k)))
def http(url, *, sitemap, rule):
    for message in scan(WebSource(url, sitemap=sitemap), rule):
        print(message)


@cli.command()
@click.argument("url")
@click.argument("rule",
        default='{"type": "cpr"}',
        type=lambda k: Rule.from_json_object(loads(k)))
def url(url, *, rule):
    for message in scan(Source.from_url(url), rule):
        print(message)


@cli.command()
@click.argument("source",
        type=lambda k: Source.from_json_object(loads(k)))
@click.argument("rule",
        default='{"type": "cpr"}',
        type=lambda k: Rule.from_json_object(loads(k)))
def json(source, *, rule):
    for message in scan(source, rule):
        print(message)


if __name__ == "__main__":
    for _, m in cli():
        print(m.to_json_object())
