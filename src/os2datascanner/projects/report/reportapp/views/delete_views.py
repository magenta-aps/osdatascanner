# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

from collections.abc import Callable
from django.contrib import messages
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView

from .base_views import HTMXEndpointView, BaseMassView
from .utilities.ews_utilities import try_ews_delete
from .utilities.google_utilities import try_gmail_delete, try_gdrive_delete
from .utilities.smb_utilities import try_smb_delete_1
from .utilities.msgraph_utilities import try_msgraph_mail_delete, try_msgraph_file_delete

DeleteFn = Callable[[HttpRequest, list[int]], tuple[bool, str]]


class BaseDeleteView(HTMXEndpointView, DetailView):
    """Base class for single-report remote deletion views.

    Subclasses must set delete_fn to a callable with the signature
    (request, pks: list[int]) -> (bool, str).
    """
    delete_fn: DeleteFn | None = None

    def post(self, request, *args, **kwargs):
        if self.delete_fn is None:
            raise NotImplementedError("No delete_fn found. Did you forget to set it?")

        response = super().post(request, *args, **kwargs)
        report = self.get_object()
        deleted, problem = self.delete_fn(request, [report.pk])
        if not deleted:
            messages.add_message(
                request,
                messages.WARNING,
                _("Failed to delete {pn}: {e}").format(
                    pn=report.matches.handle.presentation_name, e=problem),
                extra_tags="manual_close")
        return response


class BaseMassDeleteView(HTMXEndpointView, BaseMassView):
    """Base class for multi-report remote deletion views.

    Subclasses must set delete_fn to a callable with the signature
    (request, pks: list[int]) -> (bool, str).
    """
    delete_fn: DeleteFn | None = None

    def post(self, request, *args, **kwargs):
        if self.delete_fn is None:
            raise NotImplementedError("No delete_fn found. Did you forget to set it?")

        response = super().post(request, *args, **kwargs)
        deleted, problem = self.delete_fn(
            request, list(self.get_queryset().values_list("pk", flat=True)))
        if not deleted:
            messages.add_message(
                request,
                messages.WARNING,
                _("Failed to delete some resources: {e}").format(e=problem),
                extra_tags="manual_close")
        return response


class DeleteMailView(BaseDeleteView):
    """View for deleting an MSGraph email."""
    delete_fn = staticmethod(try_msgraph_mail_delete)


class MassDeleteMailView(BaseMassDeleteView):
    """View for deleting multiple MSGraph emails."""
    delete_fn = staticmethod(try_msgraph_mail_delete)


class DeleteFileView(BaseDeleteView):
    """View for deleting an MSGraph file."""
    delete_fn = staticmethod(try_msgraph_file_delete)


class MassDeleteFileView(BaseMassDeleteView):
    """View for deleting multiple MSGraph files."""
    delete_fn = staticmethod(try_msgraph_file_delete)


class DeleteSMBFileView(BaseDeleteView):
    """View for deleting a file on an SMB share."""
    delete_fn = staticmethod(try_smb_delete_1)


class MassDeleteSMBFileView(BaseMassDeleteView):
    """View for deleting multiple files on an SMB share."""
    delete_fn = staticmethod(try_smb_delete_1)


class DeleteEWSMailView(BaseDeleteView):
    """View for deleting an EWS mail."""
    delete_fn = staticmethod(try_ews_delete)


class MassDeleteEWSMailView(BaseMassDeleteView):
    """View for deleting multiple EWS mails."""
    delete_fn = staticmethod(try_ews_delete)


class DeleteGmailView(BaseDeleteView):
    """View for deleting a Gmail message."""
    delete_fn = staticmethod(try_gmail_delete)


class MassDeleteGmailView(BaseMassDeleteView):
    """View for deleting multiple Gmail messages."""
    delete_fn = staticmethod(try_gmail_delete)


class DeleteGoogleDriveView(BaseDeleteView):
    """View for deleting a Google Drive file."""
    delete_fn = staticmethod(try_gdrive_delete)


class MassDeleteGoogleDriveView(BaseMassDeleteView):
    """View for deleting multiple Google Drive files."""
    delete_fn = staticmethod(try_gdrive_delete)
