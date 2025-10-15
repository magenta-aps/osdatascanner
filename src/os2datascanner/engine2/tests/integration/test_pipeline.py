from io import BytesIO
import os.path
from copy import deepcopy
import base64
from zipfile import ZipFile
import unittest

from os2datascanner.engine2.commands.utils import DemoSourceUtility as TestSourceUtility
from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.model.file import FilesystemSource
from os2datascanner.engine2.rules.rule import Sensitivity
from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules.regex import RegexRule
from os2datascanner.engine2.rules.logical import OrRule
from os2datascanner.engine2.pipeline import (
        explorer, processor, matcher, tagger, exporter, worker, messages)


here_path = os.path.dirname(__file__)
test_data_path = os.path.join(here_path, "..", "data")


data = """Hwæt! wē Gār-Dena in gēar-dagum
þēod-cyninga þrym gefrūnon,
hū ðā æþeling as ell en fremedon.
Oft Scyld Scēfing sceaþena þrēatum,
monegum mǣgþum meodo-setla oftēah."""
encoded_data = data.encode("utf-8")
data_url = "data:text/plain;base64,{0}".format(
       base64.encodebytes(encoded_data).decode("ascii"))

rule = OrRule(
        RegexRule("Æthelred the Unready", name="Check for ill-advised kings"),
        RegexRule("(Scyld) (?:S.*g)", sensitivity=Sensitivity.CRITICAL),
        RegexRule("Professor James Moriarty"))

expected_matches = [
    {
        "rule": {
            "type": "regex",
            "sensitivity": None,
            "synthetic": False,
            "name": "Check for ill-advised kings",
            "expression": "Æthelred the Unready"
        },
        "matches": None
    },
    {
        "rule": {
            "type": "regex",
            "sensitivity": Sensitivity.CRITICAL.value,
            "synthetic": False,
            "name": None,
            "expression": "(Scyld) (?:S.*g)"
        },
        "matches": [
            {
                "match": "Scyld Scēfing",

                "offset": 98,
                # context is 50 char before and after the match(13 char)
                "context":
                    "m gefrūnon, hū ðā æþeling as ell en fremedon. Oft XXXXX"
                    " Scēfing sceaþena þrēatum, monegum mǣgþum meodo-setla"
                    " oftē",
                "context_offset": 50,
                "sensitivity": Sensitivity.CRITICAL.value,
            }
        ]
    }
]


raw_scan_spec = {
    "scan_tag": {
        "scanner": {
            "name": "integration_test",
            "pk": 0,
            "test": False,
        },
        "user": None,
        "organisation": "Vejstrand Kommune",
        "time": "2020-01-01T00:00:00+00:00"
    },
    "source": TestSourceUtility.from_url(
        data_url).to_json_object(),
    "rule": rule.to_json_object()
}


class StopHandling(Exception):
    pass


def handle_message(body, channel):
    with SourceManager() as sm:
        if channel == "os2ds_scan_specs":
            yield from explorer.message_received_raw(body, channel, sm)
        elif channel == "os2ds_conversions":
            yield from processor.message_received_raw(body, channel, sm)
        elif channel == "os2ds_representations":
            yield from matcher.message_received_raw(body, channel, sm)
        elif channel == "os2ds_handles":
            yield from tagger.message_received_raw(body, channel, sm)
        elif channel in ("os2ds_matches", "os2ds_metadata", "os2ds_problems"):
            yield from exporter.message_received_raw(body, channel, sm)
        # "os2ds_status" messages get dropped on the floor


def handle_message_worker(body, channel, *, stat_dict=None):
    with SourceManager() as sm:
        if channel == "os2ds_scan_specs":
            yield from explorer.message_received_raw(body, channel, sm)
        elif channel == "os2ds_conversions":
            yield from worker.message_received_raw(body, channel, sm)
        elif channel in ("os2ds_matches", "os2ds_metadata", "os2ds_problems"):
            yield from exporter.message_received_raw(body, channel, sm)
        elif channel == "os2ds_status" and stat_dict is not None:
            message = messages.StatusMessage.from_json_object(body)
            for k in ("total_objects", "object_size",):
                value = getattr(message, k)
                if value is not None:
                    if k not in stat_dict:
                        stat_dict[k] = 0
                    stat_dict[k] += value


class Engine2PipelineTests(unittest.TestCase):
    def setUp(self):
        self.messages = []
        self.unhandled = []

    def run_pipeline(self, runner=handle_message, **runner_kwargs):
        while self.messages:
            (body, channel), self.messages = self.messages[0], self.messages[1:]
            if channel != "os2ds_results":
                for c, b in runner(body, channel, **runner_kwargs):
                    self.messages.append((b, c,))
            else:
                self.unhandled.append((body, channel,))

    def test_simple_regex_match(self):
        self.messages.append((raw_scan_spec, "os2ds_scan_specs",))
        self.run_pipeline()

        self.assertEqual(
                len(self.unhandled),
                2)
        results = {body["origin"]: body for body, _ in self.unhandled}

        self.assertTrue(
                results["os2ds_matches"]["matched"],
                "RegexRule match failed")
        self.assertEqual(
                results["os2ds_matches"]["matches"],
                expected_matches,
                "RegexRule match did not produce expected result")

    def test_simple_regex_match_with_worker(self):
        self.messages.append((raw_scan_spec, "os2ds_scan_specs",))

        stat_dict = {}

        self.run_pipeline(runner=handle_message_worker, stat_dict=stat_dict)

        self.assertEqual(
                len(self.unhandled),
                2)
        results = {body["origin"]: body for body, _ in self.unhandled}

        self.assertTrue(
                results["os2ds_matches"]["matched"],
                "RegexRule match failed")
        self.assertEqual(
                results["os2ds_matches"]["matches"],
                expected_matches,
                "RegexRule match did not produce expected result")

    def test_unsupported_sources(self):
        obj = deepcopy(raw_scan_spec)
        obj["source"] = {
            "type": "forbidden-knowledge",
            "of": ["good", "evil"]
        }

        self.messages.append((obj, "os2ds_scan_specs",))
        self.run_pipeline()

        self.assertEqual(
                len(self.unhandled),
                1)
        self.assertEqual(
                self.unhandled[0][0]["origin"],
                "os2ds_problems")

    def test_ocr_skip(self):
        obj = deepcopy(raw_scan_spec)
        obj["source"] = (
                FilesystemSource(os.path.join(
                        test_data_path, "ocr", "good")
                ).to_json_object())
        obj["rule"] = (
                CPRRule(
                        modulus_11=False, ignore_irrelevant=False
                ).to_json_object())
        obj["configuration"] = {
            "skip_mime_types": ["image/*"]
        }

        self.messages.append((obj, "os2ds_scan_specs",))
        self.run_pipeline()

        for message, queue in self.unhandled:
            if queue == "os2ds_results":
                self.assertFalse(
                    message["matched"],
                    "OCR match found with OCR disabled")
            else:
                self.fail("unexpected message in queue {0}".format(queue))

    def test_corrupted_container(self):
        obj = deepcopy(raw_scan_spec)
        obj["source"] = (
                FilesystemSource(
                        os.path.join(test_data_path, "pdf", "corrupted")
                ).to_json_object())
        obj["rule"] = (
                CPRRule(
                        modulus_11=False, ignore_irrelevant=False
                ).to_json_object())

        self.messages.append((obj, "os2ds_scan_specs",))
        self.run_pipeline()

        self.assertEqual(
                len(self.unhandled),
                1)
        self.assertEqual(
                self.unhandled[0][0]["origin"],
                "os2ds_problems")

    def test_rule_crash(self):
        obj = deepcopy(raw_scan_spec)
        obj["rule"] = {
            "type": "buggy"
        }

        self.messages.append((obj, "os2ds_scan_specs",))
        self.run_pipeline()

        self.assertEqual(
                len(self.unhandled),
                1)
        self.assertEqual(
                self.unhandled[0][0]["origin"],
                "os2ds_problems")

    def test_zip_worker(self):
        obj = deepcopy(raw_scan_spec)

        bio = BytesIO()
        with ZipFile(bio, "w") as zf:
            zf.writestr("dummy.txt", encoded_data)
        bio.seek(0)

        content = base64.encodebytes(bio.read())
        obj["source"] = TestSourceUtility.from_url(
                "data:application/zip;base64," + content.decode("ascii")
        ).to_json_object()

        stat_dict = {}

        self.messages.append((obj, "os2ds_scan_specs",))
        self.run_pipeline(handle_message_worker, stat_dict=stat_dict)

        results = {body["origin"]: body for body, _ in self.unhandled}
        self.assertTrue(
                results["os2ds_matches"]["matched"],
                "RegexRule match failed")
        self.assertEqual(
                results["os2ds_matches"]["matches"],
                expected_matches,
                "RegexRule match did not produce expected result")

        self.assertEqual(
                stat_dict["total_objects"],
                1,
                "incorrect scanned object count")
