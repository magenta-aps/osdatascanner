# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""Coordination between workers so that identical content is converted once.

Two keys per piece of content, namespaced per scan so that nothing is reused
across scans:

    claim:{scan}:{cid}   the lease held by the worker currently converting
    result:{scan}:{cid}  the finished result, for other copies to replay

Everything here fails open: an unreachable store costs performance, never
correctness.
"""

import gzip
import json
import time
from contextlib import contextmanager
from hashlib import blake2b
from dataclasses import dataclass
from typing import Iterator, Optional
from uuid import uuid4
import redis

import structlog

from ... import settings
from ...conversions import conversion_exists
from ...conversions.types import OutputType
from ...model.core import Handle, Source
from ...utilities import mime
from ...utilities.backoff import TimeoutRetrier
from ..messages import ScanTagFragment

logger = structlog.get_logger("deduplication")


# Identifies this worker process as the holder of a claim, so that a lease can
# only be renewed or released by the worker that took it.
WORKER_ID = uuid4().hex


# LUA script to renew the lease only if we still hold it, so that a worker
# whose lease has already expired cannot reclaim it underneath the worker that
# took over.
_RENEW_SCRIPT = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('pexpire', KEYS[1], ARGV[2])
else
    return 0
end
"""

# LUA script to release the lease only if we still hold it, so that a worker
# finishing late does not delete the claim of the worker that took over from
# it.
_RELEASE_SCRIPT = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
else
    return 0
end
"""


def scan_identity(scan_tag: ScanTagFragment) -> Optional[str]:
    """Derives a stable per-scan string from a ScanTagFragment, keeping one
    scan's claims and results separate from every other scan's.

    None when the tag does not identify a scan, which means not coordinating
    over the object at all: a placeholder would file every such scan under one
    identity and replay one scan's results for another's objects."""
    if (scanner := scan_tag.scanner) is None or (started := scan_tag.time) is None:
        return None

    return f"{scanner.pk}:{started.isoformat()}"


@dataclass(frozen=True, slots=True, kw_only=True)
class ContentIdentity:
    """What a piece of content is, as far as sharing a conversion goes: the
    digest of its bytes together with the MIME type those bytes will be
    converted as.

    The type is not redundant: compute_type() prefers the type guessed from an
    object's name, so the same bytes under two names can go to two converters."""
    digest: str
    mime_type: str

    def __str__(self):
        return f"{self.digest}:{self.mime_type}"


def _pack(payload: dict) -> bytes:
    """Serialises a result for the store, compressed when that makes it
    smaller."""
    raw = json.dumps(payload).encode()
    # mtime, which gzip stamps with the current time by default, would make the
    # same payload pack to different bytes every time.
    packed = gzip.compress(raw, compresslevel=1, mtime=0)

    return packed if len(packed) < len(raw) else raw


def _unpack(raw: bytes) -> dict:
    """Reads back whatever _pack wrote, compressed or not, raising if it cannot.

    Told apart by looking for JSON."""
    if raw[:1] != b"{":
        raw = gzip.decompress(raw)

    # Checked rather than assumed: the bytes come from a store anything can
    # write to, and JSON that is not an object would answer the questions the
    # callers ask of a result by raising somewhere further away from here.
    if not isinstance(payload := json.loads(raw), dict):
        raise ValueError(
                f"a stored result must be an object, not {type(payload)}")

    return payload


class ClaimStore:
    """A shared store of conversion claims and results, backed by Valkey (or any
    wire-compatible Redis).

    The cid arguments below take the composite key from content_key(). Instances
    wrap a client rather than creating one; use get_store() for the process-wide
    instance built from the pipeline settings."""

    def __init__(
            self, client, *, lease_ms: int, result_ttl: int,
            owner: Optional[str] = None):
        self._client = client
        self._lease_ms = lease_ms
        self._result_ttl = result_ttl
        # Identifies the holder of a claim. Defaults to this process, but is
        # settable so that tests can pit two owners against each other.
        self._owner = owner or WORKER_ID
        self._renew = client.register_script(_RENEW_SCRIPT)
        self._release = client.register_script(_RELEASE_SCRIPT)

    @property
    def lease_ms(self) -> int:
        return self._lease_ms

    @staticmethod
    def _claim_key(scan_id: str, cid: str) -> str:
        return f"claim:{scan_id}:{cid}"

    @staticmethod
    def _result_key(scan_id: str, cid: str) -> str:
        return f"result:{scan_id}:{cid}"

    @staticmethod
    def _index_key(scan_id: str) -> str:
        return f"keys:{scan_id}"

    def _index(self, pipe, scan_id: str, key: str) -> None:
        """Queues the bookkeeping that lets purge() find @key again.

        Every key a scan writes is named in one set, so that clearing up after
        the scan reads that set instead of walking the whole store. Written in
        the same round trip as the key itself, and expiring no sooner than the
        longest-lived key it names."""
        index = self._index_key(scan_id)
        pipe.sadd(index, key)
        pipe.expire(index, self._result_ttl)

    def get_result(self, scan_id: str, cid: str) -> Optional[dict]:
        """Returns the stored result for this content, or None if there isn't
        one or it could not be retrieved: convert the content in that case.

        Reading renews a result, so its expiry means "unused for a while"."""
        try:
            pipe = self._client.pipeline(transaction=False)
            pipe.getex(self._result_key(scan_id, cid), ex=self._result_ttl)
            # A no-op if the index is already gone, which means the scan is over
            # and nothing is left to name.
            pipe.expire(self._index_key(scan_id), self._result_ttl)
            raw = pipe.execute()[0]
        except Exception as ex:
            logger.warning(
                    "could not read deduplication result, will convert",
                    error=f"{type(ex).__name__}: {ex}")
            return None
        if raw is None:
            return None
        try:
            return _unpack(raw)
        except Exception:
            logger.warning(
                    "discarding unreadable deduplication result", exc_info=True)
            return None

    def claim(self, scan_id: str, cid: str) -> bool:
        """Attempts to take the claim on converting this content: True if this
        worker now holds it and should convert, False if another worker does.

        True as well when the store could not be reached, so that an unavailable
        store has everyone convert rather than everyone wait."""
        key = self._claim_key(scan_id, cid)
        try:
            pipe = self._client.pipeline(transaction=False)
            pipe.set(key, self._owner, nx=True, px=self._lease_ms)
            # Indexed whether or not the claim is taken here: the key is named
            # the same whichever worker holds it.
            self._index(pipe, scan_id, key)
            taken = pipe.execute()[0]
        except Exception as ex:
            logger.warning(
                    "could not take deduplication claim, will convert",
                    error=f"{type(ex).__name__}: {ex}")
            return True
        return bool(taken)

    def renew(self, scan_id: str, cid: str) -> None:
        """Extends this worker's lease on an in-flight conversion by a further
        lease period."""
        try:
            self._renew(
                    keys=[self._claim_key(scan_id, cid)],
                    args=[self._owner, self._lease_ms])
        except Exception as ex:
            # A missed renewal is not fatal on its own: the lease may still be
            # valid, and if it isn't, the worst case is that another worker
            # converts the same content.
            logger.debug(
                    "could not renew deduplication lease", error=f"{type(ex).__name__}: {ex}")

    def store_result(self, scan_id: str, cid: str, result: dict) -> None:
        """Publishes the result of converting this content, for other copies to
        replay against their own objects."""
        try:
            pipe = self._client.pipeline(transaction=False)
            pipe.set(
                    (key := self._result_key(scan_id, cid)),
                    _pack(result), ex=self._result_ttl)
            self._index(pipe, scan_id, key)
            pipe.execute()
        except Exception as ex:
            logger.warning(
                    "could not store deduplication result", error=f"{type(ex).__name__}: {ex}")

    def purge(self, scan_id: str) -> int:
        """Deletes everything this scan left behind, returning how many keys
        were deleted.

        Reads the scan's own index rather than walking the store."""
        index = self._index_key(scan_id)
        deleted = 0
        try:
            batch = []
            # UNLINK rather than DEL: we don't need to wait for the data
            # to be deleted. Valkey will handle the deletion
            # asynchronously.
            for key in self._client.sscan_iter(index, count=1000):
                batch.append(key)
                if len(batch) >= 1000:
                    deleted += self._client.unlink(*batch)
                    batch = []
            if batch:
                deleted += self._client.unlink(*batch)
            self._client.unlink(index)
        except Exception as ex:
            logger.warning(
                    "could not purge deduplication keys",
                    scan_id=scan_id, error=f"{type(ex).__name__}: {ex}")

        return deleted

    def release(self, scan_id: str, cid: str) -> None:
        """Gives up this worker's claim on converting this content."""
        try:
            self._release(
                    keys=[self._claim_key(scan_id, cid)], args=[self._owner])
        except Exception as ex:
            # Leaving the claim behind is harmless: it expires by itself within
            # one lease period.
            logger.debug(
                    "could not release deduplication claim", error=f"{type(ex).__name__}: {ex}")


class Lease:
    """A claim this worker holds while it converts, kept alive by tick().

    tick() is called far more often than the lease needs renewing, so it only
    reaches the store once a third of the lease period has passed."""

    def __init__(self, store: ClaimStore, scan_id: str, cid: str):
        self._store = store
        self._scan_id = scan_id
        self._cid = cid
        self._interval = (store.lease_ms / 1000) / 3
        self._last = time.monotonic()

    def tick(self) -> None:
        """Renews the lease if enough time has passed since the last renewal."""
        now = time.monotonic()
        if now - self._last >= self._interval:
            self._last = now
            self._store.renew(self._scan_id, self._cid)

    def release(self) -> None:
        self._store.release(self._scan_id, self._cid)


_held_leases: list[Lease] = []
"""The claims this worker holds, renewed by renew_claims()."""


@contextmanager
def hold_lease(lease: Lease):
    """Holds a lease for as long as the block runs, and gives it up on the way
    out."""
    _held_leases.append(lease)
    try:
        yield lease
    finally:
        # Removed by identity rather than popped, because a nested conversion's
        # generator can be abandoned while this one is still running.
        _held_leases.remove(lease)
        lease.release()


def renew_claims() -> None:
    """Renews every lease this worker holds."""
    for lease in _held_leases:
        lease.tick()


_settled: list[str] = []
"""The objects a decision has already been made about, by the blocks currently
running."""


@contextmanager
def settled(handle: Handle):
    """Marks, for as long as the block runs, that a decision has been made
    about this object, so that nothing stands aside from it a second time."""
    crunched = handle.crunch(hash=True)
    _settled.append(crunched)
    try:
        yield
    finally:
        _settled.remove(crunched)


def is_settled(handle: Handle) -> bool:
    """Whether a decision has already been made about this object."""
    return handle.crunch(hash=True) in _settled


_store: Optional[ClaimStore] = None
_store_resolved = False


def _dedup_settings() -> dict:
    return settings.pipeline["worker"]["dedup"]


def _flag(value) -> bool:
    """Reads a setting that is meant to be a boolean.

    Overridden through the environment it arrives as a string, and every
    non-empty string is true, so "false" would switch a feature on."""
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    return bool(value)


def identify_timeout() -> float:
    """How long a worker may spend identifying one object's content."""
    return float(_dedup_settings()["identify_timeout"])


_identities: dict[str, Optional[ContentIdentity]] = {}
"""What the objects handled so far turned out to hold, by Handle.

Identifying an object reads all of it, so nothing should ask twice."""


_types: dict[str, Optional[str]] = {}
"""What the objects handled so far turned out to be, by Handle."""


def forget_delivery() -> None:
    """Discards everything remembered about the delivery that has just
    finished: what its objects were identified as, what types they turned out
    to be, and which of them a decision had been made about.

    Clearing _settled is a safety net rather than the owner of that lifetime:
    the blocks in settled() give theirs up themselves."""
    _identities.clear()
    _types.clear()
    _settled.clear()


def clear_scan(scan_tag) -> None:
    """Deletes one scan's claims and results, the scan being over."""
    store = get_store()
    scan_id = scan_identity(scan_tag)

    if store is None or scan_id is None:
        return

    logger.info(
            "clearing this scan's deduplication keys",
            scan_tag=scan_tag, purged=store.purge(scan_id)
        )


def computed_type(handle, resource) -> Optional[str]:
    """The MIME type an object's content will be converted as, or None if it
    could not be computed."""
    if (crunched := handle.crunch(hash=True)) in _types:
        return _types[crunched]

    try:
        _types[crunched] = TimeoutRetrier(max_tries=3, seconds=10).run(
                resource.compute_type)
    except Exception:
        logger.warning(
                "could not compute type, not coordinating this object",
                handle=str(handle), exc_info=True)
        _types[crunched] = None

    return _types[crunched]


def identify(handle, resource) -> Optional[ContentIdentity]:
    """Identifies an object's content by hashing every byte of it, or returns
    None if it could not be identified.

    None is not an error: it means this object cannot be coordinated over and has
    to be converted on its own merits."""
    # Remembered by which object this is rather than by what it holds, that being
    # the answer this is here to avoid computing twice.
    if (crunched := handle.crunch(hash=True)) in _identities:
        return _identities[crunched]

    _identities[crunched] = identity = _identify(handle, resource)
    return identity


def _identify(handle, resource) -> Optional[ContentIdentity]:
    if (mime_type := computed_type(handle, resource)) is None:
        return None

    try:
        # One attempt, unlike the type. Hashing every byte of an object is
        # deterministic, so an attempt that could not finish in the budget has no
        # more reason to finish in an identical second one, and retrying would
        # read the whole object again to reach the same conclusion.
        digest = TimeoutRetrier(
                max_tries=1, seconds=identify_timeout()).run(
                        resource.compute_content_identifier)
        if not digest:
            # Resources that cannot identify their own content -- anything that
            # isn't a file, in practice -- return nothing.
            return None
    except TimeoutError:
        logger.warning(
                "identifying content took too long, not coordinating this"
                " object", handle=str(handle))
        return None
    except Exception:
        logger.warning(
                "could not identify content, not coordinating this object",
                handle=str(handle), exc_info=True)
        return None

    return ContentIdentity(digest=digest, mime_type=mime_type)


def _longest_unrenewed_stretch_ms() -> int:
    """The longest a conversion can run without reaching an abort check, and so
    the shortest lease that will not expire underneath its holder."""
    return 1000 * int(
            int(settings.subprocess["pdf_clean_timeout"])
            + int(settings.pipeline["op_timeout"])
            * int(settings.pipeline["op_tries"]))


def _check_lease_ms(lease_ms: int) -> bool:
    """Warns if the configured lease cannot outlast the conversion it protects,
    returning whether it was found to be too short.

    Warned about because the symptom is silence: a duplicate conversion looks
    exactly like two workers working."""
    if lease_ms >= (floor := _longest_unrenewed_stretch_ms()):
        return False

    logger.warning(
            "deduplication lease is shorter than the longest conversion"
            " stretch that cannot renew it; expect duplicate conversions"
            " of large PDFs",
            lease_ms=lease_ms, minimum_ms=floor)
    return True


def build_client(conf: dict):
    """Builds a connection to the store @conf describes, or returns None if
    there is no host to connect to or no redis package to do it with.

    Connecting is deferred, so a client comes back whether or not the store is
    up."""
    if not conf.get("host"):
        return None

    # Settings overridden through the environment arrive as strings, so every
    # numeric value has to be coerced rather than used as it comes.
    timeout = float(conf["socket_timeout"])
    return redis.Redis(
            host=conf["host"],
            port=int(conf["port"]),
            db=int(conf["db"]),
            # Empty credentials have to become None rather than travelling as
            # they are: an empty password is still a password as far as redis-py
            # is concerned, and it would send an AUTH that a store without
            # credentials rejects.
            username=conf.get("username") or None,
            password=conf.get("password") or None,
            socket_timeout=timeout,
            socket_connect_timeout=timeout,
            health_check_interval=30)


def _build_store() -> Optional[ClaimStore]:
    """Builds a ClaimStore from the pipeline settings, or returns None if
    coordination is switched off, unconfigured, or unavailable."""
    conf = _dedup_settings()
    if not _flag(conf["enabled"]):
        return None

    if (client := build_client(conf)) is None:
        logger.info("deduplication enabled but unavailable, disabling")
        return None

    logger.info(
            "deduplication store configured",
            host=conf["host"], authenticated=bool(conf.get("password")))
    lease_ms = int(conf["lease_ms"])
    _check_lease_ms(lease_ms)
    return ClaimStore(
            client,
            lease_ms=lease_ms,
            result_ttl=int(conf["result_ttl"]))


def get_store() -> Optional[ClaimStore]:
    """Returns the process-wide ClaimStore, or None when workers should not
    coordinate. Built once on first use."""
    global _store, _store_resolved
    if not _store_resolved:
        _store = _build_store()
        _store_resolved = True
    return _store


def reset_store() -> None:
    """Discards the process-wide ClaimStore so that it is rebuilt on next use.
    Intended for tests that change the pipeline settings."""
    global _store, _store_resolved
    _store = None
    _store_resolved = False


# The kinds of input a rule can be evaluated against whose value is a function of
# an object's content alone, so that a result computed from them is equally true
# of any other object with the same content.
CONTENT_DERIVED_OUTPUT_TYPES = frozenset({
    OutputType.Text,
    OutputType.MRZ,
    OutputType.ImageDimensions,
    OutputType.Links,
    OutputType.EmailHeaders,
    # Neither of these looks at the object at all.
    OutputType.AlwaysTrue,
    OutputType.NoConversions,
})


def _canonical(obj):
    """Rewrites parsed JSON so its text does not depend on the order a publisher
    happened to emit list elements in.

    Only the list branch does lasting work: dicts are ordered by sort_keys
    later, and are walked here because their values are where the lists are."""
    if isinstance(obj, dict):
        return {k: _canonical(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return sorted(
                (_canonical(v) for v in obj),
                key=lambda v: json.dumps(v, sort_keys=True))
    else:
        return obj


def _without_synthetic(progress_json):
    """Drops the synthetic fragments from a progress fragment's accumulated
    matches."""
    if not isinstance(progress_json, dict):
        return progress_json

    if not isinstance(matches := progress_json.get("matches"), list):
        return progress_json

    return progress_json | {
        "matches": [
            fragment for fragment in matches
            if not (isinstance(fragment, dict)
                    and isinstance(rule := fragment.get("rule"), dict)
                    and rule.get("synthetic"))
        ],
    }


def progress_fingerprint(progress_json) -> str:
    """Reduces a progress fragment to a string representing the question being
    asked of an object's content."""
    return json.dumps(
            _canonical(_without_synthetic(progress_json)), sort_keys=True)


def content_key(cid: str, progress_json) -> str:
    """Builds the key under which a result is claimed and stored, from the
    content identifier and the progress fragment.

    The content identifier alone is not enough: two copies need not arrive with
    the same question left to answer."""
    try:
        fingerprint = progress_fingerprint(progress_json)
    except Exception:
        # Progress we cannot fingerprint gets a key nothing else will collide
        # with, so this object is effectively uncoordinated.
        logger.warning("could not fingerprint progress", exc_info=True)
        fingerprint = uuid4().hex

    digest = blake2b(fingerprint.encode("utf-8"), digest_size=16).hexdigest()
    return f"{cid}:{digest}"


@dataclass(frozen=True, slots=True, kw_only=True)
class Claimed:
    """This worker holds the claim on converting this content, and is converting
    it on behalf of every copy. Reported before the conversion starts."""
    scan_id: str
    key: str


@dataclass(frozen=True, slots=True, kw_only=True)
class Stored:
    """Another worker has already converted this content, and @payload is what it
    found. Nothing has been converted here."""
    payload: dict


@dataclass(frozen=True, slots=True, kw_only=True)
class Contended:
    """Another worker is converting this content right now, and nothing has been
    converted here. How to wait for it is the caller's business."""
    key: str


OUTCOME = Claimed | Stored | Contended


def plan_conversion(
        conversion, resource,
        required) -> Optional[Claimed | Stored | Contended]:
    """Decides whether this object's content should be converted here: Claimed,
    Stored or Contended, or None to convert it as if nothing were coordinated."""
    store = get_store()
    scan_id = scan_identity(conversion.scan_spec.scan_tag)

    # Everything cheap first: identifying the content reads all of it.
    #
    # The rule is in here because it is the cheapest check of the lot and the
    # one that disqualifies a whole scan at a time: every incremental scan asks
    # a LastModifiedRule first, and reading an object to find that out would
    # make a delta scan read everything it exists to avoid reading.
    if (store is None or scan_id is None
            or is_settled(conversion.handle)
            or not worth_coordinating(conversion.handle)
            or will_be_skipped(conversion)
            or not is_shareable(conversion.progress.rule)):
        return None

    # The type before the digest: computing it reads 512 bytes, and it settles
    # whether reading the rest of the object is worth anything at all.
    mime_type = computed_type(conversion.handle, resource)
    if mime_type is None or not can_convert(resource, required, mime_type):
        return None

    if (identity := identify(conversion.handle, resource)) is None:
        return None

    key = content_key(
            str(identity), conversion.progress.to_json_object())

    # Read before the claim is attempted: a claim is deleted by the worker that
    # finishes with it, so claiming first would take an uncontended claim on
    # content whose result was already waiting.
    if (payload := store.get_result(scan_id, key)) is not None:
        # An unshareable marker means nothing is coming. Do not wait for it.
        return None if is_unshareable(payload) else Stored(payload=payload)

    if store.claim(scan_id, key):
        logger.info(
                "took the claim on this content, converting for every copy",
                handle=str(conversion.handle))
        return Claimed(scan_id=scan_id, key=key)

    # Read again, the holder may have finished while the claim was attempted.
    if (payload := store.get_result(scan_id, key)) is not None:
        return None if is_unshareable(payload) else Stored(payload=payload)

    return Contended(key=key)


def is_shareable(rule) -> bool:
    """Decides whether a rule's conclusion about one object may be reported for
    another object with identical content.

    True only if every leaf of the tree is."""
    # A rule that has already been fully resolved constrains nothing.
    if rule is True or rule is False:
        return True

    try:
        leaves = rule.flatten()
    except Exception:
        logger.warning(
                "could not flatten rule, not coordinating", exc_info=True)
        return False

    return all(
            getattr(leaf, "operates_on", None) in CONTENT_DERIVED_OUTPUT_TYPES
            for leaf in leaves)


def worth_coordinating(handle: Handle) -> bool:
    """Decides whether an object is expensive enough to convert that
    coordinating over it pays for itself."""
    conf = _dedup_settings()

    if mime.is_one_of(handle.guess_type(), conf["always_types"]):
        return True

    try:
        size = int(handle.hint("size"))
    except (TypeError, ValueError):
        # Missing, or not a number. Either way it decides nothing.
        return False

    return size >= int(conf["min_size"])


def can_convert(resource, required, mime_type: str) -> bool:
    """False when nothing converts the type and nothing reinterprets it as a Source
    either."""
    return (conversion_exists(resource, required, mime_override=mime_type)
            or Source.mime_handler_exists(mime_type))


def will_be_skipped(conversion) -> bool:
    """Whether the scan is configured not to convert this object's type, in
    which case there is nothing to coordinate over."""
    skip = conversion.scan_spec.configuration.get("skip_mime_types") or ()
    return mime.is_one_of(conversion.handle.guess_type(), skip)


def swap_root(handle: Handle, old_root: Handle, new_root: Handle) -> Handle:
    """Rebuilds the handle so it points to the new root."""
    if handle == old_root:
        # The result belongs to the root object itself, so there is no tree
        # beneath it to rebuild.
        return new_root

    for step in handle.walk_up():
        derived = step.source
        if derived.handle == old_root:
            return handle.remap({derived: type(derived)(new_root)})

    raise ValueError(
            "BUG: attempted to swap the root of a Handle that does not descend"
            f" from it: {handle!r} is not under {old_root!r}")


# Published under the result key by a worker that converted the content but
# cannot offer its result to the other copies, so that they convert now rather
# than waiting for something that is never coming.
UNSHAREABLE_RESULT = {"unshareable": True}


def is_unshareable(payload: dict) -> bool:
    """Whether a stored result is a marker saying "do not wait for me"."""
    return bool(payload.get("unshareable"))


def encode_result(root: Handle, results: list[tuple[Handle, bool, list]]) -> dict:
    """Packs the outcome of converting and matching one object into a form
    another worker can replay against its own copy of that content."""
    pool: list[dict] = []
    index: dict[str, int] = {}

    def intern(rule: dict) -> int:
        key = json.dumps(rule, sort_keys=True)
        if key not in index:
            index[key] = len(pool)
            pool.append(rule)
        return index[key]

    encoded = [
        {
            "handle": handle.censor().to_json_object(),
            "matched": matched,
            "matches": [
                fragment | {"rule": intern(fragment["rule"])}
                for fragment in matches
            ],
        }
        for handle, matched, matches in results
    ]

    return {"root": root.censor().to_json_object(),
            "rules": pool,
            "results": encoded}


def decode_result(
        payload: dict,
        new_root: Handle) -> Iterator[tuple[Handle, bool, list]]:
    """Unpacks a stored result, yielding (handle, matched, matches) with every
    handle rebuilt to point into new_root.

    Raises an exception if the payload cannot be understood, which the caller
    should treat as a cache miss and convert the content itself."""
    old_root = Handle.from_json_object(payload["root"])
    rules = payload.get("rules") or ()
    for entry in payload["results"]:
        handle = Handle.from_json_object(entry["handle"])
        yield (
                swap_root(handle, old_root, new_root),
                entry["matched"],
                [_with_rule(fragment, rules) for fragment in entry["matches"]])


def _with_rule(fragment: dict, rules) -> dict:
    """Puts a fragment's rule back where MatchFragment expects to find it.

    A rule stored inline rather than by index is a result from a build that
    predates the pool, and travels as it is."""
    rule = fragment["rule"]

    return fragment if isinstance(rule, dict) else fragment | {
        "rule": rules[rule]}
