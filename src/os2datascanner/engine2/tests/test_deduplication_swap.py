# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

import pytest

from os2datascanner.engine2.model.smbc import SMBCSource, SMBCHandle
from os2datascanner.engine2.model.derived.zip import ZipSource, ZipHandle
from os2datascanner.engine2.model.derived.pdf import PDFSource, PDFPageHandle
from os2datascanner.engine2.pipeline.utilities.deduplication import (
        decode_result, encode_result, swap_root)


SHARE = SMBCSource("//SERVER/Documents", "username")

# A share whose credentials the pipeline needs and the store must never see.
PASSWORD = "correct-horse-battery-staple"
SECURED_SHARE = SMBCSource("//SERVER/Personale", "username", PASSWORD, "DOMAIN")

# The same content in two places on one share: this is the case deduplication
# exists to exploit.
COPY_A = SMBCHandle(SHARE, "finance/report.pdf")
COPY_B = SMBCHandle(SHARE, "legal/report.pdf")


def page_of(pdf_handle, page):
    """Builds a Handle for a page of a PDF that is itself identified by a
    Handle."""
    return PDFPageHandle(PDFSource(pdf_handle), str(page))


def page_of_zipped(zip_handle, member, page):
    """Builds a Handle for a page of a PDF stored inside a Zip archive."""
    return page_of(ZipHandle(ZipSource(zip_handle), member), page)


class TestSwapRoot:
    def test_top_level_object_becomes_the_new_root(self):
        """A result belonging to the top-level object itself has no tree beneath
        it, so swapping its root just yields the other copy."""
        assert swap_root(COPY_A, COPY_A, COPY_B) == COPY_B

    def test_one_level_of_nesting(self):
        """Page 5 of one copy of a PDF becomes page 5 of the other copy."""
        swapped = swap_root(page_of(COPY_A, 5), COPY_A, COPY_B)

        assert swapped == page_of(COPY_B, 5)
        # The path within the container is untouched; only the object the tree
        # hangs from has changed.
        assert swapped.relative_path == "5"

    def test_two_levels_of_nesting(self):
        """The rebuild reaches the root through any number of derived Sources,
        so a page of a PDF inside a Zip works just as well."""
        zip_a = SMBCHandle(SHARE, "finance/archive.zip")
        zip_b = SMBCHandle(SHARE, "legal/archive.zip")

        swapped = swap_root(
                page_of_zipped(zip_a, "report.pdf", 5), zip_a, zip_b)

        assert swapped == page_of_zipped(zip_b, "report.pdf", 5)

    def test_every_page_of_a_document_swaps_consistently(self):
        """The interesting payload is a whole document's worth of pages, so
        check the rebuild holds across all of them rather than just one."""
        for page in range(1, 20):
            assert (swap_root(page_of(COPY_A, page), COPY_A, COPY_B)
                    == page_of(COPY_B, page))

    def test_unrelated_handle_is_a_bug(self):
        """Being asked to reroot a Handle that does not descend from the old
        root means the caller has paired up a result with the wrong object,
        which must not silently produce a plausible-looking Handle."""
        with pytest.raises(ValueError):
            swap_root(page_of(SMBCHandle(SHARE, "other.pdf"), 5),
                      COPY_A, COPY_B)

    def test_swapping_is_reversible(self):
        """Nothing about the rebuild is directional, so swapping back has to
        return the original Handle."""
        original = page_of(COPY_A, 3)
        there = swap_root(original, COPY_A, COPY_B)

        assert swap_root(there, COPY_B, COPY_A) == original


class TestResultRoundTrip:
    def test_results_replay_against_the_other_copy(self):
        """A result stored by the worker that converted one copy must come back
        out addressed to whichever copy replays it."""
        results = [
            (page_of(COPY_A, 1), False, []),
            (page_of(COPY_A, 4), True, [{"rule": "cpr", "matches": ["x"]}]),
        ]

        payload = encode_result(COPY_A, results)
        # The payload has to survive the trip through the store as JSON.
        replayed = list(decode_result(payload, COPY_B))

        assert [h for h, _, _ in replayed] == [
                page_of(COPY_B, 1), page_of(COPY_B, 4)]
        assert [m for _, m, _ in replayed] == [False, True]
        assert replayed[1][2] == [{"rule": "cpr", "matches": ["x"]}]

    def test_payload_is_json_serialisable(self):
        """The store keeps results as JSON, so anything that cannot be
        serialised has to fail here rather than at scan time."""
        import json

        payload = encode_result(COPY_A, [(page_of(COPY_A, 1), True, [])])

        assert json.loads(json.dumps(payload)) == payload

    def test_replay_carries_no_metadata(self):
        """Metadata describes a location rather than a piece of content, so it
        must not travel with a result to another location."""
        payload = encode_result(COPY_A, [(page_of(COPY_A, 1), True, [])])

        assert set(payload["results"][0]) == {"handle", "matched", "matches"}


class TestStoredHandlesAreCensored:
    """A Handle serialises its Source, and a Source carries whatever it needs to
    authenticate. The store is not the pipeline: results sit in it for a week,
    it has no TLS, and it is reachable by whatever else is on its network
    segment. So Handles go into it censored, exactly as they do on the way to
    the report module."""

    SECURED_A = SMBCHandle(SECURED_SHARE, "loen/report.pdf")
    SECURED_B = SMBCHandle(SECURED_SHARE, "hr/report.pdf")

    def payload(self):
        return encode_result(self.SECURED_A, [
            (self.SECURED_A, False, []),
            (page_of(self.SECURED_A, 4), True, [{"rule": "cpr"}]),
        ])

    def test_no_credential_reaches_the_store(self):
        import json

        assert PASSWORD not in json.dumps(self.payload())

    def test_every_handle_in_the_payload_is_censored(self):
        """Including the ones nested under the root, whose Sources are derived
        from it and carry it with them."""
        payload = self.payload()
        censored = SECURED_SHARE.censor().to_json_object()

        def sources(obj):
            """Every Source in a serialised Handle, at any depth."""
            while isinstance(obj, dict) and "source" in obj:
                yield (source := obj["source"])
                obj = source.get("handle")

        for handle in [payload["root"]] + [
                r["handle"] for r in payload["results"]]:
            found = list(sources(handle))
            assert found, f"no Source found in {handle}"
            # The outermost one is the share, and it is the only one that could
            # carry a credential: everything above it is derived from it.
            assert found[-1] == censored, found[-1]

    def test_a_censored_payload_still_replays_onto_the_live_object(self):
        """The comparisons that place a stored result in this worker's tree are
        between the payload's own Handles, so censoring them consistently
        leaves them agreeing with each other.

        What comes out is addressed to the live object this worker was handed,
        credentials and all, because it is that object rather than a stored one
        that has to be followed to collect metadata."""
        replayed = list(decode_result(self.payload(), self.SECURED_B))

        assert [h for h, _, _ in replayed] == [
                self.SECURED_B, page_of(self.SECURED_B, 4)]
        for handle, _, _ in replayed:
            outermost = list(handle.walk_up())[-1]
            assert outermost.source == SECURED_SHARE, (
                    "a replayed Handle cannot be followed: its Source came out"
                    " of the store rather than out of this scan")
