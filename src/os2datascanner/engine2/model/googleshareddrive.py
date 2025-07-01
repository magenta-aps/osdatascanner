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


class GoogleSharedDrivesSource(Source):
    """Implements Google Drive API using a service account.
    The organization must create a project, a service account, enable G Suite Domain-wide Delegation
     for the service account, download the credentials in .json format
     and enable the Google Drive API for the account to use this feature.

     Guidance to complete the above can be found at:
      https://support.google.com/a/answer/7378726?hl=en
    """

    type_label = "googleshareddrive"

    eq_properties = ("_google_admin_account",)

    def __init__(self, google_api_grant, google_admin_account):
        self.google_api_grant = google_api_grant
        self._google_admin_account = google_admin_account

    def _generate_state(self, source_manager):
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        credentials = service_account.Credentials.from_service_account_info(
            self.google_api_grant,
            scopes=SCOPES).with_subject(self._google_admin_account)

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
                cutoff = essential_rule.after

        query = self._generate_query(cutoff)

        while True:
            drives = service.drives().list(
                                         fields='nextPageToken, drives(id, name)',
                                         useDomainAdminAccess=True,
                                         pageToken=page_token).execute()
            for drive in drives.get('drives', []):
                yield from self.process_drive(drive, service, query)

            page_token = drives.get('nextPageToken', None)
            if page_token is None:
                break

    def process_drive(self, drive, service, query):
        page_token = None
        while True:
            files = service.files().list(
                q=query,
                fields='nextPageToken, files(id, name, mimeType, parents)',
                driveId=drive.get('id'),
                # supportsAllDrives and includeItemsFromAllDrives are needed despite the
                # api documentation claiming it was deprecated in June of 2020 :shrug:
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                corpora='drive',
                pageToken=page_token
            ).execute()
            for file in files.get('files'):
                location = self.get_location(
                    file.get('parents')[0], service, drive.get('name'))
                yield GoogleSharedDriveHandle(
                    self,
                    file.get('id'),
                    name=file.get('name'),
                    location=location
                )
            page_token = files.get('nextPageToken', None)
            if page_token is None:
                break

    # Censoring service account file info and user email.
    def censor(self):
        return GoogleSharedDrivesSource(None, self._google_admin_account)

    def get_location(self, parent_id, service, drive_name):
        """
        Finds the path for a google drive file by traversing the parents.
        """
        path = ""
        # Files _can_ technically (rarely) have multiple parent folders but for the purpose of
        # building a path to the file exploring the first parent will do.
        parent = service.files().get(fileId=parent_id, fields='id, name, parents',
                                     supportsAllDrives=True).execute()
        path = parent.get('name') + '/' + path
        while parent.get('parents'):
            parent_id = parent.get('parents')[0]
            parent = service.files().get(fileId=parent_id, fields='id, name, parents',
                                         supportsAllDrives=True).execute()
            parent_name = parent.get('name')
            # The api has trouble returning the correct name for shared drives
            # So we check to see if it uses the default name and replace it
            if parent_name == 'Drive':
                path = drive_name + '/' + path
            else:
                path = parent_name + '/' + path
        return path

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            google_api_grant=self.google_api_grant,
            google_admin_account=self._google_admin_account,
        )

    @staticmethod
    @Source.json_handler(type_label)
    def from_json_object(obj):
        return GoogleSharedDrivesSource(obj["google_api_grant"], obj["google_admin_account"])


class GoogleSharedDriveResource(FileResource):
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
        yield "email-account", self.metadata.get("lastModifyingUser").get("emailAddress")
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
                supportsAllDrives=True,
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
                    supportsAllDrives=True,
                    fields='name, size, quotaBytesUsed, mimeType, lastModifyingUser').execute()
        return self._metadata

    def get_size(self):
        return self.metadata.get('size', self.metadata.get('quotaBytesUsed'))


class GoogleSharedDriveHandle(Handle):
    type_label = "googleshareddrive"
    resource_type = GoogleSharedDriveResource

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
        return self._location + self._name

    def to_json_object(self):
        return dict(**super().to_json_object(), name=self._name, location=self._location)

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        return GoogleSharedDriveHandle(Source.from_json_object(obj["source"]),
                                       obj["path"], obj.get('name'), obj.get('location'))
