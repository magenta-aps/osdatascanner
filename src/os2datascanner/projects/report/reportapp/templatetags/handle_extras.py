import os
from urllib.parse import urlsplit

from django.apps import apps
from django import template
from django.conf import settings

from os2datascanner.engine2.model.core import Handle
from os2datascanner.engine2.model.smbc import SMBCHandle

from ..views.report_views import RENDERABLE_RULES
from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.filter
def present(handle):
    """Returns the presentation of the given Handle."""
    if isinstance(handle, Handle):
        return str(handle)
    else:
        return None


@register.filter
def present_url(handle, key=lambda h: h.presentation_url):
    """Returns the renderable presentation URL of the given Handle (or, if it
    doesn't define one, of its first parent that does).

    A "renderable presentation URL" is a presentation URL that isn't None and
    whose scheme is present in the PERMITTED_URL_SCHEMES setting."""

    def _test_handle(handle):
        url = key(handle)
        if url:
            scheme = urlsplit(url)[0]
            if scheme in settings.PERMITTED_URL_SCHEMES:
                return url
        return None
    if isinstance(handle, Handle):
        while not _test_handle(handle) and handle.source.handle:
            handle = handle.source.handle
        return _test_handle(handle)
    else:
        return None


@register.filter
def find_parent(handle, type_label):
    """If the given Handle's type label matches the argument, then returns it;
    otherwise, returns the first parent Handle with that appropriate type label
    (or None if there wasn't one)."""
    if isinstance(handle, Handle):
        while handle and handle.type_label != type_label:
            handle = handle.source.handle
        return handle
    else:
        return None


@register.filter
def find_type_label(handle):
    """Finds the top level handles type_label and then returns it;
    (or None if there wasn't one)."""
    if isinstance(handle, Handle):
        while handle and handle.type_label:
            if handle.source.handle:
                handle = handle.source.handle
            else:
                break
        return handle.source.type_label
    else:
        return None


@register.filter
def find_svg_icon(type_label):
    svg_dir = "components/svg-icons"
    full_path = os.path.join(
        os.path.join(apps.get_app_config('os2datascanner_report').path,
                     f"templates/{svg_dir}/"), f"icon-{type_label}.svg")
    return os.path.join(
        svg_dir, f"icon-{type_label}.svg") if os.path.exists(full_path) else \
        f"{svg_dir}/icon-default.svg"


@register.simple_tag
def find_scan_type(type_label):
    match type_label:
        case "smbc" | "dropbox" | "googledrive":
            return _("File")
        case "msgraph-files":
            return _("Microsoft 365 File")
        case "msgraph-teams-files":
            return _("MS Teams file")
        case "ews":
            return _("Exchange Mail")
        case "gmail":
            return _("Gmail")
        case "msgraph-mail" | "msgraph-mail-account":
            return _("Microsoft 365 Mail")
        case "web":
            return _("Web")
        case "msgraph-calendar":
            return _("Microsoft 365 Calendar")
        case "msgraph-lists":
            return _("MS SharePoint List")
        case _:
            return _("Unrecognized scan type")


@register.filter
def find_file_folder(handle):
    return present_url(handle, key=lambda h: h.container_url)


@register.filter
def present_folder(handle):
    """Removes the filename from the path and returns
    the folder path for copying
    """
    if isinstance(handle, SMBCHandle):
        if present(handle):
            file_path = present(handle)
            file_path = file_path[:file_path.rfind('\\')]
            return file_path
        else:
            return None
    return None


@register.filter
def between(lst, interval):
    if interval is None:
        interval = (0, 10)
    return lst[interval[0]:interval[1]]


@register.filter
def merge_renderable_match_fragments(match_fragments: list):
    """ Provided a list of MatchFragment objects, verifies
    that these contain matches of renderable rules.
    Merges together matches to one result if there are multiple MatchFragments objects."""

    # TODO: Refactor match.html and this. It is a bit hacky and fragile.
    match_fragments = [frag for frag in match_fragments
                       if frag.rule.type_label in RENDERABLE_RULES
                       and frag.matches]

    match match_fragments:
        case []:
            return None
        case [one]:
            return one
        case [first, *rest]:
            merged_fragment = first
            return merged_fragment.matches.extend(
                match
                for fragment in rest
                for match in fragment.matches
            )
