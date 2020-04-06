from os import getenv
import sys
from json import dumps, loads
import unittest
from multiprocessing import Process

from os2datascanner.engine2.model.core import Source
from os2datascanner.engine2.pipeline.utilities import PikaPipelineRunner

from os2datascanner.engine2.pipeline._consume_queue import main as cons_main
from os2datascanner.engine2.pipeline.explorer import main as expl_main
from os2datascanner.engine2.pipeline.processor import main as proc_main
from os2datascanner.engine2.pipeline.matcher import main as matc_main
from os2datascanner.engine2.pipeline.tagger import main as tagg_main
from os2datascanner.engine2.pipeline.exporter import main as expo_main


from .test_engine2_pipeline import (
        handle_message, data_url, rule, expected_matches)


class StopHandling(Exception):
    pass


class SubprocessPipelineTestRunner(PikaPipelineRunner):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.messages = {}

    def handle_message(self, message_body, *, channel=None):
        self.messages[message_body["origin"]] = message_body
        if len(self.messages) == 2:
            raise StopHandling()
        yield from []


class Engine2SubprocessPipelineTests(unittest.TestCase):
    def setUp(self):
        amqp_host = getenv("AMQP_HOST", "localhost")

        self.runner = SubprocessPipelineTestRunner(
                read=["os2ds_results"],
                write=["os2ds_scan_specs"],
                host=amqp_host,
                heartbeat=6000)

        consumer = Process(target=cons_main, args=[
                        "--host", amqp_host,
                        "os2ds_scan_specs", "os2ds_conversions",
                        "os2ds_representations", "os2ds_matches",
                        "os2ds_handles", "os2ds_metadata", "os2ds_problems",
                        "os2ds_results"])
        consumer.start()
        consumer.join()

        self.explorer = Process(target=expl_main, args=["--host", amqp_host])
        self.processor = Process(target=proc_main, args=["--host", amqp_host])
        self.matcher = Process(target=matc_main, args=["--host", amqp_host])
        self.tagger = Process(target=tagg_main, args=["--host", amqp_host])
        self.exporter = Process(target=expo_main, args=["--host", amqp_host])

        for p in (self.explorer, self.processor, self.matcher, self.tagger,
                self.exporter):
            p.start()

    def tearDown(self):
        self.runner.clear()
        for p in (self.explorer, self.processor, self.matcher, self.tagger,
                self.exporter):
            p.terminate()
            p.join()

    def test_simple_regex_match(self):
        print(Source.from_url(data_url).to_json_object())
        obj = {
            "scan_tag": "integration_test",
            "source": Source.from_url(data_url).to_json_object(),
            "rule": rule.to_json_object()
        }

        self.runner.channel.basic_publish(exchange='',
                routing_key="os2ds_scan_specs",
                body=dumps(obj).encode())

        try:
            self.runner.run_consumer()
        except StopHandling as e:
            self.assertTrue(
                    self.runner.messages["os2ds_matches"]["matched"],
                    "RegexRule match failed")
            self.assertEqual(
                    self.runner.messages["os2ds_matches"]["matches"],
                    expected_matches,
                    "RegexRule match did not produce expected result")
