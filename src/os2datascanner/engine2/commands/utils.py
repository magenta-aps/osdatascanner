'''Utilities for the demo application'''
from base64 import b64encode
from urllib.parse import quote, unquote, parse_qs, urlsplit, urlunsplit

from os2datascanner.engine2.model.core.errors import UnknownSchemeError
from os2datascanner.engine2.model.smb import SMBSource, make_smb_url
from os2datascanner.engine2.model.smbc import SMBCSource
from os2datascanner.engine2.model.dropbox import DropboxSource
from os2datascanner.engine2.model.data import DataSource, unpack_data_url
from os2datascanner.engine2.model.file import FilesystemSource
from os2datascanner.engine2.model.http import WebSource


class DemoSourceUtility:
    '''
    Utility for Sources that extends the sources capabilities
    just for use in the demo app.
    '''

    @staticmethod
    def from_url(url):
        '''
        Takes a URL and a Source Type and converts the URL
        to a Source of the type provided if supported.
        The Source is then wrapped as a DemoSourceUtility
        and returned as such.

        Supported Types:
        - SMBCSource
          smbc://[[domain;]user[:password]@]hostname/path/to/share
        - SMBSource
          as above
        - DropboxSource
          dropbox://api_token
        - DataSource
          data:mime/type[;base64],content
        - FilesystemSource
          file:///local/filesystem/path
        - WebSource
          http[s]://[user[:password]@]hostname/path/to/subpage
        - SBSYS
          sbsys://[user:password@]hostname[:port]/database_name
        '''

        match urlsplit(url):
            case ("smb" | "smbc" as scheme, netloc, path, _, _):
                mtc = SMBSource.netloc_regex.match(netloc)
                if mtc:
                    if scheme == "smb":
                        return SMBSource("//" + mtc.group("unc") + unquote(path),
                                         mtc.group("username"), mtc.group("password"),
                                         mtc.group("domain"))
                    if scheme == "smbc":
                        return SMBCSource("//" + mtc.group("unc") + unquote(path),
                                          mtc.group("username"), mtc.group("password"),
                                          mtc.group("domain"))

            case ("dropbox", token, _, _, _):
                return DropboxSource(token=token)

            case ("data", _, _, _, _):
                mime, content = unpack_data_url(url)
                return DataSource(content=content, mime=mime)

            case ("file", netloc, path, _, _):
                assert not netloc
                return FilesystemSource(unquote(path) if path else None)

            case ("http" | "https", _, _, _, _):
                return WebSource(url, extended_hints=True)

            case ("sbsys", server, database, query, _):
                from os2datascanner.engine2.model._staging import sbsysdb

                query_dict = parse_qs(query)

                match query_dict.get("reflect"):
                    case [*tables]:
                        rt = tuple(tables)
                    case _:
                        rt = None
                match query_dict.get("baselink"):
                    case [str() as link]:
                        bw = link
                    case _:
                        bw = None

                user = password = None
                if "@" in server:
                    auth, server = server.split("@", maxsplit=1)
                    user, password = auth.split(":", maxsplit=1)

                port = 1433
                if ":" in server:
                    server, port, = server.split(":", maxsplit=1)
                    port = int(port)

                return sbsysdb.SBSYSDBSource(
                        server, port, database.lstrip("/"), user, password,
                        reflect_tables=rt, base_weblink=bw)

            case _:
                raise UnknownSchemeError

    @staticmethod
    def to_url(src) -> str:
        '''
        Converts the wrapped Source to a URL.

        Supported Types:
        - SMBCSource
        - SMBSource
        - DropboxSource
        - DataSource
        - FilesystemSource
        - WebSource
        '''
        src_type = type(src)

        if src_type is SMBCSource:
            return make_smb_url(
                "smbc", src._unc, src._user, src._domain, src._password)

        if src_type is SMBSource:
            return make_smb_url(
                "smb", src._unc, src._user, src._domain, src._password)

        if src_type is DropboxSource:
            return f"dropbox://{src._token}"

        if src_type is DataSource:
            content = b64encode(src._content).decode(encoding='ascii')
            return f"data:{src._mime};base64,{content}"

        if src_type is FilesystemSource:
            return urlunsplit(('file', '', quote(str(src.path)), None, None))

        if src_type is WebSource:
            return src._url

        return None
