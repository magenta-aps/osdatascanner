import re
from copy import deepcopy
import json
import hashlib
import warnings
from time import sleep
import structlog

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import SuspiciousOperation
from django.db.models import Q
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from mozilla_django_oidc import auth
from django.utils.translation import gettext_lazy as _

from os2datascanner.engine2.pipeline import messages
from .models.documentreport import DocumentReport

from os2datascanner.engine2.utilities.equality import TypePropertyEquality
from os2datascanner.projects.report.organizations.models import (
    Alias, AliasType, Organization, Account)

from mozilla_django_oidc.views import OIDCAuthenticationCallbackView

logger = structlog.get_logger("reportapp")


def convert_context_to_email_body(request):
    body = _("%0D%0A%0D%0A--- Do not alter text below this line! ---%0D%0A")
    body += f"User: {request.user.username}%0D%0A"

    return body


def relate_matches_to_user(user, account, value, alias_type):
    """
    Relates all relevant matches to the user through its aliases.
    """
    if alias_type == AliasType.EMAIL:
        aliases = Alias.objects.filter(user=user, _value__iexact=value, _alias_type=alias_type)
    else:
        aliases = Alias.objects.filter(user=user, _value=value, _alias_type=alias_type)

    if not aliases:
        alias = Alias.objects.create(user=user, account=account,
                                     _value=value, _alias_type=alias_type)
        create_alias_and_match_relations(alias)

    elif aliases:
        # A user shouldn't have duplicated aliases... This is solely to prevent SSO from
        # failing in case one does - and delete duplicates.
        alias = aliases.first()

        if aliases.count() > 1:
            aliases.exclude(pk=alias.pk).delete()

        aliases.update(account=account)
        create_alias_and_match_relations(alias)


def hash_handle(handle: dict) -> str:
    """
    Creates a SHA-512 hash value from the handle string
    and returns the hex value.
    :param handle: handle as json object
    :return: SHA-512 hex value
    """
    handle = deepcopy(handle)

    source = handle.get("source")
    while source:
        if "scan_deleted_items_folder" in source:
            del source["scan_deleted_items_folder"]
        if "scan_syncissues_folder" in source:
            del source["scan_syncissues_folder"]
        source = source.get("handle", {}).get("source")

    return hashlib.sha512(json.dumps(handle).encode()).hexdigest()


def crunch_hash(t: TypePropertyEquality) -> str:
    warnings.warn(
            ("crunch_hash is deprecated;"
             " use TypePropertyEquality.crunch directly"),
            DeprecationWarning,
            stacklevel=2)
    return t.crunch(hash="sha512")


def crunch(t: TypePropertyEquality) -> str:
    warnings.warn(
            ("crunch is deprecated;"
             " use TypePropertyEquality.crunch directly"),
            DeprecationWarning,
            stacklevel=2)
    return t.crunch()


def get_or_create_user_aliases(user_data):  # noqa: D401
    """Hook called after user is created, during SAML login, in DB and before login.
    This method creates or updates the users aliases depending on if new user_data
    has arrived or the old the user_data has been updated.

    The django-saml plugin takes care of the basic user_data such as email, username etc.
    So we do not need to worry about creating or updating the django user."""

    saml_attr = settings.SAML2_AUTH.get('ATTRIBUTES_MAP')

    username = get_user_data(saml_attr.get('username'), user_data, str)
    email = get_user_data(saml_attr.get('email'), user_data, str)
    sid = get_user_data(saml_attr.get('sid'), user_data, str)
    user = User.objects.get(username=username)

    # When the user signs in with SSO, create an account if one does not exist.
    # This only works if there is only one organization in the database.
    account = Account.objects.filter(user=user).first()
    if not account:
        if Organization.objects.count() == 1:
            related_org = Organization.objects.first()
        else:
            raise RuntimeError("Was not able to determine correct Organization for the user!")
        account = Account.objects.create(
                organization=related_org,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name)

    if email:
        relate_matches_to_user(user, account, email, AliasType.EMAIL)

    if sid:
        relate_matches_to_user(user, account, sid, AliasType.SID)


def user_is(roles, role_cls):
    """Checks whether a list of roles contains a certain role type (role_cls)"""
    return any(isinstance(role, role_cls)
               for role in roles)


class OIDCCallback(OIDCAuthenticationCallbackView):
    # Relates to this issue: https://github.com/mozilla/mozilla-django-oidc/issues/435
    # and is merely an attempt to give time enough for the session to be saved.

    def get(self, request, *args, **kwargs):
        # We don't _actually_ want this in the authentication request
        retry_counter = int(request.GET.get('retry_counter', "0"))

        try:
            return super().get(request)

        except SuspiciousOperation:
            if retry_counter > 2:
                self.request.oidc_error_text = _(
                        "It appears that the one-time authentication token"
                        " issued by your organisation's identity provider has"
                        " already been used. Please start the log-in process"
                        " again.")
                self.request.oidc_try_again = True
                return self.login_failure()

            new_query = request.GET.copy()
            new_query["retry_counter"] = retry_counter + 1
            logger.warning("SSO failed, sleeping 1s and redirecting to try again! ",
                           retry_counter=retry_counter,
                           exc_info=True
                           )
            sleep(1)
            logger.warning("Slept 1 second. Redirecting ...")
            return redirect(request.path + "?" + new_query.urlencode())

    def login_failure(self):
        return TemplateResponse(
                self.request, "error_pages/oidc-login-error.html", status=403)


class OIDCAuthenticationBackend(auth.OIDCAuthenticationBackend):
    def get_userinfo(self, access_token, id_token, payload):
        # Stash the user info in the request so we have access to it in an
        # error situation
        ui = super().get_userinfo(access_token, id_token, payload)
        self.request.user_info = ui
        return ui

    def filter_users_by_claims(self, claims):
        """ Defines how the OIDC process is supposed to identify Django-users by claims."""

        username = claims.get('preferred_username')
        if not username:
            self.request.oidc_error_text = _(
                    "Your organisation's identity provider did not send"
                    " a username for your account to OSdatascanner.")
            return self.UserModel.objects.none()

        try:
            account = Account.objects.get(user__username__iexact=username)
            return [account.user]

        except Account.DoesNotExist:
            self.request.oidc_error_text = _(
                    "No account could be found that matched the username"
                    " sent by your organisation's identity provider.")
            return self.UserModel.objects.none()

    def create_user(self, claims):
        username = claims.get('preferred_username')
        first_name = claims.get("given_name", "")
        last_name = claims.get("family_name", "")
        email = claims.get("email", "")
        sid = claims.get("objectSid", "")

        # Also slight copy pasta from SAML implementation - and we still have the flaw
        # of not being able to deal with multiple Organizations
        if Organization.objects.count() == 1:
            related_org = Organization.objects.first()
            account = Account.objects.create(
                username=username, first_name=first_name, last_name=last_name, email=email,
                organization=related_org
            )

            user = account.user
            if email:
                relate_matches_to_user(user, account, email, AliasType.EMAIL)

            if sid:
                relate_matches_to_user(user, account, sid, AliasType.SID)

        else:
            raise RuntimeError("Was not able to determine correct Organization for the user!")

        return user

    def update_user(self, user, claims):
        # TODO: handle name updates, for when creation of user is allowed(?)
        # first_name = claims.get("given_name", "") <-- unused, but available like so.
        # last_name = claims.get("family_name", "")
        email = claims.get("email", "")
        sid = claims.get("objectSid", "")

        # Todo: This is copy pasta from SAML implementation, end goal is removing SAML.
        # When the user signs in with SSO, create an account if one does not exist.
        # This only works if there is only one organization in the database.
        account = Account.objects.filter(user=user).first()
        if not account:
            if Organization.objects.count() == 1:
                related_org = Organization.objects.first()
            else:
                raise RuntimeError("Was not able to determine correct Organization for the user!")
            account = Account.objects.create(
                organization=related_org,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name)

        if email:
            relate_matches_to_user(user, account, email, AliasType.EMAIL)

        if sid:
            relate_matches_to_user(user, account, sid, AliasType.SID)

        return user


def get_user_data(key: str, user_data: dict, expected_type: type):
    """Helper method for retrieving data for a given key."""
    # For reasons of backwards compatibility / paranoia, this function supports
    # both the original django-saml2-auth data format (where user_data is a
    # dict of lists of values) and that of the grafana/django-saml2-auth fork
    # (where user_data is a plain dict of values with the dict of lists stashed
    # under the user_identity key)
    match user_data.get(key):
        case None:
            logger.warning(
                    "no value available for the given key",
                    key=key, user_data=user_data, expected_type=expected_type)
            return None
        case v if isinstance(v, expected_type):  # grafana/django-saml2-auth
            return v
        case [v, *rest] if isinstance(v, expected_type):  # original behaviour
            if rest:
                logger.info(
                        "multiple values available for the given key,"
                        " using the first one",
                        key=key, value=v)
            return v
        case v:
            logger.warning(
                    "value of the wrong type or shape",
                    key=key, value=v, expected_type=expected_type)
            return None


def iterate_queryset_in_batches(batch_size, queryset):
    """Yields everything in the given QuerySet in batches of at most
    batch_size objects.

    This function behaves appropriately when the caller modifies batches in a
    way that shrinks the size of the input QuerySet."""
    # Make sure the QuerySet is ordered -- slicing (i.e., OFFSET/LIMIT in the
    # underlying SQL statement) is otherwise not well-defined
    # (XXX: should we just always impose this ordering in order to make the
    # offset trickery below safer?)
    if not queryset.ordered:
        queryset = queryset.order_by("pk")
    i = 0
    total_count = queryset.count()
    while i < total_count:
        batch = queryset[i: batch_size + i]
        batch_count = batch.count()
        yield batch

        # The operations performed by the caller might have reduced the size of
        # the QuerySet. If that has happened, then reduce the new database
        # offset so that we don't skip over any objects
        new_total = queryset.count()
        count_diff = new_total - total_count
        i += batch_count
        if count_diff < 0:
            i += count_diff
        total_count = new_total


def get_max_sens_prop_value(doc_report_obj, key):
    """Helper method for migration 0017_documentreport_added_sensitivity_and_probability.
    This method returns either a Sensitivity object or probability maximum value.
    The method is located in utils as could become handy else where."""
    warnings.warn(
            ("get_max_sens_prop_value is deprecated;"
             " use DocumentReport.matches directly"),
            DeprecationWarning,
            stacklevel=2)

    if not hasattr(doc_report_obj, "data"):
        if doc_report_obj.matches:
            return getattr(doc_report_obj.matches, key)
    else:
        if (doc_report_obj.data
                and "matches" in doc_report_obj.data
                and doc_report_obj.data["matches"]):
            return getattr(messages.MatchesMessage.from_json_object(
                doc_report_obj.data["matches"]), key)


def create_alias_and_match_relations(sub_alias: Alias) -> int:
    """Method for creating match_relations for a given alias
    with all the matching DocumentReports"""
    tm = Alias.match_relation.through
    # We're using "only" here in combination with iterator later, to avoid
    # running into RAM issues on large datasets. DocumentReports can be many and they can be large.
    all_reports = DocumentReport.objects.only("pk", "alias_relation")

    # Although RFC 5321 says that the local part of an email address
    # -- the bit to the left of the @ --
    # is case sensitive, the real world disagrees..
    if sub_alias.alias_type == AliasType.EMAIL:
        reports = all_reports.filter(owner__iexact=sub_alias.value)
    else:
        reports = all_reports.filter(owner=sub_alias.value)

    # If we've found reports above, we should make sure no remediator alias exist
    # for those.
    if reports:
        tm.objects.filter(documentreport_id__in=reports,
                          alias___alias_type=AliasType.REMEDIATOR).delete()
    elif not reports and sub_alias.alias_type == AliasType.REMEDIATOR:
        remediator_for = sub_alias.value

        if remediator_for == "0":  # Remediator for all scannerjobs, becomes a string,
            reports = all_reports.filter(
                (Q(alias_relation__isnull=True) |
                 Q(alias_relation___alias_type=AliasType.REMEDIATOR.value))
            )

        else:  # Remediator for a specific scannerjob
            reports = all_reports.filter(
                (Q(alias_relation__isnull=True) |
                 Q(alias_relation___alias_type=AliasType.REMEDIATOR.value)) &
                Q(scanner_job_pk=remediator_for)
            )

    tm_create_list = []
    for i, report in enumerate(reports.iterator(chunk_size=2000)):
        tm_create_list.append(tm(documentreport_id=report.pk, alias_id=sub_alias.pk))

        if i % 2000 == 0 and tm_create_list:
            tm.objects.bulk_create(tm_create_list, ignore_conflicts=True)
            tm_create_list.clear()

    if tm_create_list:
        tm.objects.bulk_create(tm_create_list, ignore_conflicts=True)

    return reports.count()


def get_msg(query):
    """ Utility function used in get_presentation,
        which is used in migration 0033_add_sort_key_and_name_charfield
        and in management command refresh_sort_key.
        """
    old_db = hasattr(query, "data")

    # only one of these are not None
    matches = query.data.get("matches") if old_db else query.raw_matches
    metadata = query.data.get("metadata") if old_db else query.raw_metadata
    problem = query.data.get("problem") if old_db else query.raw_problem

    if matches:
        return messages.MatchesMessage.from_json_object(matches)
    elif problem:
        problem = messages.ProblemMessage.from_json_object(problem)
        # problemMessage have optional handle and source fields. Try the latter if
        # the first is None.
        if not problem.handle:
            problem = problem.source if problem.source else problem
        return problem
    elif metadata:
        return messages.MetadataMessage.from_json_object(metadata)
    else:
        return None


def get_presentation(query):
    """ Utility function used in used in migration 0033_add_sort_key_and_name_charfield
        and in management command refresh_sort_key.
        Returns handle of a message"""

    type_msg = get_msg(query)
    if not type_msg:
        return ""

    return type_msg.handle if type_msg.handle else ""


def prepare_json_object(o):
    """Processes an object suitable for JSON serialisation to make it suitable
    for storing in the OS2datascanner report module's database. (At the moment
    this just means removing all null bytes and PEP 383 surrogate pairs from
    string values, as PostgreSQL can't deal with them in any string or JSON
    data type.)"""
    if isinstance(o, dict):
        return {prepare_json_object(k): prepare_json_object(v)
                for k, v in o.items()}
    elif isinstance(o, (list, tuple)):
        return [prepare_json_object(i) for i in o]
    elif isinstance(o, str):
        if "\0" in o:
            warnings.warn(
                    "stripping null byte for PostgreSQL compatibility",
                    UnicodeWarning)
            o = o.replace("\0", "")
        if re.search(r'[\uD800-\uDFFF]', o):
            warnings.warn(
                    "stripping illegal surrogates for PostgreSQL compatibility",
                    UnicodeWarning)
            o = re.sub(r'[\uD800-\uDFFF]', '\ufffd', o)
        return o
    else:
        return o
