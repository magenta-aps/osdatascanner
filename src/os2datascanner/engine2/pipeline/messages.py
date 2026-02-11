# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import annotations

import uuid
from uuid import UUID
import random
from typing import Any, ClassVar, Optional, Self, Sequence, Protocol, TypeVar
from datetime import datetime
from dateutil import tz
import warnings
import structlog
from dataclasses import Field, replace, dataclass

from ..utilities.datetime import parse_datetime
from ..model.core import Handle, Source
from ..model.core.errors import DeserialisationError
from ..rules.rule import Rule, SimpleRule, Sensitivity


logger = structlog.get_logger("engine2")


class ProbablyDataclass(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


class SerialisableMessage(ProbablyDataclass, Protocol):
    def to_json_object(self) -> dict:
        ...

    @classmethod
    def from_json_object(cls, obj: dict) -> Self:
        ...


def require_fields(
        cls: type, d: dict[str, Any], *fields: str) -> None:
    for f in fields:
        if f not in d:
            raise DeserialisationError(cls.__name__, f)


N = TypeVar("N", bound=ProbablyDataclass)


def deep_replace(p: N, **kwargs) -> N:
    """As dataclasses.replace, but supports deeply nested field replacement
    using Django-like syntax ("tuple1__subtuple__field")."""
    for name, value in kwargs.items():
        name = name.split("__")
        if len(name) > 1:
            head, tail = name[0], name[1:]
            fragment = getattr(p, head)
            p = replace(p, **{
                head: deep_replace(fragment, **{
                    "__".join(tail): value
                })
            })
        else:
            p = replace(p, **{name[0]: value})
    return p


@dataclass(frozen=True, slots=True, kw_only=True)
class MatchFragment:
    """A MatchFragment represents the result of executing a single SimpleRule;
    it is a pair of the rule and the matches that it produced."""
    rule: SimpleRule
    matches: Optional[Sequence[dict]]

    def to_json_object(self):
        return {
            "rule": self.rule.to_json_object(),
            "matches": list(self.matches) if self.matches else None
        }

    @classmethod
    def from_json_object(cls, obj: dict) -> MatchFragment:
        require_fields(cls, obj, "rule", "matches")
        return MatchFragment(
                rule=Rule.from_json_object(obj["rule"]),
                matches=obj["matches"])


@dataclass(frozen=True, slots=True, kw_only=True)
class ProgressFragment:
    """A ProcessFragment represents the progress made in a scan, containing
    both the matches made so far and the remainder of the Rule to be
    evaluated."""
    rule: Rule
    matches: list[MatchFragment]

    def to_json_object(self):
        return {
            "rule": self.rule.to_json_object(),
            "matches": [m.to_json_object() for m in self.matches]
        }

    @classmethod
    def from_json_object(cls, obj: dict) -> ProgressFragment:
        require_fields(cls, obj, "rule", "matches")
        return ProgressFragment(
                rule=Rule.from_json_object(obj["rule"]),
                matches=[MatchFragment.from_json_object(mf)
                         for mf in obj["matches"]])


@dataclass(frozen=True, slots=True, kw_only=True)
class ScannerFragment:
    """A ScannerFragment is a reference to a scanner job in the OSdatascanner
    admin module. (It also carries some settings that are relevant to the
    report module.)"""
    pk: int
    name: str
    test: bool = False
    keep_fp: bool = False

    def to_json_object(self):
        return {
            "pk": self.pk,
            "name": self.name,
            "test": self.test,
            "keep_fp": self.keep_fp
        }

    @classmethod
    def from_json_object(cls, obj: dict) -> ScannerFragment:
        require_fields(cls, obj, "pk", "name")
        return ScannerFragment(
            pk=obj["pk"], name=obj["name"],
            test=obj.get("test", False),
            keep_fp=obj.get("keep_fp", False))


@dataclass(frozen=True, slots=True, kw_only=True)
class OrganisationFragment:
    """An OrganisationFragment is a reference to an organisation (i.e., an
    Organization object) in the OSdatascanner admin and report modules."""
    name: str
    uuid: Optional[UUID]

    def to_json_object(self):
        return {
            "name": self.name,
            "uuid": str(self.uuid) if self.uuid else None
        }

    @classmethod
    def from_json_object(cls, obj: dict | str) -> OrganisationFragment:
        # can't use require_fields here
        if isinstance(obj, dict):
            return OrganisationFragment(
                    name=obj["name"],
                    uuid=UUID(uv) if (uv := obj["uuid"]) else None)
        elif isinstance(obj, str):
            # Organisation fragments created between versions 3.3.3 and 3.6.0
            # inclusive were just names
            return OrganisationFragment(name=obj, uuid=None)
        else:
            raise TypeError


@dataclass(frozen=True, slots=True, kw_only=True)
class ScanTagFragment:
    """A ScanTagFragment identifies a particular execution of a scanner."""

    time: Optional[datetime]
    """The time at which the scan was started, if known."""

    user: Optional[str]
    """The username of the user who started the scan, if known. (This value
    will always be None if the scan was started outside of the Django UI, for
    example by the start_scan command or by a cronjob.)"""

    scanner: Optional[ScannerFragment]
    """A reference to the scanner."""

    organisation: Optional[OrganisationFragment]
    """A reference to the organisation to which the scanner belongs."""

    destination: Optional[str] = "pipeline_collector"
    """Not used, but present for backwards compatibility."""

    def to_json_object(self):
        return {
            "time": self.time.isoformat() if self.time else None,
            "user": self.user,
            "scanner": self.scanner.to_json_object() if self.scanner else None,
            "organisation": (self.organisation.to_json_object()
                             if self.organisation
                             else None),
            "destination": self.destination
        }

    @classmethod
    def make_dummy(cls):
        account = "".join(
                random.choice("bdfghjkqvwxyz13579_") for _ in range(0, 10))
        return ScanTagFragment(
                time=datetime.fromtimestamp(
                        random.randint(0, 2**32), tz=tz.gettz()),
                user=f"{account}@placeholder.invalid",
                scanner=ScannerFragment(
                        pk=random.randint(0, 1000000000),
                        name="Search for Datas"),
                organisation=OrganisationFragment(
                        name="Placeholder Heavy Industries, Ivld.",
                        uuid=uuid.uuid4()
                ))

    @classmethod
    def from_json_object(cls, obj: dict | str) -> ScanTagFragment:
        # can't use require_fields here
        try:
            if isinstance(obj, dict):
                return ScanTagFragment(
                        time=parse_datetime(obj["time"]),
                        user=obj["user"],  # can be None, must be present
                        scanner=ScannerFragment.from_json_object(obj["scanner"]),
                        organisation=OrganisationFragment.from_json_object(
                                obj["organisation"]))
            elif isinstance(obj, str):
                # Scan tags created between versions 3.0.0 and 3.3.2 inclusive
                # were just simple timestamps
                return ScanTagFragment(
                        time=parse_datetime(obj),
                        user=None, scanner=None, organisation=None)
            else:
                raise TypeError
        except KeyError:
            warnings.warn("trying to decode unrecognised scan tag object")
            if not isinstance(obj, dict):
                raise TypeError
            time = obj.get("time")
            user = obj.get("user")
            scanner = obj.get("scanner")
            organisation = obj.get("organisation")
            return ScanTagFragment(
                    time=parse_datetime(time) if time else None,
                    user=user or None,
                    scanner=ScannerFragment.from_json_object(
                            scanner) if scanner else None,
                    organisation=OrganisationFragment.from_json_object(
                            organisation) if organisation else None)


@dataclass(frozen=True, slots=True, kw_only=True)
class ScanSpecMessage:
    """A ScanSpecMessage is a complete scan task for the scanner engine."""

    scan_tag: ScanTagFragment
    """The identifier of this scan. (The pipeline unpacks this value to ensure
    its validity, but it's only actually used by the report module.)"""

    source: Source
    """The data source to be scanned."""

    rule: Rule
    """The rule to evaluate against the given data source."""

    configuration: dict
    """Extra configuration options, if any, for the scan task.

    The only configuration option presently supported is "skip_mime_types", a
    list of MIME types ("image/png") or simple MIME type wildcards ("image/*")
    for which OCR should not be performed."""

    progress: Optional[ProgressFragment]
    """The progress made through rule execution so far. For internal use only.

    This field is set when the pipeline's processor stage needs to refer a
    file back to the explorer stage, and is used to make sure that we don't
    evaluate a rule against both a container and the files that it contains.
    Consider a Zip file, for example, downloaded since the last scan was run
    yesterday morning, but whose sub-files have much older modification dates:
    this morning's incremental scan should only look at the modification
    timestamp of the container and not of the sub-files.

    It is almost always a mistake to set or examine this field in any context
    other than in the interplay between processor and explorer, and even in
    that case the pipeline blanks it out immediately after that to avoid
    confusion."""

    filter_rule: Optional[Rule]

    explorer_queue: str = "os2ds_scan_specs"  # os2ds_scan_specs compatability fallback.
    """The RabbitMQ queue containing sources that should be explored by a
    top-level explorer process. The admin module sends scan specs here, but the
    pipeline can also write to this queue when scanning a meta-source (that is,
    one that finds new sources and not directly scannable handles).

    Note that meta-sources are deprecated, as they make it much harder for the
    admin module to keep track of which data sources have actually been
    scanned. Instead, just send multiple scan specs with the same tag but
    different data sources to the pipeline."""

    conversion_queue: str = "os2ds_conversions"  # compatability fallback.
    """The RabbitMQ queue to which the pipeline's explorer stage should send
    conversion tasks."""

    def to_json_object(self):
        return {
            "scan_tag": self.scan_tag.to_json_object(),
            "source": self.source.to_json_object(),
            "rule": self.rule.to_json_object(),
            "configuration": self.configuration or {},
            "filter_rule": (
                self.filter_rule.to_json_object()
                if self.filter_rule else None),
            "progress": (
                    self.progress.to_json_object() if self.progress else None),
            "explorer_queue": self.explorer_queue,
            "conversion_queue": self.conversion_queue,
        }

    @classmethod
    def from_json_object(cls, obj: dict) -> ScanSpecMessage:
        require_fields(cls, obj, "scan_tag", "source", "rule")
        # The progress fragment is only present when a scan spec is based on a
        # derived source and so already contains scan progress information
        progress_fragment = obj.get("progress")
        filter_rule = obj.get("filter_rule")
        return ScanSpecMessage(
                scan_tag=ScanTagFragment.from_json_object(obj["scan_tag"]),
                source=Source.from_json_object(obj["source"]),
                rule=Rule.from_json_object(obj["rule"]),
                # The configuration dictionary was added fairly late to scan
                # specs, so not all clients will send it. Add an empty one if
                # necessary
                configuration=obj.get("configuration", {}),
                filter_rule=(
                    SimpleRule.from_json_object(filter_rule)
                    if filter_rule
                    else None),
                progress=(
                    ProgressFragment.from_json_object(progress_fragment)
                    if progress_fragment
                    else None),
                explorer_queue=obj.get("explorer_queue", "os2ds_scan_specs"),
                conversion_queue=obj.get("conversion_queue", "os2ds_conversions")
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class ConversionMessage:
    """A ConversionMessage is a partial scan task for the scanner engine: it
    represents an object and the rule remaining to be evaluated against it.

    ConversionMessages are initially generated by the pipeline's explorer
    stage. They are then consumed by the processor stage, which performs a
    conversion task and produces a RepresentationMessage. This message is then
    sent to the matcher stage, which either produces a new ConversionMessage
    (if a new type of data is required to complete the evaluation of the rule)
    or a MatchesMessage and (optionally) a HandleMessage, if evaluation is
    complete."""

    scan_spec: ScanSpecMessage
    """The complete scan task of which this conversion is a part."""

    handle: Handle
    """A reference to the object to be scanned."""

    progress: ProgressFragment
    """The progress made through the evaluation of the rule so far."""

    def to_json_object(self):
        return {
            "scan_spec": self.scan_spec.to_json_object(),
            "handle": self.handle.to_json_object(),
            "progress": self.progress.to_json_object()
        }

    @classmethod
    def from_json_object(cls, obj: dict) -> ConversionMessage:
        require_fields(cls, obj, "scan_spec", "handle", "progress")
        return ConversionMessage(
                scan_spec=ScanSpecMessage.from_json_object(obj["scan_spec"]),
                handle=Handle.from_json_object(obj["handle"]),
                progress=ProgressFragment.from_json_object(obj["progress"]))


@dataclass(frozen=True, slots=True, kw_only=True)
class RepresentationMessage:
    """A RepresentationMessage contains zero or more specific converted forms
    of an object against which a rule can be evaluated.

    (See ConversionMessage for more information about the flow this message
    participates in.)"""

    scan_spec: ScanSpecMessage
    """The complete scan task of which this representation is a part."""

    handle: Handle
    """A reference to the object to be scanned."""

    progress: ProgressFragment
    """The progress made through the evaluation of the rule so far."""

    representations: dict
    """The representations of the object made available to the pipeline's
    matcher stage."""

    def to_json_object(self):
        return {
            "scan_spec": self.scan_spec.to_json_object(),
            "handle": self.handle.to_json_object(),
            "progress": self.progress.to_json_object(),
            "representations": self.representations
        }

    @classmethod
    def from_json_object(cls, obj: dict) -> RepresentationMessage:
        require_fields(
                cls, obj, "scan_spec", "handle", "progress", "representations")
        return RepresentationMessage(
                scan_spec=ScanSpecMessage.from_json_object(obj["scan_spec"]),
                handle=Handle.from_json_object(obj["handle"]),
                progress=ProgressFragment.from_json_object(obj["progress"]),
                representations=obj["representations"])


@dataclass(frozen=True, slots=True, kw_only=True)
class _PointsAtHandle:
    """Convenience mixin for message dataclasses that carry a ScanTagFragment
    and a Handle."""

    scan_tag: ScanTagFragment
    """The complete scan task of which this handle is a part."""

    handle: Handle


@dataclass(frozen=True, slots=True, kw_only=True)
class HandleMessage(_PointsAtHandle):
    """A HandleMessage indicates that matches were found for the given object,
    and that metadata should be extracted from it. The pipeline's matcher stage
    generates these and sends them to the tagger stage."""

    def to_json_object(self):
        return {
            "scan_tag": self.scan_tag.to_json_object(),
            "handle": self.handle.to_json_object()
        }

    @classmethod
    def from_json_object(cls, obj: dict) -> HandleMessage:
        require_fields(cls, obj, "scan_tag", "handle")
        return HandleMessage(
                scan_tag=ScanTagFragment.from_json_object(obj["scan_tag"]),
                handle=Handle.from_json_object(obj["handle"]))


@dataclass(frozen=True, slots=True, kw_only=True)
class MetadataMessage(_PointsAtHandle):
    """A MetadataMessage contains all of the metadata extracted from a given
    object. The pipeline's tagger stage generates these and sends them to the
    exporter stage."""

    metadata: dict[str, Any]
    """Zero or more string-value pairs of metadata items extracted from the
    object. The report module uses this information to work out which users
    are responsible for resolving a match."""

    def to_json_object(self):
        return {
            "scan_tag": self.scan_tag.to_json_object(),
            "handle": self.handle.to_json_object(),
            "metadata": self.metadata
        }

    @classmethod
    def from_json_object(cls, obj: dict) -> MetadataMessage:
        require_fields(cls, obj, "scan_tag", "handle", "metadata")
        return MetadataMessage(
                scan_tag=ScanTagFragment.from_json_object(obj["scan_tag"]),
                handle=Handle.from_json_object(obj["handle"]),
                metadata=obj["metadata"])


@dataclass(frozen=True, slots=True, kw_only=True)
class MatchesMessage:
    """A MatchesMessage represents the conclusion of rule evaluation for a
    given object. The pipeline's matcher stage will produce one of these for
    every input object in the end."""

    scan_spec: ScanSpecMessage
    """The complete scan task of which this handle is a part."""

    handle: Handle
    """A reference to the object that was scanned."""

    matched: bool
    """Whether or not the rule associated with this scan task was satisfied by
    this object."""

    matches: Sequence[MatchFragment]
    """All of the intermediary SimpleRules and results produced while scanning
    this object, whether or not the rule as a whole produced a match."""

    @property
    def sensitivity(self):  # noqa: CCR001, too high cognitive complexity
        """Computes the overall sensitivity of the matches contained in this
        message (i.e., the highest sensitivity of any submatch), or None if
        there are no matches."""
        if not self.matches:
            return None
        else:

            def _cms(fragment):  # noqa: CCR001, E501 too high cognitive complexity
                """Computes the sensitivity of a set of results returned by a
                rule, returning (in order of preference) the highest
                sensitivity (lower than that of the rule) associated with a
                match, the sensitivity of the rule, or 0."""
                rule_sensitivity = (
                    fragment.rule.sensitivity.value
                    if fragment.rule.sensitivity
                    else None)

                max_sub = None
                if (rule_sensitivity is not None
                        and fragment.matches is not None):
                    for match_dict in fragment.matches:
                        if "sensitivity" in match_dict:
                            sub = match_dict["sensitivity"]
                            if max_sub is None or sub > max_sub:
                                max_sub = sub
                if max_sub is not None:
                    # Matches can only have a lower sensitivity than their
                    # rule, never a higher one
                    return min(rule_sensitivity or 0, max_sub)
                elif rule_sensitivity is not None:
                    return rule_sensitivity
                else:
                    return 0
            return Sensitivity(max([_cms(frag) for frag in self.matches]))

    def to_json_object(self):
        return {
            "scan_spec": self.scan_spec.to_json_object(),
            "handle": self.handle.to_json_object(),
            "matched": self.matched,
            "matches": list([mf.to_json_object() for mf in self.matches])
        }

    @property
    def probability(self):  # noqa: CCR001, too high cognitive complexity
        """Computes the overall probability of the matches contained in this
        message (i.e., the highest probability of any submatch), or None if
        there are no matches."""
        if not self.matches:
            return None
        else:

            def _cmp(fragment):
                """Computes the probability of a set of results returned by a
                rule, returning the highest probability associated with a
                match."""
                max_sub = None
                if fragment.matches is not None:
                    for match_dict in fragment.matches:
                        if "probability" in match_dict:
                            sub = match_dict["probability"]
                            if max_sub is None or sub > max_sub:
                                max_sub = sub
                if max_sub is not None:
                    return max_sub
                else:
                    return 0
        return max([_cmp(frag) for frag in self.matches])

    @classmethod
    def from_json_object(cls, obj: dict) -> MatchesMessage:
        # WARNING! Migration 0052 in the report app is dependent on this method.
        # Alter with care!
        require_fields(cls, obj, "scan_spec", "handle", "matched", "matches")
        return MatchesMessage(
                scan_spec=ScanSpecMessage.from_json_object(obj["scan_spec"]),
                handle=Handle.from_json_object(obj["handle"]),
                matched=obj["matched"],
                matches=[MatchFragment.from_json_object(mf)
                         for mf in obj["matches"]])


@dataclass(frozen=True, slots=True, kw_only=True)
class ProblemMessage:
    """A ProblemMessage represents an error encountered by the scanner engine
    during a scan."""

    scan_tag: ScanTagFragment
    """The identifier of this scan."""

    source: Optional[Source]
    """If the error was encountered during exploration (for example, if the
    API key or service account provided was not valid), a reference to the
    data source being explored."""

    handle: Optional[Handle]
    """If the error was encountered during the scan or exploration of a
    specific object (for example, if a file was deleted between its initial
    exploration and being scanned, or if a file is locked or corrupt), a
    reference to the object."""

    message: str
    """A short description of the error."""

    irrelevant: bool = False
    """Whether or not the object is still relevant to the scan. (Set by the
    admin module if a user is removed from the set of covered accounts.)"""

    def to_json_object(self):
        return {
            "scan_tag": self.scan_tag.to_json_object(),
            "source": self.source.to_json_object() if self.source else None,
            "handle": self.handle.to_json_object() if self.handle else None,
            "message": self.message,
            "irrelevant": self.irrelevant
        }

    @classmethod
    def from_json_object(
            cls, obj: dict) -> ProblemMessage | ContentMissingMessage:
        require_fields(cls, obj, "scan_tag", "message")
        scan_tag = ScanTagFragment.from_json_object(obj["scan_tag"])
        source = obj.get("source")
        handle = obj.get("handle")
        if obj.get("missing") is True:
            logger.warning(
                    "converting deprecated ProblemMessage(missing=True) to"
                    " modern ContentMissingMessage",
                    scan_tag=scan_tag)
            return ContentMissingMessage(
                    scan_tag=scan_tag,
                    handle=Handle.from_json_object(handle))
        else:
            return ProblemMessage(
                    scan_tag=scan_tag,
                    source=Source.from_json_object(source) if source else None,
                    handle=Handle.from_json_object(handle) if handle else None,
                    message=obj["message"],
                    irrelevant=obj.get("irrelevant", False))


@dataclass(frozen=True, slots=True, kw_only=True)
class StatusMessage:
    """A StatusMessage is an informational message sent by the pipeline's
    explorer and worker stages to the admin module describing the work that has
    been performed. The admin module uses these updates to give the user
    details about the progress of a scan."""

    scan_tag: ScanTagFragment
    """The identifier of this scan."""

    message: str = ""
    """A short message connected with this update, if appropriate."""

    status_is_error: bool = False
    """Indicates whether or not the message is an error message."""

    # Emitted by (top-level) explorers
    total_objects: Optional[int] = None
    """The number of objects found during an exploration pass."""

    new_sources: Optional[int] = None
    """The number of new data sources produced and enqueued during an
    exploration pass."""

    # Emitted by workers
    object_size: Optional[int] = None
    """The size (in bytes) of the object that has been scanned."""

    object_type: Optional[str] = None
    """The MIME type of the object that has just been scanned."""

    matches_found: Optional[int] = None
    """The number of matches found in the object that has just been scanned."""

    skipped_by_last_modified: Optional[int] = None
    """The number of objects skipped due only to their date of last
    modification. (Emitted by the matcher stage.)"""

    process_time_worker: Optional[float] = None
    """The total clock time spent on this object (that is, the difference in
    seconds between the time processing began and the time it finished).

    (Historically this field contained the elapsed CPU time of the Python
    process, but this didn't make much sense as a user-visible metric.)"""

    content_identifier: Optional[str] = None
    """The content identifier of the of the object that has just been scanned.
    This is usually the hash value of the object's content or another string that
    uniquely identifies the content of an object."""

    def to_json_object(self):
        return {
            "scan_tag": self.scan_tag.to_json_object(),
            "message": self.message,
            "status_is_error": self.status_is_error,

            "total_objects": self.total_objects,
            "new_sources": self.new_sources,
            "matches_found": self.matches_found,
            "skipped_by_last_modified": self.skipped_by_last_modified,

            "object_size": self.object_size,
            "object_type": self.object_type,
            "content_identifier": self.content_identifier,

            "process_time_worker": self.process_time_worker,
        }

    @classmethod
    def from_json_object(cls, obj: dict) -> StatusMessage:
        require_fields(cls, obj, "scan_tag")
        return StatusMessage(
                scan_tag=ScanTagFragment.from_json_object(obj["scan_tag"]),
                message=obj.get("message", ""),
                status_is_error=obj.get("status_is_error", False),
                total_objects=obj.get("total_objects"),
                new_sources=obj.get("new_sources"),
                matches_found=obj.get("matches_found"),
                skipped_by_last_modified=obj.get("skipped_by_last_modified"),
                object_size=obj.get("object_size"),
                object_type=obj.get("object_type"),
                process_time_worker=obj.get("process_time_worker"),
                content_identifier=obj.get("content_identifier"))


def check_metadata_dict(cls_metadata, obj_metadata):
    for key, expected_value in cls_metadata.items():
        obj_value = obj_metadata.get(key)
        if obj_value != expected_value:
            raise ValueError(
                    f"metadata field {key!r}:"
                    f" expected {expected_value!r}, but got {obj_value!r}")


@dataclass(frozen=True, slots=True, kw_only=True)
class ContentMissingMessage(_PointsAtHandle):
    """A ContentMissingMessage is emitted by the pipeline's processor stage (to
    both the admin and report modules) if an object with an associated
    conversion task could not be found.

    This situation was once represented by a ProblemMessage(missing=True)
    object; this is now deprecated, and the ProblemMessage.from_json_object()
    function will automatically convert such messages to instances of this
    class."""

    METADATA = {
        "domain": "os2datascanner.engine2.pipeline.messages",
        "type": "ContentMissingMesage"
    }

    def to_json_object(self):
        return {
            "scan_tag": self.scan_tag.to_json_object(),
            "handle": self.handle.to_json_object(),

            "__metadata": self.METADATA
        }

    @staticmethod
    def test(obj) -> bool:
        try:
            check_metadata_dict(
                    ContentMissingMessage.METADATA, obj.get("__metadata", {}))
            return True
        except ValueError:
            return False

    @classmethod
    def from_json_object(cls, obj: dict) -> ContentMissingMessage:
        check_metadata_dict(cls.METADATA, obj["__metadata"])
        return ContentMissingMessage(
                scan_tag=ScanTagFragment.from_json_object(obj["scan_tag"]),
                handle=Handle.from_json_object(obj["handle"]))


@dataclass(frozen=True, slots=True, kw_only=True)
class ContentSkippedMessage(_PointsAtHandle):
    """A ContentSkippedMessage is emitted by the pipeline's processor stage if
    the configuration of a scanner job has prohibited the content of an object
    from being scanned."""

    METADATA = {
        "domain": "os2datascanner.engine2.pipeline.messages",
        "type": "ContentSkippedMessage"
    }

    def to_json_object(self):
        return {
            "scan_tag": self.scan_tag.to_json_object(),
            "handle": self.handle.to_json_object(),

            "__metadata": self.METADATA
        }

    @staticmethod
    def test(obj) -> bool:
        try:
            check_metadata_dict(
                    ContentSkippedMessage.METADATA, obj.get("__metadata", {}))
            return True
        except ValueError:
            return False

    @classmethod
    def from_json_object(cls, obj: dict) -> ContentSkippedMessage:
        check_metadata_dict(cls.METADATA, obj["__metadata"])
        return ContentSkippedMessage(
                scan_tag=ScanTagFragment.from_json_object(obj["scan_tag"]),
                handle=Handle.from_json_object(obj["handle"]))


@dataclass(frozen=True, slots=True, kw_only=True)
class CommandMessage:
    """A CommandMessage is an order from the admin module. As they may modify
    the treatment of other messages, they should be processed as soon as
    possible, and so should be sent on a high-priority queue."""

    abort: Optional[ScanTagFragment] = None
    """If set, the scan tag of a scan that should no longer be processed by the
    pipeline. Pipeline components should acknowledge and silently ignore all
    messages carrying this tag.

    To avoid accumulating tags indefinitely, pipeline components should store
    them in a ring buffer of a reasonable size. (What "reasonable" means
    depends a bit on the installation and on how many concurrent scans it can
    be expected to perform.)"""

    log_level: Optional[int] = None
    """If set, the new logging level of the "os2datascanner" root logger."""

    profiling: Optional[bool] = None
    """If set, whether or not to perform runtime profiling.

    As a side effect of processing a message with this attribute set, the
    target process will print and clear any profiling statistics it might
    already have collected."""

    def to_json_object(self):
        return {
            "abort": self.abort.to_json_object() if self.abort else None,
            "log_level": self.log_level,
            "profiling": self.profiling
        }

    @classmethod
    def from_json_object(cls, obj: dict) -> CommandMessage:
        require_fields(cls, obj, "abort")
        abort = obj.get("abort")
        return CommandMessage(
                abort=ScanTagFragment.from_json_object(abort)
                if abort else None,
                log_level=obj.get("log_level"),
                profiling=obj.get("profiling"))
