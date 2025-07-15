import structlog
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
from os2datascanner.engine2.model.utilities.utilities import GoogleSource

logger = structlog.get_logger("engine2")


class GoogleSharedDriveSource(GoogleSource):
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
        super().__init__(google_api_grant)
        self._google_admin_account = google_admin_account
        self.parent_cache = {}

    def _generate_state(self, source_manager):
        SCOPES = ['https://www.googleapis.com/auth/drive']
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

        cutoff = None
        for essential_rule in compute_mss(rule):
            if essential_rule.type_label == "last-modified":
                cutoff = essential_rule.after

        query = self._generate_query(cutoff)

        drives = self.paginated_get(
            service=service.drives(),
            collection_name='drives',
            fields='drives(id,name)',
            useDomainAdminAccess=True)

        for drive in drives:
            yield from self.process_drive(drive, service, query)

    def process_drive(self, drive, service, query):
        # Retry a few times in case the permission change from grant_read_permissions
        # takes a moment to update
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                files = self.paginated_get(
                                    service=service.files(),
                                    collection_name='files',
                                    q=query,
                                    fields='nextPageToken, files(id, name, mimeType, parents)',
                                    driveId=drive.get('id'),
                                    supportsAllDrives=True,
                                    includeItemsFromAllDrives=True,
                                    corpora='drive'
                )

                for file in files:
                    location = self.get_location(file.get('parents')[0], service, drive)
                    yield GoogleSharedDriveHandle(
                        self,
                        file.get('id'),
                        name=file.get('name'),
                        location=location
                    )
                # Time to stop
                break

            except Exception as e:
                # Handle cases where provided admin account doesn't
                # have permission to read files in shared drive
                if "teamDriveMembershipRequired" in str(e):
                    logger.info("Insufficient permissions to access this drive "
                                "(, attempting to gain permission"
                                f"...{retry_count + 1}/{max_retries})")
                    self.grant_read_permissions(drive, service)
                    retry_count += 1
                if retry_count >= max_retries:
                    logger.error("Max retries reached, unable to scan this drive.")
                    break
                else:
                    raise

    def grant_read_permissions(self, drive, service):
        """Attempts to grant admin permission to read a drive's files"""
        new_permission = {
            'role': 'reader',
            'type': 'user',
            'emailAddress': self._google_admin_account
        }
        service.permissions().create(
            fileId=drive.get('id'),
            body=new_permission,
            supportsAllDrives=True,
            useDomainAdminAccess=True
        ).execute()

    def get_location(self, parent_id, service, drive):
        """
        Finds the path for a google drive file with caching to reduce API calls.
        """
        path_parts = []
        current_id = parent_id
        # Track visited IDs to prevent a bug that leads to an infinite loop
        visited_ids = set()

        while current_id:
            # Check for circular references
            if current_id in visited_ids:
                break

            visited_ids.add(current_id)

            # Check cache first
            if current_id in self.parent_cache:
                parent_info = self.parent_cache[current_id]
            else:
                parent_info = service.files().get(
                    fileId=current_id,
                    fields='id, name, parents',
                    supportsAllDrives=True
                ).execute()
                self.parent_cache[current_id] = parent_info

            parent_name = parent_info.get('name')
            if not parent_name:
                break

            # Check if we've reached the root and replace with correct name
            parent_parents = parent_info.get('parents')
            if not parent_parents:
                if parent_name in ['Drive']:
                    parent_name = drive.get('name', 'Drive')
                path_parts.append(parent_name)
                break

            path_parts.append(parent_name)
            current_id = parent_parents[0]

        # Reverse to get correct order and join
        path_parts.reverse()
        return '/'.join(path_parts) if path_parts else drive.get('name', 'Drive')

    # Censoring service account file info and user email.
    def censor(self):
        return GoogleSharedDriveSource(None, self._google_admin_account)

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            google_api_grant=self.google_api_grant,
            google_admin_account=self._google_admin_account,
        )

    @staticmethod
    @Source.json_handler(type_label)
    def from_json_object(obj):
        return GoogleSharedDriveSource(obj["google_api_grant"], obj["google_admin_account"])


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
        if self._location:
            return self._location + '/' + self._name
        else:
            return self._name

    def to_json_object(self):
        return dict(**super().to_json_object(), name=self._name, location=self._location)

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        return GoogleSharedDriveHandle(Source.from_json_object(obj["source"]),
                                       obj["path"], obj.get('name'), obj.get('location'))
