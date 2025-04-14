from contextlib import contextmanager
from datetime import datetime, timezone
from io import BytesIO
from ..rules.rule import Rule
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from .core import Source, Handle, FileResource
from os2datascanner.engine2.rules.utilities.analysis import compute_mss


class GoogleDriveSource(Source):
    """Implements Google Drive API using a service account.
    The organization must create a project, a service account, enable G Suite Domain-wide Delegation
     for the service account, download the credentials in .json format
     and enable the Google Drive API for the account to use this feature.

     Guidance to complete the above can be found at:
      https://support.google.com/a/answer/7378726?hl=en
    """

    type_label = "googledrive"

    eq_properties = ("_user_email",)

    def __init__(self, google_api_grant, user_email):
        self.google_api_grant = google_api_grant
        self._user_email = user_email

    def _generate_state(self, source_manager):
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        credentials = service_account.Credentials.from_service_account_info(
            self.google_api_grant,
            scopes=SCOPES).with_subject(self._user_email)

        service = build(serviceName='drive', version='v3', credentials=credentials)
        yield service

        # The Google Drive V3 API query operators can be found at:
        # https://developers.google.com/workspace/drive/api/guides/search-files
    def _generate_query(
            self,
            cutoff: datetime | None = None):
        # Don't get folders or trashed files
        query = "mimeType != 'application/vnd.google-apps.folder' and trashed = false"

        if cutoff:
            ts = cutoff.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
            query += f" and modifiedTime > '{ts}'"

        return query

    def handles(self, sm, rule: Rule | None = None):
        service = sm.open(self)
        page_token = None

        cutoff = None
        for essential_rule in compute_mss(rule):
            if essential_rule.type_label == "last-modified":
                after = essential_rule.after
                cutoff = (after if after is not None else datetime.min)

        query = self._generate_query(cutoff)

        while True:
            files = service.files().list(q=query,
                                         fields='nextPageToken, files(id, name, mimeType, parents)',
                                         pageToken=page_token).execute()
            for file in files.get('files', []):
                location = self.get_location(file.get('parents')[0], service)
                yield GoogleDriveHandle(self, file.get('id'),
                                        name=file.get('name'),
                                        location=location)
            page_token = files.get('nextPageToken', None)
            if page_token is None:
                break

    # Censoring service account file info and user email.
    def censor(self):
        return GoogleDriveSource(None, self._user_email)

    def get_location(self, parent_id, service):
        """
        Finds the path for a google drive file by traversing the parents.
        """
        path = ""
        # Files _can_ technically (rarely) have multiple parent folders but for the purpose of
        # building a path to the file exploring the first parent will do.
        parent = service.files().get(fileId=parent_id, fields='id, name, parents').execute()
        path = parent.get('name') + '/' + path
        while parent.get('parents'):
            parent_id = parent.get('parents')[0]
            parent = service.files().get(fileId=parent_id, fields='id, name, parents').execute()
            path = parent.get('name') + '/' + path
        return path

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            google_api_grant=self.google_api_grant,
            user_email=self._user_email,
        )

    @staticmethod
    @Source.json_handler(type_label)
    def from_json_object(obj):
        return GoogleDriveSource(obj["google_api_grant"], obj["user_email"])


class GoogleDriveResource(FileResource):
    def __init__(self, handle, sm):
        super().__init__(handle, sm)
        self._metadata = None

    def check(self) -> bool:
        try:
            self.metadata
            return True
        except HttpError as e:
            if e.resp.status in (404, 410,):
                return False
            raise

    def _generate_metadata(self):
        # This will only be the right email for personal drives and not shared drives.
        # Todo: Implement logic to handle shared drives
        yield "email-account", self.handle.source._user_email
        yield from super()._generate_metadata()

    def compute_type(self):
        ct = None
        if 'vnd.google-apps' in self.metadata.get('mimeType'):
            # Google-type files are exported as pdf
            ct = 'application/pdf'
        else:
            ct = self.metadata.get('mimeType', 'application/octet-stream')
        return ct

    @contextmanager
    def open_file(self):
        service = self._get_cookie()
        # Export and download Google-type files to pdf
        # Exported file can't exceed 10MB
        if 'vnd.google-apps' in self.metadata.get('mimeType'):
            request = service.files().export_media(
                fileId=self.handle.relative_path,
                fields='files(id, name)',
                mimeType='application/pdf')
        # Download files where no export needed
        else:
            request = service.files().get_media(
                fileId=self.handle.relative_path,
                fields='files(id, name)')

        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        # Seek(0) points back to the beginning of the file as it appears to not do this by it self.
        fh.seek(0)
        yield fh

    @contextmanager
    def make_stream(self):
        with self.open_file() as res:
            yield res

    @property
    def metadata(self):
        if not self._metadata:
            self._metadata = self._get_cookie().files().get(
                    fileId=self.handle.relative_path,
                    fields='name, size, quotaBytesUsed, mimeType').execute()
        return self._metadata

    def get_size(self):
        return self.metadata.get('size', self.metadata.get('quotaBytesUsed'))


class GoogleDriveHandle(Handle):
    type_label = "googledrive"
    resource_type = GoogleDriveResource

    def __init__(self, source, relpath, name, location):
        super().__init__(source, relpath)
        self._name = name
        self._location = location

    def __str__(self):
        if self._location:
            return self._location + self._name
        return self._name

    @property
    def presentation_name(self):
        return self._name

    @property
    def presentation_place(self):
        return self._location

    @property
    def presentation_url(self):
        return f"https://drive.google.com/file/d/{self.relative_path}/view"

    @property
    def sort_key(self):
        """Returns a string to sort by formatted as:
        DOMAIN/ACCOUNT/PATH/FILE_NAME"""
        account, domain = self.source._user_email.split("@", 1)
        return f'{domain}/{account}/{self.relative_path}/{self._name}'

    def to_json_object(self):
        return dict(**super().to_json_object(), name=self._name, location=self._location)

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        return GoogleDriveHandle(Source.from_json_object(obj["source"]),
                                 obj["path"], obj.get('name'), obj.get('location'))
