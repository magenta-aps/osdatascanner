# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""End-to-end test of coordination over content found inside a container.

One document in two different archives goes through worker.message_received_raw
exactly as a delivery from the conversion queue would, with a real claim store
behind it. The containers differ, so nothing about them can be shared: whatever
is reused here was reused for the document inside them.

An object inside a container never reaches the worker's entry point, so it is
coordinated in a different place and, having nowhere to wait, stands down in a
different way. Both are tested here."""

import email.message
import json
import os
import shutil
import tempfile
import zipfile

import pytest

from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.model.derived.mail import MailSource
from os2datascanner.engine2.model.derived.zip import ZipHandle, ZipSource
from os2datascanner.engine2.model.file import FilesystemHandle, FilesystemSource
from os2datascanner.engine2.pipeline import messages, worker
from os2datascanner.engine2.pipeline.utilities import deduplication
from os2datascanner.engine2.pipeline.utilities.stage import dispatch
from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules.last_modified import LastModifiedRule
from os2datascanner.engine2.rules.logical import AndRule
from os2datascanner.engine2.utilities.datetime import parse_datetime

MEMBER = "shared/report.txt"

SIGNATURE = os.path.join(
        os.path.dirname(__file__), "data", "ocr", "good", "cpr.png")

# The document both archives hold. Big enough to clear the cost gate below, and
# holding a CPR number so the scan has something to find.
CONTENT = ("Sagsbehandler noter. Borgerens CPR er 1111111118.\n"
           + "Udfyldningstekst for at give filen en realistisk stoerrelse.\n"
           * 4000)


@pytest.fixture
def gate():
    """Pins the cost gate so that the document qualifies and the archives
    holding it do not.

    Which side of it each one falls on is what this file is about, so it is
    pinned here rather than left to whatever the deployment is configured
    with."""
    conf = deduplication._dedup_settings()
    saved = dict(conf)
    conf.update({"min_size": 65536, "always_types": []})
    yield conf
    conf.clear()
    conf.update(saved)


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
def two_archives(gate):
    """One scan over two archives holding one identical document.

    Each archive also holds a file the other does not, so that they are not
    themselves two copies of one thing: what is reused here was reused for the
    document."""
    root = tempfile.mkdtemp()
    for name, filler in (("alpha.zip", "alpha"), ("beta.zip", "beta")):
        # Deflated, so that the archive falls below the cost gate that the
        # document inside it clears.
        with zipfile.ZipFile(
                os.path.join(root, name), "w",
                compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(MEMBER, CONTENT)
            zf.writestr(f"{filler}/notes.txt", f"only in {filler}\n")

    yield messages.ScanSpecMessage(
            scan_tag=messages.ScanTagFragment.make_dummy(),
            source=FilesystemSource(root), rule=CPRRule(), configuration={},
            filter_rule=None, progress=None)

    shutil.rmtree(root, ignore_errors=True)


@pytest.fixture
def two_mails(gate):
    """One scan over two mails carrying one identical attachment.

    Nothing else about them is shared, so what is reused here was reused for the
    attachment."""
    root = tempfile.mkdtemp()
    for name, subject in (("one.eml", "Fordelt"), ("two.eml", "Videresendt")):
        mail = email.message.EmailMessage()
        mail["Subject"] = subject
        mail["From"] = "sagsbehandler@example.invalid"
        mail["To"] = f"{name}@example.invalid"
        mail["Message-ID"] = f"<{name}@example.invalid>"
        mail.set_content("Se venligst vedhaeftede.\n")
        mail.add_attachment(
                CONTENT.encode("utf-8"),
                maintype="text", subtype="plain", filename="report.txt")
        with open(os.path.join(root, name), "wb") as fp:
            fp.write(mail.as_bytes())

    yield messages.ScanSpecMessage(
            scan_tag=messages.ScanTagFragment.make_dummy(),
            source=FilesystemSource(root), rule=CPRRule(), configuration={},
            filter_rule=None, progress=None)

    shutil.rmtree(root, ignore_errors=True)


@pytest.fixture
def two_signed_mails(gate):
    """Two unrelated mails carrying one identical signature image.

    Their subjects and bodies differ and neither has an attachment, so the image
    is the only thing they have in common."""
    gate["always_types"] = ["image/*"]

    with open(SIGNATURE, "rb") as fp:
        signature = fp.read()

    root = tempfile.mkdtemp()
    for name, subject, body in (
            ("one.eml", "Fordelt", "Se venligst sagen.\n"),
            ("two.eml", "Videresendt", "Til orientering, jf. nedenstaaende.\n")):
        mail = email.message.EmailMessage()
        mail["Subject"] = subject
        mail["From"] = "sagsbehandler@example.invalid"
        mail["To"] = f"{name}@example.invalid"
        mail["Message-ID"] = f"<{name}@example.invalid>"
        mail.set_content(body)
        mail.add_attachment(
                signature, maintype="image", subtype="png", cid="<signature>")
        with open(os.path.join(root, name), "wb") as fp:
            fp.write(mail.as_bytes())

    yield messages.ScanSpecMessage(
            scan_tag=messages.ScanTagFragment.make_dummy(),
            source=FilesystemSource(root),
            # The number in the image does not survive a modulus-11 check, so
            # the rule has to be one that does not make it.
            rule=CPRRule(modulus_11=False), configuration={},
            filter_rule=None, progress=None)

    shutil.rmtree(root, ignore_errors=True)


def part_handle(scan_spec, mail, sm, pick):
    """The one part of one of the mails that @pick accepts.

    Found by walking the mail rather than by building its Handle here: a Handle
    assembled by hand that differed from the real one in any detail would key
    differently and quietly test nothing."""
    source = MailSource(conversion_message(scan_spec, mail).handle)
    handles = [h for h in source.handles(sm) if pick(h)]
    assert len(handles) == 1, f"could not find the part: {handles}"

    return handles[0]


def part_key(scan_spec, mail, sm, pick):
    """The key under which that part's conversion is claimed and stored."""
    handle = part_handle(scan_spec, mail, sm, pick)
    identity = identify(handle, sm)
    assert identity is not None, f"could not identify {handle}"

    return deduplication.content_key(
            str(identity), progress_of(scan_spec).to_json_object())


def part_digest(scan_spec, mail, sm, pick):
    """The digest of the content of one part of one of the mails.

    Stored keys are matched on this rather than on the whole content key: the
    key also carries the question being asked of the content, and an incremental
    scan has answered part of that question by the time the part is reached."""
    identity = identify(part_handle(scan_spec, mail, sm, pick), sm)
    assert identity is not None, "could not identify the part"

    return identity.digest


def is_the_attachment(handle):
    return handle.relative_path.endswith("report.txt")


def is_the_signature(handle):
    return handle.guess_type() == "image/png"


def progress_of(scan_spec):
    """The progress fragment the explorer would attach to an archive.

    It reaches the document inside untouched: the processor hands its own
    fragment to the Source it reinterprets the archive as (see
    handle_conversion_key_error), and the explorer moves that onto every object
    it finds there."""
    return messages.ProgressFragment(rule=scan_spec.rule, matches=[])


def conversion_message(scan_spec, archive):
    """Builds the message the explorer would emit for one of the archives."""
    # The size hint is what the cost gate reads. Real explorers attach it
    # (file.py, smbc.py), and the archives are far smaller than the document
    # they hold, this content being about as compressible as content gets.
    handle = FilesystemHandle(
            scan_spec.source, archive,
            hints={"size": os.path.getsize(
                    os.path.join(scan_spec.source.path, archive))})
    return messages.ConversionMessage(
            scan_spec=scan_spec, handle=handle,
            progress=progress_of(scan_spec))


def member_handle(scan_spec, archive):
    """A Handle for the shared document inside one of the archives, as the
    explorer would build it while walking that archive."""
    return ZipHandle(
            ZipSource(conversion_message(scan_spec, archive).handle), MEMBER,
            hints={"size": len(CONTENT)})


def identify(handle, sm):
    """What deduplication makes of an object's content.

    Identities are memoised for the length of a delivery, so a test that asks
    twice about one object gets the same answer it would inside a worker."""
    return deduplication.identify(handle, handle.follow(sm))


def member_key(scan_spec, archive, sm):
    """The key under which the shared document's conversion is claimed and
    stored."""
    identity = identify(member_handle(scan_spec, archive), sm)
    assert identity is not None, "could not identify the shared document"

    return deduplication.content_key(
            str(identity), progress_of(scan_spec).to_json_object())


def member_conversion_message(scan_spec, archive):
    """The message the worker builds for the shared document as it walks one of
    the archives."""
    return messages.ConversionMessage(
            scan_spec=messages.replace(
                    scan_spec,
                    source=ZipSource(
                            conversion_message(scan_spec, archive).handle),
                    progress=None),
            handle=member_handle(scan_spec, archive),
            progress=progress_of(scan_spec))


def run(message, sm):
    """Pushes one message through the worker exactly as a delivery would be,
    returning the (queue, body) pairs it produced."""
    return list(worker.message_received_raw(
            message.to_json_object(), "os2ds_conversions", sm))


def contended(generator):
    """Whether a conversion stood aside instead of converting, consuming
    whatever it produced along the way."""
    return any(
            isinstance(m, deduplication.Contended) for m in generator)


def dispatched(generator):
    """Turns the messages a plan yields into the (queue, body) pairs the worker
    would emit for them."""
    return dispatch(
            generator,
            (messages.ProblemMessage, ["os2ds_problems"]),
            (messages.ContentMissingMessage, ["os2ds_problems"]),
            (messages.MatchesMessage, ["os2ds_matches"]),
            (messages.MetadataMessage, ["os2ds_metadata"]),
            (messages.StatusMessage, ["os2ds_status"]),
            (messages.ObjectProgressMessage, ["os2ds_status"]))


def result_for_the_document(store, scan_spec, archive, sm, sentinel):
    """A real result for the shared document, marked so a replay of it can be
    recognised, and taken back out of the store so that the caller controls when
    it appears."""
    scan_id = deduplication.scan_identity(scan_spec.scan_tag)
    key = member_key(scan_spec, archive, sm)
    list(dispatched(worker.process(
            sm, member_conversion_message(scan_spec, archive), check=False)))

    payload = store.get_result(scan_id, key)
    assert payload is not None, "nothing was published to plant a marker in"
    store._client.delete(f"result:{scan_id}:{key}")

    return plant(payload, sentinel)


def plant(payload, sentinel):
    """Marks every match in a stored result, so that a replay of it can be told
    from a conversion that happened again."""
    planted = False
    for result in payload["results"]:
        for fragment in result["matches"]:
            for match in fragment["matches"] or ():
                match["match"] = sentinel
                planted = True
    assert planted, f"stored result had no matches to mark: {payload}"
    return payload


def matches_in(emitted):
    return [body for queue, body, *_ in emitted if queue == "os2ds_matches"]


def paths_in(emitted):
    return [json.dumps(m["handle"]) for m in matches_in(emitted)]


def conversions_in(emitted):
    """The objects this delivery handed back to the pipeline as scan tasks of
    their own."""
    return [body for queue, body, *_ in emitted if queue == "os2ds_conversions"]


def counted_objects(emitted):
    """How many objects this delivery told the admin module to add to the
    scan's total."""
    return sum(
            body.get("new_objects") or 0
            for queue, body, *_ in emitted if queue == "os2ds_status")


def scanned_objects(emitted):
    """How many objects this delivery reported as scanned.

    object_size and object_type together are what the status collector reads as
    "one more object of this scan has been scanned"."""
    return len([
            body for queue, body, *_ in emitted
            if queue == "os2ds_status"
            and body.get("object_size") is not None
            and body.get("object_type") is not None])


class TestTheGate:
    """The preconditions the rest of the file rests on. Coordination that
    quietly does not happen looks exactly like coordination that happens and
    saves nothing, so these are asserted rather than assumed."""

    def test_the_document_qualifies(self, two_archives):
        assert deduplication.worth_coordinating(
                member_handle(two_archives, "alpha.zip"))

    def test_the_archives_holding_it_do_not(self, two_archives):
        for archive in ("alpha.zip", "beta.zip"):
            assert not deduplication.worth_coordinating(
                    conversion_message(two_archives, archive).handle), archive


class TestClearingTheStore:
    """Results are namespaced per scan, so once a scan is over nothing can read
    them. They hold match contexts, so they go rather than expiring."""

    def test_the_worker_clears_this_scan_s_entries(
            self, store, two_archives):
        with SourceManager() as sm:
            run(conversion_message(two_archives, "alpha.zip"), sm)

        assert list(store._client.scan_iter("result:*")), (
                "nothing was stored to purge")

        worker.clear_dedup_store(two_archives.scan_tag)

        assert list(store._client.scan_iter("result:*")) == []

    def test_being_asked_about_an_unrelated_scan_changes_nothing(
            self, store, two_archives):
        with SourceManager() as sm:
            run(conversion_message(two_archives, "alpha.zip"), sm)

        worker.clear_dedup_store(
                messages.replace(
                        two_archives.scan_tag,
                        scanner=messages.ScannerFragment(
                                pk=999, name="another scanner")))

        assert list(store._client.scan_iter("result:*")), (
                "another scan's results were purged")


class TestCoordinationSwitchedOff:
    def test_an_object_inside_a_container_is_scanned_with_no_store(
            self, two_archives):
        """The feature is off by default, so off has to cost nothing and change
        nothing about what a container's contents produce."""
        deduplication._store = None
        deduplication._store_resolved = True
        try:
            with SourceManager() as sm:
                emitted = run(conversion_message(two_archives, "alpha.zip"), sm)
        finally:
            deduplication.reset_store()

        assert any(MEMBER in p for p in paths_in(emitted)), paths_in(emitted)
        assert not conversions_in(emitted), (
                "nothing should be handed back with nothing to coordinate with")


class TestOneDocumentInTwoArchives:
    def test_the_document_is_what_gets_coordinated(self, store, two_archives):
        """Not the archive holding it, and not the small file beside it."""
        with SourceManager() as sm:
            run(conversion_message(two_archives, "alpha.zip"), sm)

            keys = [k.decode() for k in store._client.scan_iter("result:*")]
            assert len(keys) == 1, f"expected one stored result, got {keys}"
            assert keys[0].endswith(
                    member_key(two_archives, "alpha.zip", sm))

        payload = deduplication._unpack(store._client.get(keys[0]))
        assert not deduplication.is_unshareable(payload), (
                f"the first archive published nothing usable: {payload}")
        assert payload["results"], "stored result contains no rule results"

    def test_the_second_archive_really_reuses_the_result(
            self, store, two_archives):
        """Proves reuse rather than inferring it.

        The second archive would report the document's findings just as happily
        by unpacking and converting it again, so a marker is planted in the
        stored result between the two runs and findings carrying it demonstrably
        came out of the store."""
        sentinel = "SENTINEL-PLANTED-IN-THE-STORE"

        with SourceManager() as sm:
            run(conversion_message(two_archives, "alpha.zip"), sm)

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

            second = run(conversion_message(two_archives, "beta.zip"), sm)

        assert sentinel in json.dumps(matches_in(second)), (
                "the second archive unpacked and converted the document again"
                " instead of reusing the stored result")

    def test_each_archive_reports_the_document_inside_itself(
            self, store, two_archives):
        """The point of the whole feature: a reused conversion changes how a
        representation was obtained, never which object is reported."""
        with SourceManager() as sm:
            first = run(conversion_message(two_archives, "alpha.zip"), sm)
            second = run(conversion_message(two_archives, "beta.zip"), sm)

        assert matches_in(first), "the first archive produced no matches"
        assert matches_in(second), "the second archive produced no matches"

        assert all("alpha.zip" in p for p in paths_in(first)), paths_in(first)
        assert all("beta.zip" in p for p in paths_in(second)), paths_in(second)

    def test_no_claim_is_left_behind(self, store, two_archives):
        """A leftover claim on the document would stall the next archive holding
        it for a whole lease period."""
        with SourceManager() as sm:
            run(conversion_message(two_archives, "alpha.zip"), sm)
            run(conversion_message(two_archives, "beta.zip"), sm)

        claims = list(store._client.scan_iter("claim:*"))
        assert claims == [], f"claim left behind: {claims}"


class TestOneDocumentAttachedToTwoMails:
    """The case this is really aimed at: a document mailed to a whole
    department, arriving as one mail per recipient with nothing but the
    attachment in common.

    The mails clear the cost gate too, a mail being bigger than what is attached
    to it, so the attachment is coordinated under a claim on the mail."""

    def test_the_attachment_is_coordinated(self, store, two_mails):
        with SourceManager() as sm:
            run(conversion_message(two_mails, "one.eml"), sm)

            key = part_key(two_mails, "one.eml", sm, is_the_attachment)

        scan_id = deduplication.scan_identity(two_mails.scan_tag)
        assert store.get_result(scan_id, key) is not None, (
                "the attachment was converted without publishing a result")

    def test_the_second_mail_reuses_the_attachment_conversion(
            self, store, two_mails):
        sentinel = "SENTINEL-PLANTED-IN-THE-STORE"

        with SourceManager() as sm:
            run(conversion_message(two_mails, "one.eml"), sm)

            key = part_key(two_mails, "one.eml", sm, is_the_attachment)
            scan_id = deduplication.scan_identity(two_mails.scan_tag)
            payload = store.get_result(scan_id, key)
            assert payload is not None, "nothing stored to reuse"
            store.store_result(scan_id, key, plant(payload, sentinel))

            second = run(conversion_message(two_mails, "two.eml"), sm)

        assert sentinel in json.dumps(matches_in(second)), (
                "the second mail converted the attachment again instead of"
                " reusing the stored result")
        assert any("two.eml" in p for p in paths_in(second)), paths_in(second)


class TestASignatureImageInTwoMails:
    """The commonest duplication in a municipal mailbox: one signature image at
    the foot of mail after mail.

    It is far too small to clear the size gate and qualifies by being an image,
    which is what always_types is for: a few kB of logo is seconds of OCR."""

    def test_the_signature_qualifies_although_it_is_small(
            self, two_signed_mails, gate):
        with SourceManager() as sm:
            signature = part_handle(
                    two_signed_mails, "one.eml", sm, is_the_signature)

        assert signature.hint("size") < gate["min_size"]
        assert deduplication.worth_coordinating(signature)

    def test_the_signature_is_coordinated(self, store, two_signed_mails):
        with SourceManager() as sm:
            run(conversion_message(two_signed_mails, "one.eml"), sm)

            key = part_key(
                    two_signed_mails, "one.eml", sm, is_the_signature)

        scan_id = deduplication.scan_identity(two_signed_mails.scan_tag)
        assert store.get_result(scan_id, key) is not None, (
                "the signature was converted without publishing a result")

    def test_the_second_mail_reuses_the_signature_conversion(
            self, store, two_signed_mails):
        sentinel = "SENTINEL-PLANTED-IN-THE-STORE"

        with SourceManager() as sm:
            run(conversion_message(two_signed_mails, "one.eml"), sm)

            key = part_key(two_signed_mails, "one.eml", sm, is_the_signature)
            scan_id = deduplication.scan_identity(two_signed_mails.scan_tag)
            payload = store.get_result(scan_id, key)
            assert payload is not None, "nothing stored to reuse"
            store.store_result(scan_id, key, plant(payload, sentinel))

            second = run(conversion_message(two_signed_mails, "two.eml"), sm)

        assert sentinel in json.dumps(matches_in(second)), (
                "the second mail ran OCR on the signature again instead of"
                " reusing the stored result")
        assert any("two.eml" in p for p in paths_in(second)), paths_in(second)


class TestAnIncrementalScan:
    """The shape a production scan has: a LastModifiedRule in front of the rules
    that look at content, concluding with each object's own modification time.

    Two mails sent at different times still hold one attachment, so the
    conversion of that attachment has to be shared between them however far
    apart the mails are."""

    @pytest.fixture
    def incremental(self, two_mails):
        """The same two mails, given different modification times and scanned
        the way an incremental scan scans them."""
        root = two_mails.source.path
        os.utime(os.path.join(root, "one.eml"), (1_700_000_000, 1_700_000_000))
        os.utime(os.path.join(root, "two.eml"), (1_750_000_000, 1_750_000_000))

        return messages.replace(
                two_mails,
                rule=AndRule(
                        LastModifiedRule(
                                parse_datetime("2000-01-01T00:00:00+00:00")),
                        CPRRule()))

    def test_the_mails_really_do_differ(self, incremental):
        """The precondition. Two mails with the same timestamp would share
        whether or not any of this worked."""
        root = incremental.source.path
        assert (os.path.getmtime(os.path.join(root, "one.eml"))
                != os.path.getmtime(os.path.join(root, "two.eml")))

    def test_the_attachment_is_coordinated(self, store, incremental):
        """What the class is about: the attachment's conversion is published for
        the other mail whatever the mails' own timestamps are."""
        with SourceManager() as sm:
            run(conversion_message(incremental, "one.eml"), sm)
            digest = part_digest(incremental, "one.eml", sm, is_the_attachment)

        keys = [k.decode() for k in store._client.scan_iter("result:*")]
        assert any(digest in key for key in keys), (
                f"nothing was published for the attachment: {keys}")

    def test_the_mail_around_it_is_coordinated_too(self, store, incremental):
        """An incremental scan asks a LastModifiedRule of an object before it
        asks anything about content, and that first question cannot be
        coordinated: its answer is the object's own modification time. The
        content question that follows it is the question a full scan asks first,
        so it is coordinated like any other."""
        with SourceManager() as sm:
            run(conversion_message(incremental, "one.eml"), sm)

        types = {key.decode().rsplit(":", 2)[-2]
                 for key in store._client.scan_iter("result:*")}
        assert "message/rfc822" in types, (
                f"the mail's content hop was left uncoordinated: {types}")

    def test_the_second_mail_reuses_the_attachment_conversion(
            self, store, incremental):
        """What the whole thing is for. The attachment is one piece of content
        however different the mails carrying it are."""
        sentinel = "SENTINEL-PLANTED-IN-THE-STORE"

        with SourceManager() as sm:
            run(conversion_message(incremental, "one.eml"), sm)

            # Addressed by its content rather than by being the only thing in
            # the store: the mail carrying it is coordinated too.
            digest = part_digest(incremental, "one.eml", sm, is_the_attachment)
            keys = [k.decode() for k in store._client.scan_iter("result:*")
                    if digest in k.decode()]
            assert len(keys) == 1, f"nothing stored to reuse: {keys}"

            payload = plant(
                    deduplication._unpack(store._client.get(keys[0])), sentinel)
            store._client.set(keys[0], deduplication._pack(payload))

            second = run(conversion_message(incremental, "two.eml"), sm)

        assert sentinel in json.dumps(matches_in(second)), (
                "the second mail converted the attachment again: the two mails"
                " were asked what looked like different questions")


class TestADocumentAnotherWorkerIsConverting:
    """An object inside a container cannot put itself down: its delivery covers
    the container, some of whose other objects have already been reported in
    messages nothing can retract. So it stands aside instead, and the delivery
    comes back to it once the container's other objects have been dealt with.

    Nothing is fetched again to make that happen, the container being open for
    the length of the walk regardless."""

    def contend(self, store, scan_spec, sm, archive="alpha.zip"):
        """Takes the claim on the shared document as another worker would, so
        that the worker under test finds it held."""
        scan_id = deduplication.scan_identity(scan_spec.scan_tag)
        key = member_key(scan_spec, archive, sm)
        holder = deduplication.ClaimStore(
                store._client, lease_ms=60000, result_ttl=60,
                owner="another-worker")

        assert holder.claim(scan_id, key), "could not take the claim"
        return scan_id, key

    def test_the_document_is_set_aside_rather_than_converted_in_place(
            self, store, two_archives):
        with SourceManager() as sm:
            self.contend(store, two_archives, sm)

            message = member_conversion_message(two_archives, "alpha.zip")
            emitted = list(worker.process(sm, message, check=False))

        assert [type(m) for m in emitted] == [deduplication.Contended], (
                "the document was converted rather than set aside")

    def test_it_is_reported_after_the_container_s_other_objects(
            self, store, two_archives):
        """Getting on with them *is* the wait, so the order is the mechanism
        rather than an incidental detail of it."""
        with SourceManager() as sm:
            self.contend(store, two_archives, sm)

            emitted = run(conversion_message(two_archives, "alpha.zip"), sm)

        reported = paths_in(emitted)
        assert len(reported) == 2, reported
        assert "notes.txt" in reported[0], reported
        assert MEMBER in reported[1], reported

    def test_it_is_scanned_even_if_the_claim_is_never_released(
            self, store, two_archives):
        """The floor under the whole mechanism: standing aside must never mean
        going unscanned. Converting a duplicate is what would have happened
        without coordinating at all."""
        with SourceManager() as sm:
            self.contend(store, two_archives, sm)

            emitted = run(conversion_message(two_archives, "alpha.zip"), sm)

        assert any(MEMBER in p for p in paths_in(emitted)), paths_in(emitted)

    def test_the_second_look_reuses_a_result_that_has_since_arrived(
            self, store, two_archives):
        """What the waiting is for. The holder finishes while the container's
        other objects are being dealt with, and the second look finds the result
        instead of converting the content again."""
        sentinel = "SENTINEL-PLANTED-IN-THE-STORE"

        with SourceManager() as sm:
            payload = result_for_the_document(
                    store, two_archives, "beta.zip", sm, sentinel)

            scan_id, key = self.contend(store, two_archives, sm)
            message = member_conversion_message(two_archives, "alpha.zip")

            assert contended(worker.process(sm, message, check=False)), (
                    "nothing was set aside to come back to")

            # The holder finishes while the container's other objects are being
            # dealt with. Its claim is left in place, a result being read before
            # a claim is attempted.
            store.store_result(scan_id, key, payload)

            emitted = list(dispatched(
                    worker.second_look(sm, message)))

        assert sentinel in json.dumps(emitted), (
                "the second look converted the document again instead of"
                " reusing the result that had arrived")

    def test_the_second_look_takes_a_claim_that_has_been_abandoned(
            self, store, two_archives):
        """A worker that died holding a claim leaves it to expire. The second
        look runs the whole protocol again, so it converts for every copy rather
        than converting only for itself."""
        with SourceManager() as sm:
            scan_id, key = self.contend(store, two_archives, sm)
            message = member_conversion_message(two_archives, "alpha.zip")

            assert contended(worker.process(sm, message, check=False))

            store._client.delete(f"claim:{scan_id}:{key}")

            list(dispatched(worker.second_look(sm, message)))

        assert store.get_result(scan_id, key) is not None, (
                "the second look converted without publishing a result")

    def test_nothing_is_handed_back_to_the_pipeline(
            self, store, two_archives):
        """Standing aside happens inside the delivery. Handing the object back
        as a scan task of its own would mean fetching and opening the container
        again to get to it, which for a large archive costs a full download."""
        with SourceManager() as sm:
            self.contend(store, two_archives, sm)

            emitted = run(conversion_message(two_archives, "alpha.zip"), sm)

        assert not conversions_in(emitted), conversions_in(emitted)

    def test_the_scan_s_object_accounting_is_untouched(
            self, store, two_archives):
        """The archive is one object of this scan however many of the objects
        inside it had to wait, so nothing here adds to the scan's totals."""
        with SourceManager() as sm:
            self.contend(store, two_archives, sm)

            emitted = run(conversion_message(two_archives, "alpha.zip"), sm)

        assert counted_objects(emitted) == 0
        assert scanned_objects(emitted) == 1
