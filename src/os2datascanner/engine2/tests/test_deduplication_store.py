# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Tests for the claim protocol, run against a real store.

The interesting behaviour here is all in the store's atomicity guarantees -- that
exactly one of two simultaneous claims succeeds, and that a lease can only be
touched by the worker holding it -- so a fake store would test nothing but the
fake. The tests skip themselves when no store is reachable."""

import gzip
import json
import time

import pytest

from os2datascanner.engine2.pipeline.utilities import deduplication
from os2datascanner.engine2.pipeline.utilities.deduplication import ClaimStore

redis = pytest.importorskip("redis")

LEASE_MS = 60000


@pytest.fixture
def worker_a(dedup_client):
    return ClaimStore(
            dedup_client, lease_ms=LEASE_MS, result_ttl=60, owner="worker-a")


@pytest.fixture
def worker_b(dedup_client):
    return ClaimStore(
            dedup_client, lease_ms=LEASE_MS, result_ttl=60, owner="worker-b")


SCAN = "17:2026-08-14T08:00:00"
CID = "a" * 64


class TestClaims:
    def test_only_one_worker_takes_a_claim(self, worker_a, worker_b):
        """The whole point: two copies dispatched at the same moment must not
        both convert."""
        assert worker_a.claim(SCAN, CID) is True
        assert worker_b.claim(SCAN, CID) is False

    def test_claims_are_per_content(self, worker_a, worker_b):
        """Holding a claim on one piece of content must not block another."""
        assert worker_a.claim(SCAN, CID) is True
        assert worker_b.claim(SCAN, "b" * 64) is True

    def test_claims_are_per_scan(self, worker_a, worker_b):
        """Nothing is shared between scans, so the same content in a different
        scan is a different claim."""
        assert worker_a.claim(SCAN, CID) is True
        assert worker_b.claim("18:2026-08-14T09:00:00", CID) is True

    def test_releasing_frees_the_claim(self, worker_a, worker_b):
        assert worker_a.claim(SCAN, CID) is True
        worker_a.release(SCAN, CID)

        assert worker_b.claim(SCAN, CID) is True

    def test_a_worker_cannot_release_another_worker_s_claim(
            self, worker_a, worker_b):
        """A worker that finishes late, after its lease expired and another
        worker took over, must not delete the new holder's claim: that would put
        a third copy into conversion alongside it."""
        assert worker_a.claim(SCAN, CID) is True

        worker_b.release(SCAN, CID)

        assert worker_b.claim(SCAN, CID) is False

    def test_an_expired_claim_can_be_retaken(self, dedup_client, worker_b):
        """A worker that dies mid-conversion stops renewing, and the claim has
        to become available again. This is what bounds the cost of a crash to a
        single lease period."""
        dying = ClaimStore(
                dedup_client, lease_ms=250, result_ttl=60, owner="dying-worker")
        assert dying.claim(SCAN, CID) is True
        assert worker_b.claim(SCAN, CID) is False

        time.sleep(0.4)

        assert worker_b.claim(SCAN, CID) is True

    def test_renewing_keeps_a_claim_alive(self, dedup_client, worker_b):
        """The counterpart: a worker that is still working keeps its claim, so
        the short lease does not let a second worker in while the first is
        making progress."""
        working = ClaimStore(
                dedup_client, lease_ms=400, result_ttl=60, owner="working-worker")
        assert working.claim(SCAN, CID) is True

        for _ in range(4):
            time.sleep(0.15)
            working.renew(SCAN, CID)

        assert worker_b.claim(SCAN, CID) is False

    def test_a_worker_cannot_renew_another_worker_s_claim(
            self, dedup_client, worker_b):
        """A late worker must not be able to extend a lease it no longer owns,
        which would let it hold the claim indefinitely after taking over."""
        original = ClaimStore(
                dedup_client, lease_ms=250, result_ttl=60, owner="original")
        assert original.claim(SCAN, CID) is True
        time.sleep(0.4)
        assert worker_b.claim(SCAN, CID) is True

        original.renew(SCAN, CID)
        original.release(SCAN, CID)

        # worker_b's claim survived both attempts by the previous holder.
        assert ClaimStore(
                dedup_client, lease_ms=LEASE_MS, result_ttl=60,
                owner="worker-c").claim(SCAN, CID) is False


class TestResults:
    def test_a_result_is_visible_to_another_worker(self, worker_a, worker_b):
        worker_a.store_result(SCAN, CID, {"root": {}, "results": []})

        assert worker_b.get_result(SCAN, CID) == {"root": {}, "results": []}

    def test_no_result_reads_as_a_miss(self, worker_b):
        assert worker_b.get_result(SCAN, CID) is None

    def test_a_result_outlives_the_claim(self, worker_a, worker_b):
        """Results have to survive the claim being released, because that is the
        ordering the protocol relies on: the copies that were deferred while the
        conversion ran find the result once it is done."""
        worker_a.claim(SCAN, CID)
        worker_a.store_result(SCAN, CID, {"root": {}, "results": [1]})
        worker_a.release(SCAN, CID)

        assert worker_b.get_result(SCAN, CID) == {"root": {}, "results": [1]}

    def test_reading_a_result_renews_it(self, dedup_client):
        """A result still being used must not age out.

        A scan can run for longer than any expiry worth configuring, so if the
        clock ran from when a result was written, a long scan would lose its own
        results midway through and send every remaining copy off to convert
        content it had already converted."""
        short = ClaimStore(
                dedup_client, lease_ms=60000, result_ttl=2, owner="worker-a")
        short.store_result(SCAN, CID, {"root": {}, "results": [1]})

        # Read it repeatedly across a span longer than the expiry.
        for _ in range(4):
            time.sleep(0.6)
            assert short.get_result(SCAN, CID) is not None

        assert short.get_result(SCAN, CID) == {"root": {}, "results": [1]}

    def test_reading_a_result_renews_the_index(self, dedup_client):
        """Renewal has to cover the index as well as the result.

        A result kept alive by replays alone would otherwise outlive the index
        purge() finds it through, and would sit in the store for another whole
        expiry period holding the match contexts of a scan that is over."""
        short = ClaimStore(
                dedup_client, lease_ms=60000, result_ttl=2, owner="worker-a")
        short.store_result(SCAN, CID, {"root": {}, "results": [1]})

        # Read it repeatedly across a span longer than the expiry, writing
        # nothing: replaying a stored result is the only traffic this key sees.
        for _ in range(4):
            time.sleep(0.6)
            assert short.get_result(SCAN, CID) is not None

        assert short.purge(SCAN) == 1, "the index lost track of a live result"
        assert list(dedup_client.scan_iter("*")) == []

    def test_an_unused_result_still_expires(self, dedup_client):
        """The counterpart: renewal on use must not turn the expiry off, or the
        store would fill with results from scans that finished long ago."""
        short = ClaimStore(
                dedup_client, lease_ms=60000, result_ttl=1, owner="worker-a")
        short.store_result(SCAN, CID, {"root": {}, "results": [1]})

        time.sleep(1.4)

        assert short.get_result(SCAN, CID) is None

    def test_unreadable_result_is_a_miss(self, dedup_client, worker_b):
        """Garbage in the store must send the worker down the convert-it-myself
        path rather than raising."""
        dedup_client.set(f"result:{SCAN}:{CID}", b"{not json")

        assert worker_b.get_result(SCAN, CID) is None


class TestHowAResultIsStored:
    """A result is compressed on the way in, which halves what an ordinary one
    costs and takes far more than that off a container's, whose entries repeat.

    Nothing outside the store knows the format, so what is pinned here is that
    it survives the round trip, that it is really compressed, and that a store
    holding either form stays readable."""

    PAYLOAD = {
        "root": {"type": "filesystem", "path": "finance/report.txt"},
        "rules": [{"type": "cpr", "modulus_11": True,
                   "blacklist": ["cvr", "tlf", "faknr", "ordrenr"]}],
        "results": [
            {"handle": {"type": "filesystem", "path": f"page-{i}.txt"},
             "matched": True,
             "matches": [{"rule": 0, "matches": [{
                 "match": "1111XXXXXX", "offset": 31, "probability": 1.0,
                 "context": "Sagsbehandler noter. Borgerens CPR er"
                            " XXXXXX-XXXX. Udfyldningstekst",
                 "context_offset": 31}]}]}
            for i in range(5)],
    }

    def test_a_result_survives_the_round_trip(self, worker_a):
        worker_a.store_result(SCAN, CID, self.PAYLOAD)

        assert worker_a.get_result(SCAN, CID) == self.PAYLOAD

    def test_what_lands_in_the_store_is_compressed(
            self, dedup_client, worker_a):
        """Losing the compression would cost memory rather than correctness, so
        nothing else here would notice."""
        worker_a.store_result(SCAN, CID, self.PAYLOAD)

        stored = dedup_client.get(f"result:{SCAN}:{CID}")
        assert stored[:2] == b"\x1f\x8b", stored[:16]
        assert len(stored) < len(json.dumps(self.PAYLOAD)) / 2

    def test_a_result_stored_as_plain_json_is_still_read(
            self, dedup_client, worker_b):
        """What a worker running a build from before this was left behind, and
        what an operator poking at the store by hand would write."""
        dedup_client.set(f"result:{SCAN}:{CID}", json.dumps(self.PAYLOAD))

        assert worker_b.get_result(SCAN, CID) == self.PAYLOAD

    def test_a_result_that_arrived_cut_short_is_a_miss(
            self, dedup_client, worker_b):
        """Half a compressed payload has to read as "convert it yourself" like
        any other unreadable one, rather than raising."""
        packed = deduplication._pack(self.PAYLOAD)
        dedup_client.set(f"result:{SCAN}:{CID}", packed[:len(packed) // 2])

        assert worker_b.get_result(SCAN, CID) is None

    def test_a_result_with_a_corrupt_body_is_a_miss(
            self, dedup_client, worker_b):
        """The failure a cut-short payload does not reach: an intact gzip header
        and trailer around a body that will not inflate, which raises zlib.error
        rather than the OSError or EOFError the other damaged forms raise."""
        packed = deduplication._pack(self.PAYLOAD)
        # 10-byte header, 8-byte CRC and length trailer, nothing in between that
        # the decompressor can make sense of.
        dedup_client.set(
                f"result:{SCAN}:{CID}",
                packed[:10] + bytes(len(packed) - 18) + packed[-8:])

        assert worker_b.get_result(SCAN, CID) is None

    def test_a_result_that_is_not_an_object_is_a_miss(
            self, dedup_client, worker_b):
        """Readable JSON that is not a result. The callers read one by asking it
        questions, so a list answering them would raise far from the store."""
        dedup_client.set(
                f"result:{SCAN}:{CID}", gzip.compress(b'["not", "a", "result"]'))

        assert worker_b.get_result(SCAN, CID) is None

    def test_a_payload_compression_would_grow_is_stored_as_it_is(
            self, dedup_client, worker_a):
        """The marker saying not to wait is 21 bytes of JSON and 41 gzipped."""
        worker_a.store_result(SCAN, CID, deduplication.UNSHAREABLE_RESULT)

        assert dedup_client.get(f"result:{SCAN}:{CID}")[:1] == b"{"
        assert deduplication.is_unshareable(worker_a.get_result(SCAN, CID))


class TestPurgingAFinishedScan:
    """Every key is namespaced by the scan, so once a scan is over none of them
    can be read again by anything. They hold match contexts, so they should not
    be left to expire on their own."""

    def populate(self, store, scan_id, n=3):
        for i in range(n):
            assert store.claim(scan_id, f"cid-{i}")
            store.store_result(scan_id, f"cid-{i}", {"results": [], "n": i})

    def test_everything_the_scan_left_behind_goes(self, worker_a, dedup_client):
        self.populate(worker_a, "finished")

        purged = worker_a.purge("finished")

        assert purged == 6, "expected three claims and three results"
        assert list(dedup_client.scan_iter("*")) == []

    def test_another_scan_is_untouched(self, worker_a, dedup_client):
        self.populate(worker_a, "finished")
        self.populate(worker_a, "still-running")

        worker_a.purge("finished")

        assert worker_a.get_result("still-running", "cid-1") is not None
        assert not worker_a.claim("still-running", "cid-1"), (
                "another scan's claim was purged with this one's")

    def test_purging_a_scan_that_left_nothing_is_fine(self, worker_a):
        assert worker_a.purge("never-ran") == 0

    def test_purging_does_not_walk_the_store(self, worker_a, monkeypatch):
        """The order to clear up is broadcast, so every worker purges the same
        scan at the same moment. A keyspace walk each would cost the store more
        than the scan it is cleaning up after did."""
        self.populate(worker_a, "finished")

        def explode(*args, **kwargs):
            raise AssertionError("purge walked the whole keyspace")

        monkeypatch.setattr(worker_a._client, "scan_iter", explode)

        assert worker_a.purge("finished") == 6

    def test_purging_twice_is_fine(self, worker_a):
        self.populate(worker_a, "finished")

        assert worker_a.purge("finished") == 6
        assert worker_a.purge("finished") == 0


class TestUnreachableStore:
    """Every operation has to degrade to "convert it yourself" when the store
    cannot be reached, so that a broken store costs throughput and never
    correctness."""

    @pytest.fixture
    def unreachable(self):
        c = redis.Redis(
                host="203.0.113.1", port=6379, db=0,
                socket_timeout=0.25, socket_connect_timeout=0.25)
        return ClaimStore(c, lease_ms=LEASE_MS, result_ttl=60, owner="lonely")

    def test_claim_succeeds_so_the_work_still_happens(self, unreachable):
        """If a failed claim read as "someone else has it", every worker would
        wait for a conversion that nobody is doing."""
        assert unreachable.claim(SCAN, CID) is True

    def test_result_lookup_is_a_miss(self, unreachable):
        assert unreachable.get_result(SCAN, CID) is None

    def test_renew_release_and_store_do_not_raise(self, unreachable):
        unreachable.renew(SCAN, CID)
        unreachable.store_result(SCAN, CID, {"root": {}, "results": []})
        unreachable.release(SCAN, CID)
