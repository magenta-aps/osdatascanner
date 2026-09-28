# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""End-to-end test of the deduplication protocol through the real worker.

Two identical files in two places go through worker.message_received_raw exactly
as a delivery from the conversion queue would, with a real claim store behind it.
The tests prove reuse rather than inferring it, because this feature's
characteristic failure is silently doing nothing while every component reports
healthy."""

import json
import os
from datetime import datetime, timezone
import shutil
import tempfile

import pytest

from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.model.file import FilesystemHandle, FilesystemSource
from os2datascanner.engine2.pipeline import messages, worker
from os2datascanner.engine2.pipeline.utilities import deduplication, sharing
from os2datascanner.engine2.conversions.types import OutputType
from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules.last_modified import LastModifiedRule
from os2datascanner.engine2.rules.logical import AndRule
from os2datascanner.engine2.rules.meta import HasConversionRule

# Big enough to clear the cost gate, and holding a CPR number so the scan has
# something to find. The number is the one the project's other fixtures use.
CONTENT = ("Sagsbehandler noter. Borgerens CPR er 1111111118.\n"
           + "Udfyldningstekst for at give filen en realistisk stoerrelse.\n"
           * 4000)


@pytest.fixture
def store(dedup_client):
    store = deduplication.ClaimStore(
            dedup_client, lease_ms=60000, result_ttl=60, owner="test-worker")
    # Install it as the process-wide store, which is what the worker consults.
    deduplication._store = store
    deduplication._store_resolved = True
    yield store
    deduplication.reset_store()


@pytest.fixture
def two_copies():
    """One scan over two identical files in two directories, standing in for one
    document found in two places.

    Yields the ScanSpecMessage both copies belong to."""
    root = tempfile.mkdtemp()
    for folder in ("finance", "legal"):
        os.makedirs(os.path.join(root, folder))
        with open(os.path.join(root, folder, "report.txt"), "w") as fp:
            fp.write(CONTENT)

    source = FilesystemSource(root)
    yield messages.ScanSpecMessage(
            scan_tag=messages.ScanTagFragment.make_dummy(),
            source=source, rule=CPRRule(), configuration={},
            filter_rule=None, progress=None)

    shutil.rmtree(root, ignore_errors=True)


def conversion_message(scan_spec, folder):
    """Builds the message the explorer would emit for one copy of the document.

    Both copies must carry the *same* scan_spec, because results are namespaced
    per scan: two messages built with their own scan tags would land in two
    separate key spaces and could never share anything, however identical their
    content. That is a property of the design, not an accident of it, so the
    scan_spec is passed in rather than made here."""
    # The size hint matters: the cost gate uses it to decide whether an object is
    # expensive enough to coordinate over, so without it nothing here would be
    # coordinated at all. Real explorers attach it (file.py, smbc.py).
    handle = FilesystemHandle(
            scan_spec.source, f"{folder}/report.txt",
            hints={"size": len(CONTENT)})
    return messages.ConversionMessage(
            scan_spec=scan_spec, handle=handle,
            progress=messages.ProgressFragment(
                    rule=scan_spec.rule, matches=[]))


def run(message, sm):
    """Pushes one message through the worker exactly as a delivery would be,
    returning the (queue, body) pairs it produced."""
    body = message.to_json_object()
    return list(worker.message_received_raw(body, "os2ds_conversions", sm))


def matches_in(emitted):
    return [body for queue, body, *_ in emitted if queue == "os2ds_matches"]


class TestTwoCopiesOfOneDocument:
    def test_the_first_copy_converts_and_publishes_a_result(
            self, store, two_copies):
        """A completed conversion leaves something behind for the other
        copies, which everything else here depends on."""
        with SourceManager() as sm:
            emitted = run(conversion_message(two_copies, "finance"), sm)

        assert matches_in(emitted), "no matches produced at all"

        keys = [k.decode() for k in store._client.scan_iter("result:*")]
        assert len(keys) == 1, f"expected one stored result, got {keys}"

        # And it is a real result, not the "do not wait for me" marker.
        payload = deduplication._unpack(store._client.get(keys[0]))
        assert not deduplication.is_unshareable(payload), (
                f"winner published nothing usable: {payload}")
        assert payload["results"], "stored result contains no rule results"

    def test_both_locations_report_against_their_own_object(
            self, store, two_copies):
        """Deduplication changes how a representation was obtained, never
        whether a location gets reported."""
        with SourceManager() as sm:
            first = run(conversion_message(two_copies, "finance"), sm)
            second = run(conversion_message(two_copies, "legal"), sm)

        assert matches_in(first), "first copy produced no matches"
        assert matches_in(second), "second copy produced no matches"

        first_paths = [m["handle"]["path"] for m in matches_in(first)]
        second_paths = [m["handle"]["path"] for m in matches_in(second)]

        assert all("finance/" in p for p in first_paths), first_paths
        assert all("legal/" in p for p in second_paths), second_paths

    def test_the_second_copy_really_reuses_the_stored_result(
            self, store, two_copies):
        """Proves reuse rather than inferring it.

        Asserting that the second copy reported matches proves nothing on its
        own: it would report matches just as happily by converting the file
        again. So a marker is planted in the stored result between the two runs,
        and findings carrying it demonstrably came out of the store."""

        sentinel = "SENTINEL-PLANTED-IN-THE-STORE"

        with SourceManager() as sm:
            run(conversion_message(two_copies, "finance"), sm)

            keys = [k.decode() for k in store._client.scan_iter("result:*")]
            assert len(keys) == 1, f"nothing stored to reuse: {keys}"

            payload = deduplication._unpack(store._client.get(keys[0]))
            planted = False
            for result in payload["results"]:
                for fragment in result["matches"]:
                    for match in fragment["matches"] or ():
                        match["match"] = sentinel
                        planted = True
            assert planted, f"stored result had no matches to mark: {payload}"
            store._client.set(keys[0], deduplication._pack(payload))

            second = run(conversion_message(two_copies, "legal"), sm)

        assert sentinel in json.dumps(matches_in(second)), (
                "the second copy converted the file again instead of reusing"
                " the stored result")

    def test_both_copies_find_the_same_thing(self, store, two_copies):
        """Reuse must not change what is reported: identical content has to
        produce identical findings whichever path produced them."""
        with SourceManager() as sm:
            first = run(conversion_message(two_copies, "finance"), sm)
            second = run(conversion_message(two_copies, "legal"), sm)

        def matched_flags(emitted):
            return sorted(m["matched"] for m in matches_in(emitted))

        assert matched_flags(first) == matched_flags(second)

    def test_the_second_copy_does_not_take_a_claim(self, store, two_copies):
        """A copy that reuses a result must not claim anything: claiming would
        block nobody and achieve nothing, and a leftover claim would stall the
        next copy for a whole lease period."""
        with SourceManager() as sm:
            run(conversion_message(two_copies, "finance"), sm)
            run(conversion_message(two_copies, "legal"), sm)

        claims = list(store._client.scan_iter("claim:*"))
        assert claims == [], f"claim left behind: {claims}"


class TestAResultThatCannotBeRead:
    """A stored result is input from outside this process: written by another
    worker, which may be running another build with other Handle and Rule types
    registered, and possibly sitting in a shared store for a week. A copy that
    cannot read one has to convert instead."""

    def plant(self, store, two_copies, sm, payload):
        """Puts @payload where the "legal" copy will find it, and returns that
        copy's message."""

        message = conversion_message(two_copies, "legal")
        identity = deduplication.identify(message.handle, message.handle.follow(sm))
        assert identity is not None, "could not identify the test document"

        key = deduplication.content_key(
                str(identity), message.to_json_object()["progress"])
        store._client.set(
                f"result:{deduplication.scan_identity(two_copies.scan_tag)}"
                f":{key}",
                deduplication._pack(payload))
        return message

    def test_an_undecodable_result_does_not_stop_the_object_being_scanned(
            self, store, two_copies):
        """The payload is well-formed JSON of the right shape, so nothing
        catches it before the Handles inside it are deserialised. Letting that
        failure out would abandon the delivery unacked, and the redelivered copy
        would find the same unreadable result and fail the same way."""
        with SourceManager() as sm:
            message = self.plant(store, two_copies, sm, {
                "root": {"type": "a-handle-from-a-later-version", "path": "x"},
                "results": [],
            })

            emitted = run(message, sm)

        assert matches_in(emitted), (
                "the object was not scanned at all after an unreadable result")

    def test_a_truncated_result_does_not_stop_the_object_being_scanned(
            self, store, two_copies):
        """The other shape of the same problem: valid JSON that simply does not
        have the fields a result has."""
        with SourceManager() as sm:
            message = self.plant(store, two_copies, sm, {"results": []})

            emitted = run(message, sm)

        assert matches_in(emitted), (
                "the object was not scanned at all after a truncated result")


class TestAResultThatCannotBeWritten:
    """Packing a result is the one step on the winner's path that the store's
    own error handling does not cover, and it runs after the object has already
    been converted successfully. Letting a failure out there would abandon the
    delivery unacked and stop the worker, so a scan would lose a worker to a
    problem in the bookkeeping rather than in the scanning."""

    @pytest.fixture
    def unpackable(self, monkeypatch):
        def explode(*args, **kwargs):
            raise ValueError("this result cannot be packed")

        monkeypatch.setattr(deduplication, "encode_result", explode)

    def test_the_object_is_still_scanned_and_reported(
            self, store, two_copies, unpackable):
        with SourceManager() as sm:
            emitted = run(conversion_message(two_copies, "finance"), sm)

        assert matches_in(emitted), (
                "the winner's own findings were lost when packing failed")

    def test_the_other_copies_are_told_to_convert(
            self, store, two_copies, unpackable):
        """Storing nothing at all would leave the other copies cycling through
        the deferral queues until their budget ran out, waiting for a result
        that is never coming."""
        with SourceManager() as sm:
            run(conversion_message(two_copies, "finance"), sm)

        keys = [k.decode() for k in store._client.scan_iter("result:*")]
        assert len(keys) == 1, f"expected one stored marker, got {keys}"
        assert deduplication.is_unshareable(
                deduplication._unpack(store._client.get(keys[0])))

    def test_the_other_copy_converts_and_reports(
            self, store, two_copies, unpackable):
        with SourceManager() as sm:
            run(conversion_message(two_copies, "finance"), sm)
            second = run(conversion_message(two_copies, "legal"), sm)

        assert matches_in(second), "the second copy was left with nothing"
        assert all(
                "legal/" in m["handle"]["path"] for m in matches_in(second))


class TestAnIncrementalScanOfATopLevelObject:
    """An incremental scan asks a LastModifiedRule of an object before it asks
    anything about content, and answers it from the object's own metadata. The
    content question that follows is the one a full scan asks first, and an
    object reached directly from the explorer must be coordinated over it just
    as an object inside a container is."""

    @pytest.fixture
    def incremental(self, two_copies):
        """The same two copies, scanned the way a scanner that has run before
        scans them: every production scan has this shape, the last-modified
        check being on by default."""
        return messages.replace(
                two_copies,
                rule=AndRule.make(
                        LastModifiedRule(
                                datetime(2000, 1, 1, tzinfo=timezone.utc)),
                        CPRRule()))

    def test_the_content_hop_is_coordinated(self, store, incremental):
        with SourceManager() as sm:
            run(conversion_message(incremental, "finance"), sm)

        keys = [k.decode() for k in store._client.scan_iter("result:*")]
        assert len(keys) == 1, (
                f"the content hop was left uncoordinated: {keys}")

    def test_the_second_copy_reuses_it(self, store, incremental):
        with SourceManager() as sm:
            run(conversion_message(incremental, "finance"), sm)
            second = run(conversion_message(incremental, "legal"), sm)

        assert matches_in(second), "the second copy reported nothing"
        assert not [k for k in store._client.scan_iter("claim:*")], (
                "the second copy took a claim of its own instead of reusing"
                " the result that was waiting for it")


class TestACancelledScanStoresNothing:
    """The order that cancels a scan also purges its keys, so a worker that
    publishes on the way out writes into a key space the purge has already been
    through, where it sits until the result TTL with nobody left to read it."""

    @pytest.fixture
    def cancelled_mid_conversion(self, monkeypatch, two_copies):
        """Cancels the scan as the last of the conversion's messages goes past,
        so the capture loop ends of its own accord instead of aborting: the
        abort check is only reached between messages."""
        original = sharing.capture_matches

        def cancel_on_the_way_out(generator, capture):
            yield from original(generator, capture)
            worker.notify_abort(two_copies.scan_tag)

        monkeypatch.setattr(sharing, "capture_matches", cancel_on_the_way_out)
        yield
        worker._cancelled_tags.discard(two_copies.scan_tag)

    def test_no_result_is_published(
            self, store, two_copies, cancelled_mid_conversion):
        with SourceManager() as sm:
            run(conversion_message(two_copies, "finance"), sm)

        keys = [k.decode() for k in store._client.scan_iter("result:*")]
        assert not keys, f"a cancelled scan published {keys}"

    def test_the_claim_is_given_up(
            self, store, two_copies, cancelled_mid_conversion):
        with SourceManager() as sm:
            run(conversion_message(two_copies, "finance"), sm)

        keys = [k.decode() for k in store._client.scan_iter("claim:*")]
        assert not keys, f"the claim outlived the conversion it protected: {keys}"


class TestSyntheticRulesAreNotStored:
    """Synthetic rules are the pipeline's internal tests: is this image big
    enough to be worth OCRing, did this object convert to text at all. Nothing
    that reads a result counts or displays them, and one fragment per image per
    internal test is what turns the stored result for a document full of images
    into mostly padding."""

    @pytest.fixture
    def with_an_internal_test(self, two_copies):
        """The same scan, asking a question that carries a synthetic rule
        alongside the real one.

        HasConversionRule operates on Text, which is derived from content, so a
        tree containing it is still one whose conclusions may be shared."""
        rule = AndRule(HasConversionRule(OutputType.Text), CPRRule())
        assert any(leaf.synthetic for leaf in rule.flatten()), (
                "this test needs a rule tree with a synthetic leaf in it")
        assert deduplication.is_shareable(rule), (
                "a tree that is not shareable would never be stored at all")

        return messages.replace(two_copies, rule=rule)

    def stored_payload(self, store):
        keys = [k.decode() for k in store._client.scan_iter("result:*")]
        assert len(keys) == 1, f"expected one stored result, got {keys}"
        return deduplication._unpack(store._client.get(keys[0]))

    def stored_fragments(self, store):
        """The fragments of a stored result, with each rule looked up in the
        pool its fragments refer to it by index in."""
        payload = self.stored_payload(store)
        rules = payload["rules"]

        return [
            fragment | {"rule": rules[fragment["rule"]]}
            for result in payload["results"]
            for fragment in result["matches"]]

    def test_the_internal_test_is_left_out_of_the_stored_result(
            self, store, with_an_internal_test):
        with SourceManager() as sm:
            run(conversion_message(with_an_internal_test, "finance"), sm)

        fragments = self.stored_fragments(store)
        stored_rules = [f["rule"]["type"] for f in fragments]

        assert stored_rules, "nothing at all was stored"
        assert "conversion" not in stored_rules, stored_rules
        assert not any(
                f["rule"].get("synthetic") for f in fragments), stored_rules

    def test_the_real_rule_is_kept(self, store, with_an_internal_test):
        """Stripping the internal tests must not strip the findings beside
        them."""
        with SourceManager() as sm:
            run(conversion_message(with_an_internal_test, "finance"), sm)

        assert any(
                f["rule"]["type"] == "cpr" and f["matches"]
                for f in self.stored_fragments(store)), (
                self.stored_fragments(store))

    def test_one_rule_is_stored_once_however_many_fragments_use_it(
            self, store, with_an_internal_test):
        """What the pool is for: a result holds a fragment per rule per page,
        image and archive member, and a rule serialises to a few hundred bytes
        of its own."""
        with SourceManager() as sm:
            run(conversion_message(with_an_internal_test, "finance"), sm)

        payload = self.stored_payload(store)
        pool = payload["rules"]

        assert len(pool) == len({json.dumps(r, sort_keys=True) for r in pool}), (
                f"the pool holds the same rule more than once: {pool}")
        assert all(
                isinstance(fragment["rule"], int)
                for result in payload["results"]
                for fragment in result["matches"]), (
                "a rule was stored inline rather than pooled")

    def test_the_other_copy_still_reports_the_finding(
            self, store, with_an_internal_test):
        """What the report module makes of a replayed result has to be what it
        would have made of a converted one, and it counts and displays only the
        rules that are not synthetic."""
        with SourceManager() as sm:
            run(conversion_message(with_an_internal_test, "finance"), sm)
            second = run(conversion_message(with_an_internal_test, "legal"), sm)

        reported = matches_in(second)
        assert reported, "the second copy reported nothing"
        assert any(
                fragment["rule"]["type"] == "cpr" and fragment["matches"]
                for body in reported
                for fragment in body["matches"]), reported
        assert all(body["matched"] for body in reported), reported
