import io
from os import stat_result, O_RDONLY
import enum
import logging
import smbc
from typing import Optional
from urllib.parse import quote
from pathlib import PureWindowsPath
from datetime import datetime
import operator
import warnings
from functools import reduce
from contextlib import contextmanager

from ..utilities.backoff import DefaultRetrier
from ..conversions.types import OutputType
from ..conversions.utilities.navigable import make_values_navigable
from .smb import (
    make_smb_url, compute_domain,
    make_full_windows_path, make_presentation_url)
from .core import Source, Handle, FileResource
from .core.errors import UncontactableError
from .file import stat_attributes

import errno

logger = logging.getLogger(__name__)

XATTR_DOS_ATTRIBUTES = "system.dos_attr.mode"
"""The attribute name for a file's mode flags. (This is not documented in
pysmbc, but it is in the underlying libsmbclient library.)"""


IGNORABLE_SMBC_EXCEPTIONS = (
        smbc.NoEntryError, smbc.NotDirectoryError, smbc.PermissionError)
"""The exceptions to ignore during SMBC exploration. Note that this does not
exclude write errors or connection errors."""


class Mode(enum.IntFlag):
    """A convenience enumeration for manipulating SMB file mode flags."""
    # description of flags mapping
    # https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-smb/65e0c225-5925-44b0-8104-6b91339c709f
    NONE = 0x0
    READ_ONLY = 0x01
    HIDDEN = 0x02
    SYSTEM = 0x04
    # Windows defines VOLUME_ID = 0x08, but CIFS/SMB doesn't
    DIRECTORY = 0x10
    ARCHIVE = 0x20
    # Windows defines DEVICE = 0x40, but CIFS/SMB doesn't
    NORMAL = 0x80
    TEMPORARY = 0x100
    SPARSE = 0x200
    REPARSE_POINT = 0x400
    COMPRESSED = 0x800
    OFFLINE = 0x1000
    NONINDEXED = 0x2000
    ENCRYPTED = 0x4000

    @staticmethod
    def for_url(context: smbc.Context, url: str) -> Optional['Mode']:
        """Attempts to convert the mode flags retrieved from the given smb://
        URL to a Mode."""
        try:
            mode_ = context.getxattr(url, XATTR_DOS_ATTRIBUTES)
            logger.debug(f"mode flags for {url}: {mode_}")
            return Mode(int(mode_, 16))
        except (ValueError, *IGNORABLE_SMBC_EXCEPTIONS, MemoryError) as exc:
            logger.info(f"Exception thrown: {exc}\n for {url}\n"
                        f"Ignoring and continuing")
            return None


ModeMask = reduce(operator.or_, Mode, Mode.NONE)


class SMBCSource(Source):
    type_label = "smbc"
    eq_properties = ("_unc", "_user", "_password", "_domain")

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
        return SMBCSource(self.unc, None, None, None, self.driveletter)

    @classmethod
    def is_skippable(cls, context, url, path, name):
        """Evaluates whether or not the given file is skippable: i.e., whether
        its attributes and other properties indicate that we should ignore it.

        (Note that the policy decision about whether or not to *actually* skip
        a skippable file is not implemented here.)"""
        mode = Mode.for_url(context, url)

        if mode is not None:
            # If the Mode.NORMAL bit is set *along with* other bits...
            if ((mode & Mode.NORMAL
                    and mode != Mode.NORMAL)
                    # ... or if a bit not permitted by the specification is
                    # set...
                    or mode & ~ModeMask):
                # ... then something has gone very badly wrong
                warnings.warn(
                        "incoherent mode flags detected"
                        " (Samba bug #14101?)")
                if name.startswith("~"):
                    logger.info("skipping perhaps-hidden object {path}")
                    return True

            # If this object is super-hidden -- that is, if it has the hidden
            # bit set plus either the system bit or the "~" character at the
            # start of its name -- then ignore it
            if (mode & Mode.HIDDEN
                    and (mode & Mode.SYSTEM or name.startswith("~"))):
                logger.info(f"skipping super-hidden object {path}")
                return True

        # Special-case the ~snapshot folder, which we should never scan
        # (XXX: revisit this once we know the Samba bug is fixed)
        if name == "~snapshot":
            logger.info(f"skipping snapshot directory {path}")
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

    def handles(self, sm):  # noqa: C901,E501,CCR001
        url, context = sm.open(self)

        def handle_dirent(parents, entity, owner_sid: str = None):
            name = entity.name

            here = parents + [entity]
            path = '/'.join([h.name for h in here])
            url_here = url + "/" + path

            if (self._skip_super_hidden
                    and SMBCSource.is_skippable(
                            context, url_here, path, name)):
                return

            hints = {}
            if owner_sid:
                hints["owner_sid"] = owner_sid

            handle_here = SMBCHandle(self, path, hints=hints)
            if entity.smbc_type == smbc.DIR and name not in (".", ".."):
                try:
                    try:
                        obj = context.opendir(url_here)
                    except MemoryError as e:
                        # A memory error here means that the path is using
                        # deprecated encoding. Skip the path and keep going!
                        logger.warning(
                            f"Skipping handle with memory error at {url_here}")
                        yield (handle_here, e)
                        return
                    for dent in obj.getdents():
                        yield from handle_dirent(here, dent, owner_sid)
                except (ValueError, *IGNORABLE_SMBC_EXCEPTIONS):
                    pass
            elif entity.smbc_type == smbc.FILE:
                yield handle_here

        try:
            obj = context.opendir(url)
        except ValueError as ex:
            code = ex.args[0]
            if code == errno.EINVAL:
                raise UncontactableError(self._unc) from ex
            else:
                raise ex

        # Iterate over every folder lying directly under the provided UNC
        for dent in obj.getdents():
            if dent.name not in (".", "..",):
                # If we know that the provided UNC is a folder containing user
                # home folders, then compute the owner of each folder here.
                # handle_dirent can use this as a hint so SMBCResource doesn't
                # have to retrieve ownership metadata for individual files
                if self._unc_is_home_root:
                    owner = self._get_owner_for(url, context, dent.name)
                else:
                    owner = None
                yield from handle_dirent([], dent, owner)

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
                # On NTFS (Windows), if a file is copied within the same
                # volume, the new file inherits the Modified Datetime (MTIME)
                # from the original, but the Changed Datetime (CTIME)
                # IS updated. CTIME in NTFS represents file creation,
                # and thus a file is also "created" when copied.
                mt = datetime.fromtimestamp(stat.st_mtime)
                ct = datetime.fromtimestamp(stat.st_ctime)

                # So we simply choose the most recent datetime among
                # CTIME and MTIME.
                ts = max(ct, mt)
                self._mr = make_values_navigable(
                        {k: getattr(stat, k) for k in stat_attributes} |
                        {OutputType.LastModified: ts})
            finally:
                f.close()
        return self._mr

    def get_size(self):
        return self.unpack_stat()["st_size"]

    def get_last_modified(self):
        return self.unpack_stat().setdefault(OutputType.LastModified,
                                             super().get_last_modified())

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

    def __str__(self):
        return make_full_windows_path(self)

    @property
    def sort_key(self):
        return self.presentation.removesuffix("\\")

    def censor(self):
        return SMBCHandle(self.source.censor(), self.relative_path)
