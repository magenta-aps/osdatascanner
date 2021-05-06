from json import dumps
from pika.exceptions import AMQPError

from django.db.models import Q
from django.forms import ModelMultipleChoiceField

from .views import RestrictedListView, RestrictedCreateView, \
    RestrictedUpdateView, RestrictedDetailView, RestrictedDeleteView
from ..models.authentication_model import Authentication
from ..models.rules.rule_model import Rule
from ..models.scannerjobs.scanner_model import Scanner, ScanStatus
from ..models.userprofile_model import UserProfile


class StatusOverview(RestrictedListView):
    template_name = "os2datascanner/scan_status.html"
    model = ScanStatus

    def get_queryset(self):
        return super().get_queryset().order_by("-pk")


class StatusCompleted(RestrictedListView):
    template_name = "os2datascanner/scan_completed.html"
    model = ScanStatus

    def get_queryset(self):
        return super().get_queryset().order_by("-pk")


class ScannerList(RestrictedListView):
    """Displays list of scanners."""

    template_name = 'os2datascanner/scanners.html'
    context_object_name = 'scanner_list'

    def get_queryset(self):
        """Get queryset, don't include non-visible scanners."""
        qs = super().get_queryset()
        # Dismiss scans that are not visible
        qs = qs.filter(is_visible=True)
        return qs


class ScannerBase():
    template_name = 'os2datascanner/scanner_form.html'

    def get_form(self, form_class=None):
        """Get the form for the view.

        Querysets used for choices in the 'domains' and 'rules' fields
        will be limited by the user's organization unless the user is a
        superuser.
        """
        try:
            organization = self.request.user.profile.organization
        except UserProfile.DoesNotExist:
            organization = None

        form = super().get_form(form_class)

        if not self.request.user.is_superuser:
            self.filter_queryset(form, organization)

        form.fields['schedule'].required = False

        form.fields["rules"] = ModelMultipleChoiceField(
            Rule.objects.all(),
            validators=ModelMultipleChoiceField.default_validators)

        return form

    def get_form_fields(self):
        """Get the list of form fields.

        The 'validation_status' field will be added to the form if the
        user is a superuser.
        """
        fields = super().get_form_fields()
        if self.request.user.is_superuser:
            fields.append('validation_status')

        self.fields = fields
        return fields

    def filter_queryset(self, form, organization):
        for field_name in ['rules']:
            queryset = form.fields[field_name].queryset
            queryset = queryset.filter(organization=organization)
            form.fields[field_name].queryset = queryset

    def get_scanner_object(self):
        return self.get_object()

    def form_valid(self, form):
        if not self.request.user.is_superuser:
            user_profile = self.request.user.profile
            self.object = form.save(commit=False)
            self.object.organization = user_profile.organization

        """Makes sure authentication info gets stored in db."""
        domain = form.save(commit=False)
        if domain.authentication:
            authentication = domain.authentication
        else:
            authentication = Authentication()

        if 'username' in form.cleaned_data:
            authentication.username = form.cleaned_data['username']
        if 'password' in form.cleaned_data:
            authentication.set_password(str(form.cleaned_data['password']))
        if 'domain' in form.cleaned_data:
            authentication.domain = form.cleaned_data['domain']

        authentication.save()
        domain.authentication = authentication
        domain.save()

        return super().form_valid(form)


class ScannerCreate(ScannerBase, RestrictedCreateView):
    """View for creating a new scannerjob."""


class ScannerUpdate(ScannerBase, RestrictedUpdateView):
    """View for editing an existing scannerjob."""
    edit = True
    old_url = ''
    old_rules = None

    def get_form(self, form_class=None):
        """Get the form for the view.

        Querysets used for choices in the 'domains' and 'rules' fields
        will be limited by the user's organization unless the user is a
        superuser.
        """
        self.old_url = self.get_object().url
        # Store the existing rules selected in the scannerjob
        self.old_rules = self.object.rules.get_queryset()
        return super().get_form(form_class)

    def get_form_fields(self):
        """Get the list of form fields.

        The 'validation_status' field will be added to the form if the
        user is a superuser.
        """
        fields = super().get_form_fields()
        if self.request.user.is_superuser:
            fields.append('validation_status')

        self.fields = fields
        return fields

    def form_valid(self, form):
        """Validate the submitted form."""
        if self.old_url != self.object.url:
            self.object.validation_status = Scanner.INVALID
        # Compare the previous set of rules with new selection of rules
        if not set(self.old_rules) == set(form.cleaned_data["rules"]):
            # Reset last scanner-run timestamp if the rule sets differ
            self.object.e2_last_run_at = None
        return super().form_valid(form)


class ScannerDelete(RestrictedDeleteView):
    def get_form(self, form_class=None):
        """Adds special field password and decrypts password."""
        if form_class is None:
            form_class = self.get_form_class()

        return super().get_form(form_class)


class ScannerAskRun(RestrictedDetailView):
    """Base class for prompt before starting scan, validate first."""
    fields = []

    def get_context_data(self, **kwargs):
        """Check that user is allowed to run this scanner."""
        context = super().get_context_data(**kwargs)
        last_status = self.object.statuses.last()
        if self.object.validation_status is Scanner.INVALID:
            ok = False
            error_message = Scanner.NOT_VALIDATED
        elif not self.object.rules.all():
            ok = False
            error_message = Scanner.HAS_NO_RULES
        elif last_status and not last_status.finished:
            ok = False
            error_message = Scanner.ALREADY_RUNNING
        else:
            ok = True

        context['ok'] = ok
        if not ok:
            context['error_message'] = error_message

        return context


class ScannerRun(RestrictedDetailView):
    """Base class for view that handles starting of a scanner run."""

    template_name = 'os2datascanner/scanner_run.html'
    model = Scanner

    def __init__(self):
        self.object = None

    def get(self, request, *args, **kwargs):
        """Handle a get request to the view."""
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        try:
            context['scan_tag'] = dumps(
                    self.object.run(user=request.user), indent=2)
        except AMQPError as ex:
            context['pika_error'] = type(ex).__name__
        except Exception as ex:
            context['engine2_error'] = ", ".join([str(e) for e in ex.args])

        return self.render_to_response(context)
