import sys
import unittest
import subprocess

from os2datascanner.engine2.commands.utils import DemoSourceUtility as TestSourceUtility
from os2datascanner.engine2.pipeline.utilities import pika
from .test_pipeline import (data_url, rule, expected_matches)
from .test_pipeline_rabbitmq import (StopHandling, PipelineTestRunner)


def python(*args):
    """Starts a new instance of this Python interpreter with the specified
    arguments. Standard output and standard error will be passed through."""
    return subprocess.Popen([sys.executable, *args])


class Engine2SubprocessPipelineTests(unittest.TestCase):
    def setUp(self):

        self.runner = PipelineTestRunner(
                read=["os2ds_results"],
                write=["os2ds_scan_specs"],
                heartbeat=6000)

        with pika.PikaConnectionHolder() as clearer:
            for channel_name in (
                    "os2ds_scan_specs",
                    "os2ds_conversions",
                    "os2ds_matches",
                    "os2ds_metadata",
                    "os2ds_problems",
                    "os2ds_results",):
                clearer.channel.queue_purge(channel_name)

        self.explorer = python(
                "-m", "os2datascanner.engine2.pipeline.explorer")
        self.worker = python(
            "-m", "os2datascanner.engine2.pipeline.worker")
        self.exporter = python(
                "-m", "os2datascanner.engine2.pipeline.exporter")

    def tearDown(self):
        self.runner.clear()
        for p in (self.explorer, self.worker, self.exporter):
            p.kill()
            p.wait()

    def test_simple_regex_match(self):
        jsonobj = TestSourceUtility.from_url(data_url).to_json_object()
        print(jsonobj)
        obj = {
            "scan_tag": {
                "scanner": {
                    "name": "integration_test",
                    "pk": 0,
                    "test": False,
                },
                "time": "2020-01-01T00:00:00+00:00",
                "user": None,
                "organisation": "Vejstrand Kommune"
            },
            "source": jsonobj,
            "rule": rule.to_json_object()
        }

        self.runner.enqueue_message("os2ds_scan_specs", obj)

        try:
            self.runner.run_consumer()
        except StopHandling:
            self.assertTrue(
                    self.runner.messages["os2ds_matches"]["matched"],
                    "RegexRule match failed")
            self.assertEqual(
                    self.runner.messages["os2ds_matches"]["matches"],
                    expected_matches,
                    "RegexRule match did not produce expected result")
