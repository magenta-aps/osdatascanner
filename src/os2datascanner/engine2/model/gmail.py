from contextlib import contextmanager
from io import BytesIO

from .core import Source, Handle, FileResource
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

import base64


class GmailSource(Source):
    """Implements Gmail API using a service account.
       The organization must create a project, a service account,
        enable G Suite Domain-wide Delegation for the service account,
        download the credentials in .json format
        and enable the Gmail API and scope for the account to use this feature.

        Guidance to complete the above can be found at:
        https://support.google.com/a/answer/7378726?hl=en
        List of users in organization downloadable by admin from: https://admin.google.com/ac/users
        Add scope https://www.googleapis.com/auth/gmail.readonly to:
        https://admin.google.com/ac/owl/domainwidedelegation
    """

    type_label = "gmail"

    eq_properties = ("_user_email_gmail",)

    def __init__(self, google_api_grant, user_email_gmail, scan_attachments):
        self.google_api_grant = google_api_grant
        self._user_email_gmail = user_email_gmail
        self.scan_attachments = scan_attachments

    def _generate_state(self, source_manager):
        SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        credentials = service_account.Credentials.from_service_account_info(
            self.google_api_grant,
            scopes=SCOPES).with_subject(
                self._user_email_gmail
            )
        service = build(serviceName='gmail', version='v1', credentials=credentials)
        yield service

    def handles(self, sm):
        service = sm.open(self)

        # Call the Gmail API to retrieve all labels
        labels = service.users().labels().list(
            userId=self._user_email_gmail).execute()

        # Filter 'DRAFT' and 'TRASH' from the labels
        label_ids = [label['id'] for label in labels["labels"]
                     if label['id'] not in ('TRASH', 'DRAFT')]

        for label_id in label_ids:
            # Call the Gmail API to fetch INBOX
            results = service.users().messages().list(userId=self._user_email_gmail,
                                                      labelIds=[label_id], maxResults=500).execute()

            messages = []
            if 'messages' in results:
                messages.extend(results['messages'])
                while 'nextPageToken' in results:
                    page_token = results['nextPageToken']
                    results = service.users().messages().list(userId=self._user_email_gmail,
                                                              labelIds=[label_id], maxResults=500,
                                                              pageToken=page_token).execute()
                    messages.extend(results['messages'])

                for message in messages:
                    # Fetch info on specific email
                    msgId = message.get("id")
                    email = service.users().messages().get(userId=self._user_email_gmail,
                                                           id=msgId).execute()
                    headers = email["payload"]["headers"]
                    subject = [i['value'] for i in headers if i["name"] == "Subject"][0]
                    # Id of given email is set to be path.
                    yield GmailHandle(self, msgId, mail_subject=subject)

    # Censoring service account details
    def censor(self):
        return GmailSource(None, self._user_email_gmail, self.scan_attachments)

    def to_json_object(self):
        return dict(
            **super().to_json_object(),
            google_api_grant=self.google_api_grant,
            user_email=self._user_email_gmail,
            scan_attachments=self.scan_attachments
        )

    @staticmethod
    @Source.json_handler(type_label)
    def from_json_object(obj):
        return GmailSource(obj["google_api_grant"], obj["user_email"], obj.get("scan_attachments"))


class GmailResource(FileResource):
    def __init__(self, handle, sm):
        super().__init__(handle, sm)
        self._metadata = None

    def _generate_metadata(self):
        yield "email-account", self.handle.source._user_email_gmail
        yield from super()._generate_metadata()

    def check(self) -> bool:
        try:
            self.metadata
            return True
        except HttpError as e:
            if e.resp.status in (404, 410,):
                return False
            raise

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = self._get_cookie().users().messages().get(
                userId=self.handle.source._user_email_gmail,
                id=self.handle.relative_path, format="metadata").execute()
        return self._metadata

    @contextmanager
    def make_stream(self):
        response = self._get_cookie().users().messages().get(
            userId=self.handle.source._user_email_gmail,
            id=self.handle.relative_path,
            format="raw").execute()
        response_bts = base64.urlsafe_b64decode(response['raw'].encode('ASCII'))
        with BytesIO(response_bts) as fp:
            yield fp

    # Estimated size in bytes of the message.
    # Is this used anywhere?
    def get_size(self):
        return self.metadata.get('sizeEstimate')

    def get_last_modified(self):
        return super().get_last_modified()

    def compute_type(self):
        return "message/rfc822"


class GmailHandle(Handle):
    type_label = "gmail"
    resource_type = GmailResource

    def __init__(self, source, relpath, mail_subject):
        super().__init__(source, relpath)
        self._mail_subject = mail_subject

    @property
    def presentation_name(self):
        return f"\"{self._mail_subject}\""

    @property
    def scan_attachments(self):
        return self.source.scan_attachments

    @property
    def presentation_place(self):
        return f"account {self.source._user_email_gmail}"

    @property
    def presentation_url(self):
        return "https://mail.google.com/mail/#inbox/{0}".format(self.relative_path)

    @property
    def sort_key(self):
        """ Returns a string to sort by formatted as:
             DOMAIN/ACCOUNT/MAIL_SUBJECT"""
        # We should probably look towards EWS implementation and see if you get/can get folder
        # the mail resides in and add this.
        account, domain = self.source._user_email_gmail.split("@", 1)
        return f'{domain}/{account}/{self._mail_subject}'

    def guess_type(self):
        return "message/rfc822"

    def to_json_object(self):
        return dict(**super().to_json_object(), **{
            "mail_subject": self._mail_subject
        })

    @staticmethod
    @Handle.json_handler(type_label)
    def from_json_object(obj):
        return GmailHandle(
            Source.from_json_object(obj["source"]),
            obj["path"], obj["mail_subject"])
