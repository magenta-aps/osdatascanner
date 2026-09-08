# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Tests for the decisions a worker makes before it coordinates over an object:
whether the object is expensive enough to be worth coordinating over, whether
its rule's conclusions may be attributed to another object at all, how long to
stand aside when another worker is already converting the content, and how much
it is prepared to spend finding out what the content is."""

import email.message
import os
import shutil
import tempfile
import time
from datetime import timedelta

import pytest

from os2datascanner.engine2 import settings
from os2datascanner.engine2.conversions import conversion_exists
from os2datascanner.engine2.conversions.types import OutputType
from os2datascanner.engine2.model.core import SourceManager
from os2datascanner.engine2.model.core.resource import Resource
from os2datascanner.engine2.model.derived.mail import MailSource
from os2datascanner.engine2.model.ews import EWSAccountSource, EWSMailHandle
from os2datascanner.engine2.model.file import FilesystemHandle, FilesystemSource
from os2datascanner.engine2.model.smbc import SMBCSource, SMBCHandle
from os2datascanner.engine2.pipeline import messages
from os2datascanner.engine2.pipeline.utilities import deduplication
from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules.dimensions import DimensionsRule
from os2datascanner.engine2.rules.last_modified import LastModifiedRule
from os2datascanner.engine2.rules.logical import AndRule, NotRule, OrRule
from os2datascanner.engine2.rules.meta import HasConversionRule, SizeRule
from os2datascanner.engine2.rules.presentation import PresentationRule
from os2datascanner.engine2.rules.regex import RegexRule
from os2datascanner.utils.system_utilities import time_now


SHARE = SMBCSource("//SERVER/Documents", "username")

# One pixel, so that an inline image is unambiguously below any size threshold.
PNG = bytes.fromhex(
        "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753"
        "de0000000c4944415408d763f8cfc00000030101003e3ba7b40000000049454e"
        "44ae426082")


@pytest.fixture
def dedup_config():
    """Pins the coordination thresholds so the tests do not depend on whatever
    the deployment happens to be configured with."""
    conf = deduplication._dedup_settings()
    saved = dict(conf)
    conf.update({
        "min_size": 1048576,
        "always_types": ["application/pdf", "image/*"],
        "backoff_ms": [1000, 2000, 5000],
        "max_deferral_ms": 10000,
    })
    yield conf
    conf.clear()
    conf.update(saved)


class TestWorthCoordinating:
    def test_expensive_formats_qualify_at_any_size(self, dedup_config):
        """A scanned PDF can occupy a worker for hours whatever it weighs, so
        the decision cannot rest on size alone."""
        assert deduplication.worth_coordinating(
                SMBCHandle(SHARE, "small-but-scanned.pdf")) is True

    @pytest.mark.parametrize("size", [None, "", "not a number", "1.5", []])
    def test_a_size_that_is_not_a_number_does_not_qualify(
            self, dedup_config, size):
        """A hint is whatever the Source that found the object put in the
        message, and coordinating is an optimisation: one that raised here would
        turn a scannable object into a problem report."""
        assert not deduplication.worth_coordinating(
                SMBCHandle(SHARE, "sagsmappe/rapport.txt", hints={"size": size}))

    def test_a_size_that_arrives_as_a_string_still_qualifies(
            self, dedup_config):
        """Google Drive reports int64 as a JSON string."""
        assert deduplication.worth_coordinating(
                SMBCHandle(SHARE, "sagsmappe/rapport.pdf",
                           hints={"size": "2097152"}))

    def test_cheap_object_of_unknown_size_does_not_qualify(self, dedup_config):
        """Without a size there is nothing to justify the read that identifying
        the content would cost."""
        assert deduplication.worth_coordinating(
                SMBCHandle(SHARE, "records.csv")) is False

    def test_small_object_does_not_qualify(self, dedup_config):
        """The 2-second CSV that turns up twenty times is cheaper to convert
        twenty times than to coordinate over."""
        assert deduplication.worth_coordinating(
                SMBCHandle(SHARE, "records.csv", hints={"size": 4096})) is False

    def test_large_object_qualifies(self, dedup_config):
        assert deduplication.worth_coordinating(
                SMBCHandle(
                    SHARE, "records.csv",
                    hints={"size": 50 * 1048576})) is True

    def test_size_exactly_at_the_threshold_qualifies(self, dedup_config):
        assert deduplication.worth_coordinating(
                SMBCHandle(
                    SHARE, "records.csv", hints={"size": 1048576})) is True


class TestExpensiveTypes:
    """Coordination is aimed at what a conversion costs, which is not what an
    object weighs: a 20 kB signature image is seconds of OCR, and the same few
    of them turn up in every mail in a department."""

    def small(self, name, mime_type=None):
        """A small object, well under any size threshold."""
        class _Handle(SMBCHandle):
            def guess_type(self):
                return mime_type or super().guess_type()

        return _Handle(SHARE, name, hints={"size": 20 * 1024})

    @pytest.mark.parametrize("mime_type", [
        "image/png", "image/jpeg", "image/gif", "image/tiff"])
    def test_a_small_image_qualifies(self, dedup_config, mime_type):
        assert deduplication.worth_coordinating(
                self.small("signature", mime_type))

    def test_a_wildcard_does_not_match_a_neighbouring_family(
            self, dedup_config):
        """"image/*" must not reach text/* or anything else that merely starts
        the same way."""
        assert not deduplication.worth_coordinating(
                self.small("notes", "text/plain"))
        assert not deduplication.worth_coordinating(
                self.small("archive", "application/zip"))

    def test_a_small_pdf_still_qualifies(self, dedup_config):
        assert deduplication.worth_coordinating(
                self.small("report.pdf", "application/pdf"))


class TestTheGateDividesAMailFromItsParts:
    """The mail object is the envelope, and never clears the gate: it carries
    email headers and no size, and message/rfc822 is not an expensive type. What
    it holds is met one part at a time, which is where mail duplication is
    actually caught."""

    @pytest.fixture
    def parts(self, dedup_config):
        """One mail holding a body, an inline image and an attachment, walked as
        the worker walks it.

        Built as a real mail and taken apart by MailSource rather than described
        with stand-in Handles, since what is under test is the type and size
        those Handles come out carrying."""
        dedup_config["min_size"] = 16384

        root = tempfile.mkdtemp()
        mail = email.message.EmailMessage()
        mail["Subject"] = "Fordelt"
        mail["Message-ID"] = "<one@example.invalid>"
        mail.set_content("Se venligst vedhaeftede.\n")
        mail.add_attachment(PNG, maintype="image", subtype="png", cid="<logo>")
        mail.add_attachment(
                ("Sagsbehandler noter. CPR 1111111118.\n" * 2000).encode(),
                maintype="text", subtype="plain", filename="report.txt")
        with open(os.path.join(root, "one.eml"), "wb") as fp:
            fp.write(mail.as_bytes())

        source = FilesystemSource(root)
        handle = FilesystemHandle(source, "one.eml")
        with SourceManager() as sm:
            # By path rather than by type: a body and a text attachment are both
            # text/plain, which is the point of keeping them apart here.
            yield {
                h.relative_path: h
                for h in MailSource(handle).handles(sm)}

        shutil.rmtree(root, ignore_errors=True)

    def test_the_mail_itself_does_not_qualify(self, dedup_config):
        assert not deduplication.worth_coordinating(
                EWSMailHandle(
                    EWSAccountSource(
                            "example.invalid", "https://example.invalid/ews",
                            "admin", "secret", "someone"),
                    "SU5CT1gK", "Fordelt", "INBOX", 1, None,
                    hints={"email-headers": {"subject": "Fordelt"}}))

    def test_an_attachment_qualifies_on_its_size(self, parts):
        attachment = parts["2/report.txt"]
        assert attachment.guess_type() == "text/plain"
        assert attachment.hint("size") > 16384
        assert deduplication.worth_coordinating(attachment)

    def test_an_inline_image_qualifies_however_small(self, parts):
        image = parts["1/file"]
        assert image.guess_type() == "image/png"
        assert image.hint("size") < 16384
        assert deduplication.worth_coordinating(image)

    def test_a_small_body_does_not_qualify(self, parts):
        """Converting a couple of kB of text costs less than coordinating over
        it."""
        body = parts["0/"]
        assert body.guess_type() == "text/plain"
        assert not deduplication.worth_coordinating(body)


class TestSkippedTypesAreNotCoordinated:
    """A scan with OCR switched off configures the processor to skip image/*.
    Identifying every image in it would be paying the cost of coordination for
    a conversion that is never going to happen."""

    def conversion(self, mime_type, **configuration):
        class _Handle(SMBCHandle):
            def guess_type(self):
                return mime_type

        return messages.ConversionMessage(
                scan_spec=messages.ScanSpecMessage(
                        scan_tag=messages.ScanTagFragment.make_dummy(),
                        source=SHARE, rule=CPRRule(),
                        configuration=configuration, filter_rule=None,
                        progress=None),
                handle=_Handle(SHARE, "signature", hints={"size": 20 * 1024}),
                progress=messages.ProgressFragment(rule=CPRRule(), matches=[]))

    def test_a_skipped_type_is_not_coordinated(self):
        assert deduplication.will_be_skipped(
                self.conversion("image/png", skip_mime_types=["image/*"]))

    def test_a_type_that_will_be_converted_is_coordinated(self):
        assert not deduplication.will_be_skipped(
                self.conversion("image/png", skip_mime_types=["video/*"]))

    def test_a_scan_with_nothing_skipped_coordinates(self):
        assert not deduplication.will_be_skipped(
                self.conversion("image/png"))


class TestNothingToSkip:
    """Coordinating an object is only worth a read of it if there is a
    conversion for the other copies to skip, or something inside it for them to
    skip walking."""

    @pytest.mark.parametrize("mime_type", [
        "video/mp4", "video/x-matroska", "audio/mpeg",
        "application/x-iso9660-image", "application/x-msdownload",
        "application/octet-stream",
        # No OCR is registered for either of these, so there is no text to
        # extract from them however much of them there is to read.
        "image/tiff", "image/webp"])
    def test_a_type_that_converts_to_nothing_is_not_worth_it(self, mime_type):
        assert not deduplication.can_convert(
                None, OutputType.Text, mime_type)

    @pytest.mark.parametrize("mime_type", [
        "text/plain", "text/html", "image/png", "image/jpeg"])
    def test_a_type_with_a_converter_is_worth_it(self, mime_type):
        assert deduplication.can_convert(
                None, OutputType.Text, mime_type)

    @pytest.mark.parametrize("mime_type", [
        "application/zip", "message/rfc822", "application/pdf"])
    def test_a_container_is_worth_it(self, mime_type):
        """These convert to nothing themselves, and a copy replaying one of
        them skips walking and converting everything inside it, which is the
        largest saving there is."""
        assert not conversion_exists(
                None, OutputType.Text, mime_override=mime_type), (
                f"{mime_type} has a text converter after all")
        assert deduplication.can_convert(
                None, OutputType.Text, mime_type)


class TestTheDigestIsTakenLast:
    """Reading an object to hash it is the one expensive part of coordinating
    over it, so nothing may read one before it is settled that coordinating
    could save anything."""

    class _AlwaysAvailable:
        """A store with nothing in it that nobody has claimed."""
        available = True

        def get_result(self, scan_id, cid):
            return None

        def claim(self, scan_id, cid):
            return False

    @pytest.fixture
    def store(self):
        deduplication._store = self._AlwaysAvailable()
        deduplication._store_resolved = True
        deduplication.forget_delivery()
        yield
        deduplication.reset_store()
        deduplication.forget_delivery()

    def conversion(self, handle, rule=None):
        rule = rule or CPRRule()
        return messages.ConversionMessage(
                scan_spec=messages.ScanSpecMessage(
                        scan_tag=messages.ScanTagFragment.make_dummy(),
                        source=SHARE, rule=rule, configuration={},
                        filter_rule=None, progress=None),
                handle=handle,
                progress=messages.ProgressFragment(rule=rule, matches=[]))

    def test_a_video_is_never_hashed(self, store, dedup_config):
        """The case this ordering is for: a video clears every size threshold
        there is and has nothing to convert, so hashing one would read hundreds
        of megabytes to learn nothing."""
        resource = _CountingResource(delay=0, mime_type="video/mp4")
        handle = _StandInHandle(resource, "clip.mp4", size=200 * 1024 * 1024)

        plan = deduplication.plan_conversion(
                self.conversion(handle), resource, OutputType.Text)

        assert plan is None
        assert resource.digest_attempts == 0, (
                "the object was read to hash it before anything had established"
                " that coordinating it could save something")

    def test_something_convertible_is_hashed(self, store, dedup_config):
        """The other half: the check must not stop everything."""
        resource = _CountingResource(delay=0, mime_type="text/plain")
        handle = _StandInHandle(resource, "notes.txt", size=200 * 1024 * 1024)

        plan = deduplication.plan_conversion(
                self.conversion(handle), resource, OutputType.Text)

        assert resource.digest_attempts == 1
        assert isinstance(plan, deduplication.Contended), (
                "the protocol did not run to the end")

    def test_an_incremental_scan_is_never_hashed(self, store, dedup_config):
        """An incremental scan asks a LastModifiedRule before it asks anything
        about content, and no conclusion of that rule may be attributed to
        another object. Reading one to find that out would have a delta scan
        read every object it exists to avoid reading."""
        resource = _CountingResource(delay=0, mime_type="text/plain")
        handle = _StandInHandle(resource, "notes.txt", size=200 * 1024 * 1024)
        conversion = self.conversion(
                handle, AndRule(LastModifiedRule(time_now()), CPRRule()))

        plan = deduplication.plan_conversion(
                conversion, resource, OutputType.LastModified)

        assert plan is None
        assert resource.digest_attempts == 0, (
                "the object was read to hash it before the rule that makes it"
                " uncoordinated had been looked at")


class TestIsShareable:
    @pytest.mark.parametrize("rule", [
        CPRRule(),
        RegexRule("[0-9]+"),
        OrRule(CPRRule(), RegexRule("[0-9]+")),
        AndRule(CPRRule(), RegexRule("[0-9]+")),
        # A rule tree that has already been resolved constrains nothing.
        True,
        False,
        # The dynamic case: this rule's input type is whatever it was built with.
        HasConversionRule(OutputType.Text),
    ])
    def test_content_only_rules_are_shareable(self, rule):
        assert deduplication.is_shareable(rule) is True

    @pytest.mark.parametrize("rule", [
        # An object's modification date is a property of where it lives, not of
        # what it contains.
        LastModifiedRule(time_now()),
        # As is its path.
        PresentationRule("secret"),
        # Size is reported by the Resource rather than measured from the bytes,
        # so it is excluded deliberately.
        SizeRule(1024),
        HasConversionRule(OutputType.LastModified),
    ])
    def test_location_dependent_rules_are_not_shareable(self, rule):
        assert deduplication.is_shareable(rule) is False

    def test_one_bad_leaf_spoils_the_tree(self):
        """The gate has to look at every leaf, not just the outermost rule: a
        single date comparison anywhere makes the whole conclusion specific to
        this object."""
        assert deduplication.is_shareable(
                AndRule(CPRRule(), LastModifiedRule(time_now()))) is False

    def test_negation_does_not_launder_a_bad_leaf(self):
        assert deduplication.is_shareable(
                NotRule(LastModifiedRule(time_now()))) is False

    def test_nested_trees_are_walked_to_the_bottom(self):
        assert deduplication.is_shareable(
                AndRule(
                    OrRule(CPRRule(), RegexRule("[0-9]+")),
                    NotRule(AndRule(
                        RegexRule("x"),
                        LastModifiedRule(time_now()))))) is False

    def test_unrecognised_rule_is_not_shareable(self):
        """A rule type that knows nothing about deduplication must lose the
        optimisation rather than risk being replayed somewhere it does not
        apply."""
        class Unknown:
            pass

        assert deduplication.is_shareable(Unknown()) is False


class TestShippedDefaults:
    """Three settings that look like values worth trimming, and that quietly
    cost the whole saving when they are trimmed.

    These read the shipped defaults rather than the effective configuration,
    because a deployment (including the dev stack) may legitimately choose
    shorter values for a corpus with shorter conversions. What is guarded here
    is what new deployments inherit."""

    def shipped(self) -> dict:
        import tomllib
        from pathlib import Path

        import os2datascanner.engine2 as engine2

        defaults = Path(engine2.__file__).parent / "default-settings.toml"
        with defaults.open("rb") as fp:
            return tomllib.load(fp)["pipeline"]["worker"]["dedup"]

    def test_the_shipped_default_budget_outlasts_a_long_conversion(self):
        """A duplicate that gives up before the worker converting its content has
        finished converts it again, and the only thing achieved was the
        waiting."""
        two_hours_ms = 2 * 60 * 60 * 1000

        assert self.shipped()["max_deferral_ms"] > two_hours_ms

    def test_the_shipped_floor_admits_an_object_worth_coordinating(self):
        """Measured on plain text with no match in it, which is the least a
        replay can save, coordinating pays from about 8 kB and is a 2x win by
        32 kB. A floor above that trades the saving away."""
        assert self.shipped()["min_size"] <= 32 * 1024

    def test_the_shipped_result_expiry_outlasts_a_long_scan(self):
        """Results are renewed when they are used, so this is an idle timeout --
        but two copies of one document can be discovered a long way apart, and an
        expiry measured in hours would drop a result in between."""
        one_day_s = 24 * 60 * 60

        assert self.shipped()["result_ttl"] > one_day_s


class TestScanIdentity:
    """The namespace every claim and every result is filed under.

    Nothing may ever be reused across scans, and this string is the only thing
    keeping one scan's results away from another's."""

    def test_a_scan_is_identified_by_its_scanner_and_its_start(self):
        tag = messages.ScanTagFragment.make_dummy()

        assert (deduplication.scan_identity(tag)
                == f"{tag.scanner.pk}:{tag.time.isoformat()}")

    def test_one_scan_keys_the_same_way_every_time(self):
        """Two workers handling two copies from one scan have to agree, or they
        never find each other's work."""
        tag = messages.ScanTagFragment.make_dummy()

        assert (deduplication.scan_identity(tag)
                == deduplication.scan_identity(
                        messages.ScanTagFragment.from_json_object(
                                tag.to_json_object())))

    def test_two_runs_of_one_scanner_are_different_scans(self):
        """The same scanner run twice must not share results between the runs:
        the second run exists to look at the data again."""
        first = messages.ScanTagFragment.make_dummy()
        second = messages.deep_replace(
                first, time=first.time + timedelta(hours=1))

        assert (deduplication.scan_identity(first)
                != deduplication.scan_identity(second))

    @pytest.mark.parametrize("missing", ["scanner", "time"])
    def test_an_unidentifiable_scan_gets_no_identity(self, missing):
        """A ScanTagFragment holds both of these optionally, and the fallback for
        an unrecognised tag in ScanTagFragment.from_json_object can leave both
        unset. Substituting a placeholder would file every such scan under one
        identity, so that two scans of one document with one rule would share a
        result -- which is the one thing this module must never do."""
        tag = messages.deep_replace(
                messages.ScanTagFragment.make_dummy(), **{missing: None})

        assert deduplication.scan_identity(tag) is None

    def test_the_legacy_timestamp_scan_tag_gets_no_identity(self):
        """Scan tags from versions 3.0.0 to 3.3.2 inclusive were bare
        timestamps, which name no scanner."""
        tag = messages.ScanTagFragment.from_json_object(
                time_now().isoformat())

        assert deduplication.scan_identity(tag) is None


class TestContentIdentity:
    """What counts as "the same content" for the purposes of sharing a
    conversion."""

    def test_the_same_bytes_read_as_the_same_type_are_the_same_content(self):
        assert (str(deduplication.ContentIdentity(
                        digest="a" * 64, mime_type="application/pdf"))
                == str(deduplication.ContentIdentity(
                        digest="a" * 64, mime_type="application/pdf")))

    def test_the_same_bytes_read_as_different_types_are_not(self):
        """A conversion is a function of the converter as well as the bytes, and
        Resource.compute_type() takes the type from the object's *name* whenever
        the bytes look generic. The same bytes stored as "report.doc" are
        converted as a Word document, and stored without an extension as an OLE
        container, for which there is no text converter at all."""
        assert (str(deduplication.ContentIdentity(
                        digest="a" * 64, mime_type="application/msword"))
                != str(deduplication.ContentIdentity(
                        digest="a" * 64, mime_type="application/x-ole-storage")))

    def test_different_bytes_are_not_the_same_content(self):
        assert (str(deduplication.ContentIdentity(
                        digest="a" * 64, mime_type="application/pdf"))
                != str(deduplication.ContentIdentity(
                        digest="b" * 64, mime_type="application/pdf")))


class TestContentKey:
    """The key is built from the progress fragment, which a top-level object has
    in the form it arrived on the wire in and an object inside a container can
    only serialise for itself (see TestProgressRoundTrip)."""

    CID = "a" * 64

    def test_progress_with_different_matches_gives_a_different_key(self):
        """The remaining rule is only half of the question being asked: what an
        already-evaluated rule concluded travels beside it in the accumulated
        matches, so two copies whose remainders agree but whose findings so far
        differ are not asking the same question."""
        rule_json = CPRRule().to_json_object()
        found = RegexRule("cat").to_json_object()

        assert (deduplication.content_key(
                    self.CID, {"rule": rule_json, "matches": []})
                != deduplication.content_key(
                    self.CID,
                    {"rule": rule_json,
                     "matches": [{"rule": found, "matches": [{"match": "cat"}]}]}))

    def test_the_same_content_and_rule_give_the_same_key(self):
        rule_json = CPRRule().to_json_object()

        assert (deduplication.content_key(self.CID, rule_json)
                == deduplication.content_key(self.CID, rule_json))

    def test_different_content_gives_a_different_key(self):
        rule_json = CPRRule().to_json_object()

        assert (deduplication.content_key(self.CID, rule_json)
                != deduplication.content_key("b" * 64, rule_json))

    def test_a_different_rule_gives_a_different_key(self):
        """Two copies of one document do not necessarily arrive with the same
        rule left to evaluate, because the pipeline resolves what it can up
        front and a last-modified cutoff resolves differently per copy. Keying on
        content alone would report one copy's conclusions for a copy that was
        asked a different question."""
        assert (deduplication.content_key(self.CID, CPRRule().to_json_object())
                != deduplication.content_key(
                        self.CID,
                        AndRule(CPRRule(), RegexRule("x")).to_json_object()))

    def test_rule_argument_changes_the_key(self):
        assert (deduplication.content_key(
                    self.CID, RegexRule("cat").to_json_object())
                != deduplication.content_key(
                    self.CID, RegexRule("dog").to_json_object()))

    def test_resolved_rules_are_keyed_without_raising(self):
        """progress.rule is JSON true or false once a rule has been fully
        resolved."""
        assert (deduplication.content_key(self.CID, True)
                != deduplication.content_key(self.CID, False))

    def test_dict_key_order_does_not_matter(self):
        """Two JSON objects that differ only in key order describe the same rule
        and must key the same, because nothing guarantees which order a
        publisher emitted them in.

        This one is held up by the sort_keys in content_key rather than by
        canonicalisation; the list ordering below is what canonicalisation is
        for."""
        assert (deduplication.content_key(self.CID, {"a": 1, "b": 2})
                == deduplication.content_key(self.CID, {"b": 2, "a": 1}))

    def test_unfingerprintable_rule_gets_a_unique_key(self):
        """A rule that cannot be serialised must not collide with anything, so
        that the object ends up effectively uncoordinated rather than sharing a
        key with an unrelated rule."""
        class Unserialisable:
            pass

        first = deduplication.content_key(self.CID, Unserialisable())
        second = deduplication.content_key(self.CID, Unserialisable())

        assert first != second

    def test_set_derived_list_order_cannot_affect_the_key(self):
        """Regression test: a permuted list must not change the key.

        Several rules keep parts of themselves in sets and emit them as lists --
        CPRRule's whitelist and blacklist among them -- and Python randomises
        string hashing per process, so two workers can serialise one rule to two
        different texts."""
        rule = CPRRule()
        emitted = rule.to_json_object()

        # The precondition that made the bug possible, asserted so that this test
        # starts failing if the rule stops holding this in a set. (The whitelist
        # is a set too, but holds a single word, so it could never have varied.)
        assert isinstance(rule._blacklist, (set, frozenset))
        assert isinstance(emitted["blacklist"], list)
        assert len(emitted["blacklist"]) > 1, "need >1 entry to permute"

        shuffled = dict(
                emitted, blacklist=list(reversed(emitted["blacklist"])))

        assert (deduplication.content_key(self.CID, emitted)
                == deduplication.content_key(self.CID, shuffled))

    def test_a_set_serialised_as_a_string_cannot_affect_the_key(self):
        """Canonicalisation sorts lists, and cannot see into a scalar, so a set
        that serialises to a comma-joined string has to be sorted by the rule
        itself. CPRRule's exception lists are the ones that do."""
        words = ["sagsnr", "journalnr", "cvr", "p-nummer"]
        emitted = CPRRule(
                exceptions=words, surrounding_exceptions=words).to_json_object()

        assert emitted["exceptions"] == ",".join(sorted(words)), emitted
        assert emitted["surrounding_exceptions"] == ",".join(sorted(words))

        assert (deduplication.content_key(
                    self.CID, emitted)
                == deduplication.content_key(
                    self.CID,
                    CPRRule(
                            exceptions=list(reversed(words)),
                            surrounding_exceptions=list(reversed(words))
                            ).to_json_object()))

    def test_nested_list_order_cannot_affect_the_key(self):
        """Canonicalisation has to reach all the way down, because the lists that
        matter are the component lists of a rule tree."""
        first = AndRule(CPRRule(), RegexRule("x")).to_json_object()
        second = AndRule(RegexRule("x"), CPRRule()).to_json_object()

        assert (deduplication.content_key(self.CID, first)
                == deduplication.content_key(self.CID, second))

    def test_genuinely_different_rules_still_differ(self):
        """Canonicalisation must not flatten away real differences: it only
        removes ordering, and a key collision here would mean one rule's findings
        reported for another rule."""
        assert (deduplication.content_key(
                    self.CID, AndRule(CPRRule(), RegexRule("x")).to_json_object())
                != deduplication.content_key(
                    self.CID, AndRule(CPRRule(), RegexRule("y")).to_json_object()))


class TestSyntheticFragmentsDoNotSplitTheKey:
    """Synthetic rules are the pipeline's internal tests, and what one of them
    concluded is not stored in a result. Keying on it would split the key
    between objects being asked the same question."""

    CID = "a" * 64

    def key(self, *fragments):
        return deduplication.content_key(
                self.CID,
                messages.ProgressFragment(
                        rule=CPRRule(), matches=list(fragments)).to_json_object())

    def test_a_last_modified_conclusion_does_not_split_the_key(self):
        """The case that matters. Every incremental scan puts a
        LastModifiedRule in front of the rules that look at content, and it
        concludes with the object's own modification time, so keying on it would
        stop two copies of one document from ever sharing anything."""
        assert self.key(
                messages.MatchFragment(
                        rule=LastModifiedRule(time_now()),
                        matches=[{"match": "2026-09-01T10:00:00+02:00"}])
                ) == self.key(
                messages.MatchFragment(
                        rule=LastModifiedRule(time_now()),
                        matches=[{"match": "2026-03-14T08:30:00+01:00"}]))

    def test_an_image_dimension_conclusion_does_not_split_the_key(self):
        """The other synthetic rule a scan with OCR switched on carries."""
        assert self.key(
                messages.MatchFragment(
                        rule=DimensionsRule(), matches=[{"match": [640, 480]}])
                ) == self.key(
                messages.MatchFragment(
                        rule=DimensionsRule(), matches=[{"match": [200, 100]}]))

    def test_a_synthetic_fragment_is_the_same_as_no_fragment(self):
        assert self.key(
                messages.MatchFragment(
                        rule=LastModifiedRule(time_now()),
                        matches=[{"match": "2026-09-01T10:00:00+02:00"}])
                ) == self.key()

    def test_a_real_fragment_still_splits_the_key(self):
        """Dropping the synthetic ones must not drop the rest: what a rule the
        user asked about concluded is part of what gets reported."""
        assert self.key(
                messages.MatchFragment(
                        rule=RegexRule("cat"), matches=[{"match": "cat"}])
                ) != self.key()


class TestProgressRoundTrip:
    """A progress fragment parsed from the wire and serialised again has to
    fingerprint exactly as the text it was parsed from.

    Objects inside a container never arrive on the wire: the worker walks them
    within the delivery of the container, building their messages itself, so it
    can only fingerprint what it serialises locally. If the round trip were to
    lose or add anything, the workers reaching one piece of content by that route
    would key it differently from the workers reaching it directly, and neither
    group would ever see the other's result. The characteristic symptom is
    silence, so it is asserted here rather than assumed."""

    def fingerprints_agree(self, fragment) -> bool:
        wire = fragment.to_json_object()
        parsed_again = messages.ProgressFragment.from_json_object(
                wire).to_json_object()

        return (deduplication.progress_fingerprint(wire)
                == deduplication.progress_fingerprint(parsed_again))

    def test_a_plain_rule_survives_the_round_trip(self):
        assert self.fingerprints_agree(
                messages.ProgressFragment(rule=CPRRule(), matches=[]))

    def test_a_rule_holding_sets_survives_the_round_trip(self):
        """CPRRule's blacklist is the one that made this worth checking: it is a
        set, and it reaches JSON as a list whose order is not the same twice."""
        assert self.fingerprints_agree(
                messages.ProgressFragment(
                        rule=CPRRule(
                                blacklist={"kontonummer", "p-nummer"},
                                whitelist={"cpr"}),
                        matches=[]))

    def test_a_rule_tree_survives_the_round_trip(self):
        assert self.fingerprints_agree(
                messages.ProgressFragment(
                        rule=AndRule(
                                OrRule(CPRRule(), RegexRule("cat")),
                                NotRule(RegexRule("dog"))),
                        matches=[]))

    def test_accumulated_matches_survive_the_round_trip(self):
        """The other half of the question: what the rules resolved before
        dispatch concluded travels beside the remainder."""
        assert self.fingerprints_agree(
                messages.ProgressFragment(
                        rule=CPRRule(),
                        matches=[
                            messages.MatchFragment(
                                    rule=LastModifiedRule(time_now()),
                                    matches=[]),
                            messages.MatchFragment(
                                    rule=RegexRule("cat"), matches=None),
                        ]))


class TestUnshareableMarker:
    def test_the_marker_is_recognised(self):
        assert deduplication.is_unshareable(
                deduplication.UNSHAREABLE_RESULT) is True

    def test_a_real_result_is_not_the_marker(self):
        assert deduplication.is_unshareable(
                {"root": {}, "results": []}) is False

    def test_the_marker_survives_json(self):
        """It goes through the store as JSON like any other result."""
        import json

        assert deduplication.is_unshareable(
                json.loads(json.dumps(
                        deduplication.UNSHAREABLE_RESULT))) is True


class TestLeaseSizing:
    """The lease bounds the damage from a worker that dies holding a claim, so
    the instinct is to make it short. These pin the opposite constraint: a lease
    shorter than the conversion stretch that cannot renew it expires under its
    holder, and a second worker then converts the same content."""

    def test_the_configured_lease_outlasts_the_longest_unrenewed_stretch(self):
        """Fails if the lease is lowered, and equally if the conversion timeouts
        the floor is derived from are raised, because either change reopens the
        gap."""
        lease_ms = int(deduplication._dedup_settings()["lease_ms"])

        assert lease_ms >= deduplication._longest_unrenewed_stretch_ms(), (
                "the configured lease expires before a large PDF reaches its"
                " first renewal, so its content will be converted twice")

    def test_the_floor_tracks_the_preprocessing_bound(self):
        """The floor is derived rather than written down, so that raising the
        PDF pre-processing budget raises it too. A constant would silently stop
        protecting anything the first time that budget changed."""
        saved = settings.subprocess["pdf_clean_timeout"]
        try:
            before = deduplication._longest_unrenewed_stretch_ms()

            settings.subprocess["pdf_clean_timeout"] = int(saved) + 60
            after = deduplication._longest_unrenewed_stretch_ms()
        finally:
            settings.subprocess["pdf_clean_timeout"] = saved

        assert after == before + 60_000

    def test_a_lease_below_the_floor_is_reported(self):
        """The old default, which is well below the floor."""
        assert deduplication._check_lease_ms(60_000) is True

    def test_a_lease_above_the_floor_is_not_reported(self):
        assert deduplication._check_lease_ms(
                deduplication._longest_unrenewed_stretch_ms() + 1) is False


class _CountingResource:
    """Stands in for a resource whose content takes longer to read than the
    identification budget allows, and counts the attempts made on it."""

    def __init__(self, *, delay: float, mime_type="application/pdf"):
        self.delay = delay
        self.mime_type = mime_type
        self.digest_attempts = 0

    def compute_type(self):
        return self.mime_type

    def compute_content_identifier(self):
        self.digest_attempts += 1
        time.sleep(self.delay)
        return "0" * 64


class _StandInHandle:
    """The least a Handle has to be for deduplication.identify: something that
    names itself, so that what was identified can be remembered."""

    def __init__(self, resource, name="stand-in-handle", size=None):
        self.resource = resource
        self.name = name
        self.size = size

    def crunch(self, *, hash=None):
        return self.name

    def guess_type(self):
        return "application/octet-stream"

    def hint(self, name):
        return self.size if name == "size" else None

    def follow(self, sm):
        return self.resource

    def __str__(self):
        return self.name


class TestTheIdentifierMeasuresContent:
    """compute_content_identifier() identifies content, so that two Resources
    returning one identifier can be deduplicated against each other."""

    def test_a_resource_that_cannot_identify_itself_returns_nothing(self):
        """The base implementation, so that deduplication has something to test
        rather than an identifier it cannot trust."""
        assert Resource.compute_content_identifier(object()) is None


class TestIdentificationBudget:
    """Identifying content reads and hashes every byte of an object, once per
    copy, and is the price of admission to coordinating at all. What it must not
    do is pay that price more than once to reach the same answer."""

    @pytest.fixture
    def short_budget(self):
        conf = deduplication._dedup_settings()
        saved = conf.get("identify_timeout")
        conf["identify_timeout"] = 0.5
        deduplication.forget_delivery()
        yield
        conf["identify_timeout"] = saved
        deduplication.forget_delivery()

    def test_an_overrunning_digest_is_attempted_once(self, short_budget):
        """A TimeoutRetrier retries nothing but its own timeout, and the
        operation here is a deterministic read of the whole object: a second
        identical attempt re-reads all of it to time out again. Retrying is the
        cost this feature exists to remove."""
        resource = _CountingResource(delay=2.0)

        handle = _StandInHandle(resource)
        identity = deduplication.identify(handle, resource)

        assert identity is None
        assert resource.digest_attempts == 1, (
                "the whole object was read more than once to reach the same"
                " conclusion")

    def test_content_identified_within_the_budget_is_returned(
            self, short_budget):
        """The other half of the same behaviour: giving up early must not mean
        giving up on objects that can be identified."""
        resource = _CountingResource(delay=0)

        handle = _StandInHandle(resource)
        identity = deduplication.identify(handle, resource)

        assert identity is not None
        assert identity.digest == "0" * 64
        assert identity.mime_type == "application/pdf"
        assert resource.digest_attempts == 1

    def test_one_object_is_only_ever_read_once(self, short_budget):
        """A rule tree that needs two representations of an object has it
        converted twice, and each conversion is coordinated over separately,
        being a different question about the same content. Reading and hashing
        the object again to answer the second one would be pure waste: its
        content is the one thing that cannot have changed in between."""
        resource = _CountingResource(delay=0)
        handle = _StandInHandle(resource)

        first = deduplication.identify(handle, resource)
        second = deduplication.identify(handle, resource)

        assert first == second
        assert resource.digest_attempts == 1, (
                "the object was read again to reach the same conclusion")

    def test_what_was_identified_is_forgotten_between_deliveries(
            self, short_budget):
        """The cache is only ever useful within one delivery, and an object can
        have been changed by the time a later one reaches it."""
        resource = _CountingResource(delay=0)
        handle = _StandInHandle(resource)

        deduplication.identify(handle, resource)
        deduplication.forget_delivery()
        deduplication.identify(handle, resource)

        assert resource.digest_attempts == 2

    def test_two_objects_are_told_apart(self, short_budget):
        """Two objects that happen to be handled by one delivery are two
        objects, however alike their Resources look."""
        first, second = (
                _CountingResource(delay=0), _CountingResource(delay=0))

        deduplication.identify(_StandInHandle(first, "one"), first)
        deduplication.identify(_StandInHandle(second, "two"), second)

        assert first.digest_attempts == 1
        assert second.digest_attempts == 1


class TestTheMasterSwitch:
    """Every value in this section can arrive as a string, settings being
    overridable through the environment, and every non-empty string is true."""

    @pytest.mark.parametrize("value", [False, "false", "False", "0", "no", ""])
    def test_these_leave_coordination_off(self, value):
        assert deduplication._flag(value) is False

    @pytest.mark.parametrize("value", [True, "true", "True", "1", "yes", "on"])
    def test_these_turn_coordination_on(self, value):
        assert deduplication._flag(value) is True
