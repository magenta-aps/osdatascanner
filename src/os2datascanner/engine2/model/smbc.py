import io
from os import stat_result, O_RDONLY
import enum
import errno
import structlog
import smbc
from typing import Optional
from urllib.parse import quote, urlunsplit
from pathlib import PureWindowsPath
from datetime import datetime
from dateutil.tz import gettz
from operator import or_
from functools import reduce
from contextlib import contextmanager

from os2datascanner.engine2.rules.utilities.analysis import find_cutoff

from ..utilities.backoff import DefaultRetrier
from ..utilities.datetime import parse_datetime, unparse_datetime
from ..conversions.types import OutputType
from ..conversions.utilities.navigable import make_values_navigable
from .core import Source, Handle, FileResource
from .core.errors import UncontactableError
from .file import stat_attributes


logger = structlog.get_logger("engine2")

XATTR_DOS_ATTRIBUTES = "system.dos_attr.mode"
"""The attribute name for a file's mode flags. (This is not documented in
pysmbc, but it is in the underlying libsmbclient library.)"""


IGNORABLE_SMBC_EXCEPTIONS = (
        smbc.NoEntryError, smbc.NotDirectoryError, smbc.PermissionError)
"""The exceptions to ignore during SMBC exploration. Note that this does not
exclude write errors or connection errors."""


# Only used by the SMB attribute override code
def _parse_int_flag_expr(
        etype: enum.IntFlag, expr: str,
        *,
        suppress_errors: bool = True) -> enum.IntFlag | None:
    """Given an IntFlag enumeration (with members A, B, C, ...) and a string
    expression of the form "A | C | F"..., computes the final value of that
    expression as a member of the enumeration.

    (This is essentially a very limited version of the eval() builtin, where
    the only available variables are the members of the enumeration and the
    only operator available is operator.or_.)

    >>> _parse_int_flag_expr(
    ...     enum.IntFlag("Type", names=["HIDDEN", "SYSTEM", "DIRECTORY"]),
    ...     "HIDDEN | DIRECTORY")
    ...
    <Type.HIDDEN|DIRECTORY: 5>

    If part of the expression refers to a non-existent member of the
    enumeration, a KeyError will be raised, unless the suppress_errors keyword
    argument is set to False."""

    available_attrs = etype.__members__
    tokens = []
    for k in expr.split("|"):
        try:
            tokens.append(available_attrs[k.strip()])
        except KeyError:
            if not suppress_errors:
                raise
    return reduce(or_, tokens, etype(0))


# Only used by the SMB attribute override code
def _trivial_read(ctx: smbc.Context, url: str) -> bytes | None:
    """Attempts to read and return the complete binary content of the specified
    file. Returns None in the event of anything resembling an error."""
    try:
        with _SMBCFile(ctx.open(url)) as fp:
            return fp.read()
    except Exception:
        # Normally this would be bad practice, but we only use this function
        # for testing
        return None


def inlang(lang, s):
    """Indicates whether or not every character in a given string @s can be
    found in the string @lang."""
    return all(c in lang for c in s)


# Third form from https://www.iana.org/assignments/uri-schemes/prov/smb
def make_smb_url(schema, unc, user, domain, password):
    server, path = unc.replace("\\", "/").lstrip('/').split('/', maxsplit=1)
    netloc = ""
    if user:
        if domain:
            netloc += domain + ";"
        netloc += user
        if password:
            netloc += ":" + password
        netloc += "@"
    netloc += server
    return urlunsplit((schema, netloc, quote(path), None, None))


def compute_domain(unc):
    """Attempts to extract a domain name from a UNC path. Returns None when the
    server name is a simple, unqualified name or an IP address."""
    server, path = unc.replace("\\", "/").lstrip('/').split('/', maxsplit=1)
    dot_count = server.count(".")
    # Check if we can extract an authentication domain from a fully-qualified
    # server name
    if (server.startswith('[')  # IPv6 address
            or dot_count == 0  # NetBIOS name
            or (inlang("0123456789.", server)
                and dot_count == 3)):  # IPv4 address
        return None
    else:
        # The machine name is the first component, and the rest is the domain
        # name
        _, remainder = server.split(".", maxsplit=1)
        return remainder


def make_full_windows_path(self):
    p = self.source.driveletter
    if p:
        # If you have a network drive //SERVER/DRIVE with the drive letter X,
        # sometimes you want to set up a scan for a specific subfolder that
        # nonetheless uses the drive letter X ("X:\Departments\Finance", for
        # example). Checking to see if the "drive letter" already contains a
        # colon makes this work properly
        if ":" not in p:
            p += ":"
    else:
        p = self.source.unc

    if p[-1] != "/":
        p += "/"
    return (p + self.relative_path).replace("/", "\\")


def make_presentation_url(self):
    # Note that this implementation returns a Windows-friendly URL to the
    # underlying file -- i.e., one that uses the file: scheme and not smb:
    url = "file:"
    # XXX: our testing seems to indicate that drive letter URLs don't work
    # properly; we'll leave the disabled logic here for now...
    if False and self.source.driveletter:
        # Wikipedia indicates that local filesystem paths are represented
        # with an empty hostname followed by an absolute path...
        url += "///{0}:".format(self.source.driveletter)
    else:
        # ... and that remote ones are indicated with a hostname in the
        # usual place. Luckily the UNC already starts with two forward
        # slashes, so we can just paste it in here
        url += self.source.unc
    if url[-1] != "/":
        url += "/"
    return url + self.relative_path


class SMBCSource(Source):
    type_label = "smbc"
    eq_properties = ("_unc", "_user", "_password", "_domain")

    allow_fake_attr: bool = False  # Not serialised, only useful for testing

    def __init__(
            self, unc: str,
            user: Optional[str] = None, password: Optional[str] = None,
            domain: Optional[str] = None, driveletter: Optional[str] = None,
            *,
            skip_super_hidden: bool = False,
            unc_is_home_root: bool = False):
        self._unc = unc.replace('\\', '/')
        self._user = user
        self._password = password
        self._domain = domain if domain is not None else compute_domain(unc)
        self._driveletter = (
                driveletter.replace('\\', '/') if driveletter else None)

        self._skip_super_hidden = skip_super_hidden
        self._unc_is_home_root = unc_is_home_root

    @property
    def unc(self):
        return self._unc

    @property
    def driveletter(self):
        return self._driveletter

    def __auth_handler(self, server, share, workgroup, username, password):
        """Returns the (workgroup, username, password) tuple expected of
        pysmbc authentication functions."""
        return (self._domain or "WORKGROUP",
                self._user or "GUEST", self._password or "")

    def _generate_state(self, sm):
        c = smbc.Context(auth_fn=self.__auth_handler)
        # Session cleanup for pysmbc is handled by the Python garbage
        # collector (groan...), so it's *critical* that no objects have a live
        # reference to this smbc.Context when this function completes
        yield (self._to_url(), c)

    def censor(self):
        return SMBCSource(
            self.unc,
            None,
            None,
            None,
            self.driveletter,
            skip_super_hidden=self._skip_super_hidden,
            unc_is_home_root=self._unc_is_home_root)

    def get_attrs(
            self, context: smbc.Context,
            here: smbc.FileInfo, url: str) -> smbc.Attribute:
        """Returns the (possibly overridden) Windows filesystem attributes of
        the file identified by the given URL and FileInfo."""
        logger.debug(
                "SMBCSource.get_attrs",
                url=url, attr=here.attrs)

        attr = here.attrs

        if self.allow_fake_attr:
            if raw_attr := _trivial_read(context, url + ".attr-override"):
                # Load this file's SMB attributes from the override file next
                # to it
                override_attr = _parse_int_flag_expr(
                        smbc.Attribute, raw_attr.decode())

                logger.info(
                        "SMBCSource.get_attrs overriding attributes",
                        url=url, original=attr, override=override_attr)
                return override_attr

        return attr

    @classmethod
    def is_skippable(  # noqa CCR001
            cls, name: str, attr: smbc.Attribute) -> bool:
        """Evaluates whether or not the given file is skippable: i.e., whether
        its attributes and other properties indicate that we should ignore it.

        (Note that the policy decision about whether or not to *actually* skip
        a skippable file is not implemented here.)"""
        logger.debug(
                "SMBCSource.is_skippable",
                name=name, attr=attr)

        if attr is not None:
            # If the smbc.Attribute.NORMAL bit is set *along with* other bits...
            if ((attr & smbc.Attribute.NORMAL
                    and attr != smbc.Attribute.NORMAL)
                    # ... or if a bit not permitted by the specification is
                    # set...
                    or attr & ~smbc.AttributeMask):
                # ... then something has gone very badly wrong
                logger.warning("incoherent attributes detected")
                if name.startswith("~"):
                    logger.info("skipping perhaps-hidden object")
                    return True

            # If this object is super-hidden -- that is, if it has the hidden
            # bit set plus either the system bit or the "~" character at the
            # start of its name -- then ignore it
            if (attr & smbc.Attribute.HIDDEN
                    and (attr & smbc.Attribute.SYSTEM
                         or name.startswith("~"))):
                logger.info("skipping super-hidden object")
                return True

        # Special-case the ~snapshot folder, which we should never scan
        # (XXX: revisit this once we know the Samba bug is fixed)
        if name == "~snapshot":
            logger.info("skipping snapshot directory")
            return True

        return False

    def _get_owner_for(self, url, context, dent_name):
        try:
            return DefaultRetrier(smbc.TimedOutError).run(
                    context.getxattr, url + "/" + dent_name, smbc.XATTR_OWNER)
        except MemoryError:
            # The path is using deprecated encoding, so we can't retrieve its
            # owner
            return None

    def handles(self, sm, *, rule=None):  # noqa: C901,CCR001
        base_url, context = sm.open(self)

        cutoff = find_cutoff(rule)

        def handle_fileinfo(  # noqa: C901,CCR001
                chain_here: list[smbc.FileInfo],
                owner_sid: str = None):
            *parents, here = chain_here

            if here.name in (".", ".."):
                return

            path_here: str = '/'.join([h.name for h in chain_here])
            url_here: str = base_url + "/" + path_here

            attrs = self.get_attrs(context, here, url_here)
            if self._skip_super_hidden and self.is_skippable(here.name, attrs):
                return

            hints = {
                "ctime": unparse_datetime(
                        ctime := here.ctime.astimezone(gettz())),
                "mtime": unparse_datetime(
                        mtime := here.mtime.astimezone(gettz()))
            }
            if owner_sid:
                hints["owner_sid"] = owner_sid
            handle_here: 'SMBCHandle' = SMBCHandle(
                    self, path_here, hints=hints)

            if attrs & smbc.Attribute.DIRECTORY:
                # On every filesystem we care about, creating or deleting
                # a/b/c.txt will update the modification timestamp on a/b/ but
                # not on a/, so we always need to explore the complete
                # directory hierarchy
                try:
                    obj = context.opendir(url_here)

                    while (fileinfo_raw := obj.readdirplus()):
                        fileinfo = smbc.FileInfo.from_raw_tuple(fileinfo_raw)
                        yield from handle_fileinfo(
                                chain_here + [fileinfo], owner_sid)
                except MemoryError as e:
                    # A memory error here means that the path is using
                    # deprecated encoding. Skip the path and keep going!
                    logger.warning(
                            "Skipping handle with memory error",
                            url_here=url_here)
                    yield (handle_here, e)
                    return
                except (ValueError, *IGNORABLE_SMBC_EXCEPTIONS):
                    pass
            else:
                # We assume anything not tagged as a directory is (scannable as
                # if it were) a normal file

                if cutoff:
                    # Pick whichever one is newer of the content and metadata
                    # change timestamps
                    updated_timestamp = max(ctime, mtime)
                    if updated_timestamp <= cutoff:
                        logger.debug(
                                "skipping file not updated after cutoff",
                                url_here=url_here,
                                cutoff=cutoff, updated=updated_timestamp)
                        return

                yield handle_here

        try:
            obj = context.opendir(base_url)
        except ValueError as ex:
            code = ex.args[0]
            if code == errno.EINVAL:
                raise UncontactableError(self._unc) from ex
            else:
                raise ex

        # Iterate over every folder lying directly under the provided UNC
        while (fileinfo_raw := obj.readdirplus()):
            fileinfo = smbc.FileInfo.from_raw_tuple(fileinfo_raw)
            if fileinfo.name in (".", "..",):
                continue

            # If we know that the provided UNC is a folder containing user home
            # folders, then compute the owner of each folder here.
            # handle_fileinfo can use this as a hint so SMBCResource doesn't
            # have to retrieve ownership metadata for individual files
            if self._unc_is_home_root:
                owner = self._get_owner_for(base_url, context, fileinfo.name)
            else:
                owner = None
            yield from handle_fileinfo([fileinfo], owner)

    # For our own purposes, we need to be able to make a "smb://" URL to give
    # to pysmbc. That URL doesn't need to contain authentication details,
    # though, as our __auth_handler function takes care of that
    def _to_url(self):
        return make_smb_url("smb", self._unc, None, None, None)

    def to_json_object(self):
        return super().to_json_object() | {
            "unc": self._unc,
            "user": self._user,
            "password": self._password,
            "domain": self._domain,
            "driveletter": self._driveletter,
            "skip_super_hidden": self._skip_super_hidden,
            "unc_is_home_root": self._unc_is_home_root
        }

    @staticmethod
    @Source.json_handler(type_label)
    def from_json_object(obj):
        return SMBCSource(
                obj["unc"], obj["user"], obj["password"], obj["domain"],
                obj["driveletter"],

                skip_super_hidden=obj.get("skip_super_hidden", False),
                unc_is_home_root=obj.get("unc_is_home_root", False))


class _SMBCFile(io.RawIOBase):
    def __init__(self, obj):
        self._file = obj

    def readinto(self, b):
        data = self._file.read(len(b))
        count = len(data)
        b[0:count] = data
        return count

    def write(self, bytes):
        raise TypeError("_SMBCFile is read-only")

    def seek(self, pos, whence=0):
        r = self._file.lseek(pos, whence)
        if r != -1:
            return r
        else:
            raise IOError("lseek failed")

    def tell(self):
        r = self._file.lseek(0, io.SEEK_CUR)
        if r != -1:
            return r
        else:
            raise IOError("lseek failed")

    def truncate(self, n=None):
        raise TypeError("_SMBCFile is read-only")

    def close(self):
        if self._file:
            try:
                # XXX: for now, we can't propagate this error back up, because
                # we *need* this reference to be removed in all circumstances.
                # See SMBCSource._generate_state for the gruesome details

                # r = self._file.close()
                # if r and r < 0:
                #     raise IOError("Failed to close {0}".format(self), r)

                self._file.close()
            finally:
                self._file = None

    def readable(self):
        return True

    def writable(self):
        return False

    def seekable(self):
        return True


class SMBCResource(FileResource):
    def __init__(self, handle, sm):
        super().__init__(handle, sm)
        self._mr = None

    def _generate_metadata(self):
        yield from super()._generate_metadata()
        yield "filesystem-owner-sid", self.get_owner_sid()

    def check(self) -> bool:
        try:
            _, context = self._get_cookie()
            context.stat(self._make_url())
            return True
        except smbc.NoEntryError:
            return False

    def _make_url(self):
        url, _ = self._get_cookie()
        return url + "/" + quote(self.handle.relative_path)

    def open_file(self):
        _, context = self._get_cookie()
        return DefaultRetrier(smbc.TimedOutError).run(
                context.open, self._make_url(), O_RDONLY)

    def get_xattr(self, attr):
        """Retrieves a SMB extended attribute for this file. (See the
        documentation for smbc.Context.getxattr for *most* of the supported
        attribute names.)"""
        _, context = self._get_cookie()
        return DefaultRetrier(smbc.TimedOutError).run(
                context.getxattr, self._make_url(), attr)

    def unpack_stat(self):
        if not self._mr:
            f = self.open_file()
            try:
                stat = stat_result(f.fstat())
                ts = datetime.fromtimestamp(stat.st_mtime)
                self._mr = make_values_navigable(
                        {k: getattr(stat, k) for k in stat_attributes} |
                        {OutputType.LastModified: ts})
            finally:
                f.close()
        return self._mr

    def get_size(self):
        return self.unpack_stat()["st_size"]

    def get_last_modified(self):
        hints = []
        for hn in ("ctime", "mtime",):
            if hv := self.handle.hint(hn):
                hints.append(parse_datetime(hv))
        return max(hints) if hints else self.unpack_stat().setdefault(
                OutputType.LastModified, super().get_last_modified())

    def get_owner_sid(self):
        """Returns the Windows security identifier of the owner of this file,
        which libsmbclient exposes as an extended attribute."""
        if (owner_sid := self.handle.hint("owner_sid")):
            return owner_sid
        return self.get_xattr(smbc.XATTR_OWNER)

    @contextmanager
    def make_stream(self):
        with _SMBCFile(self.open_file()) as fp:
            yield fp

    DOWNLOAD_CHUNK_SIZE = 1024 * 512


@Handle.stock_json_handler("smbc")
class SMBCHandle(Handle):
    type_label = "smbc"
    resource_type = SMBCResource

    @property
    def presentation_name(self):
        return PureWindowsPath(make_full_windows_path(self)).name

    @property
    def presentation_place(self):
        return str(PureWindowsPath(make_full_windows_path(self)).parent)

    @property
    def presentation_url(self):
        return make_presentation_url(self)

    @property
    def container_url(self):
        return self.presentation_url.rsplit('/', maxsplit=1)[0]

    def __str__(self):
        return make_full_windows_path(self)

    @property
    def sort_key(self):
        return str(self).removesuffix("\\")
