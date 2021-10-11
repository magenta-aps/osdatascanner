from django import forms
from django.core.exceptions import ValidationError
from django.forms.models import ModelMultipleChoiceField
from os2datascanner.projects.admin.adminapp.models.authentication_model import Authentication
from os2datascanner.projects.admin.adminapp.models.rules.rule_model import Rule
from os2datascanner.projects.admin.adminapp.models.scannerjobs.filescanner_model import FileScanner

from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner_model import (
    Scanner,
)
from os2datascanner.projects.admin.adminapp.models.scannerjobs.webscanner_model import (
    WebScanner,
)
from django.utils.translation import ugettext_lazy as _

from os2datascanner.projects.admin.organizations.models import Organization

class ScannerForm(forms.ModelForm):
    class Meta:
        model = Scanner
        fields = [
            "name",
            "schedule",
            "rules",
            "organization",
            "validation_status",
            "do_last_modified_check",
        ]
    _request = None

    def __init__(self, request=None,*args, **kwargs) -> None:
        """
        Querysets used for choices in the 'domains' and 'rules' fields
        will be limited by the user's organization unless the user is a
        superuser.
        """
        super().__init__(*args, **kwargs)
        self._request = request
        user = request.user
        self.fields['schedule'].required = False
        org_qs = Organization.objects.none()
        if hasattr(user, 'administrator_for'):
            org_qs = Organization.objects.filter(
                client=user.administrator_for.client
            )
        elif user.is_superuser:
            org_qs = Organization.objects.all()
        
        self.fields['organization'].queryset = org_qs
        self.fields["rules"] = ModelMultipleChoiceField(
            Rule.objects.all(),
            validators=ModelMultipleChoiceField.default_validators)
        print(self._request)


    def is_valid(self) -> bool:

        user = self._request.user
        if not user.is_superuser:
            self.object = self.save(commit=False)
        
        # Makes sure authentication info gets stored in db.
        print(self.data)
        print(self.errors)
        return super().is_valid()


    def save(self, commit=True):
        domain = super().save(commit=False)

        #TODO is this necessary
        user = self._request.user
        if not user.is_superuser:
            self.object = super().save(commit=False)

        if domain.authentication:
            authentication = domain.authentication
        else:
            authentication = Authentication()
        
        if 'username' in self.cleaned_data:
            authentication.username = self.cleaned_data['username']
        if 'password' in self.cleaned_data:
            authentication.set_password(str(self.cleaned_data['password']))
        if 'domain' in self.cleaned_data:
            authentication.domain = self.cleaned_data['domain']

        authentication.save()
        domain.authentication = authentication
        return super().save(commit=commit)


class WebScannerForm(ScannerForm):
    url = forms.CharField(
        label="URL",
        widget=forms.TextInput(
            attrs={"placeholder": _("e.g. https://example.com/")}
        ),
    )
    exclude_urls = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("e.g. https://example.com/exclude1, https://example.com/exclude2")
            }
        )
    )

    class Meta(ScannerForm.Meta):
        model = WebScanner
        type = "web"
        fields = ScannerForm.Meta.fields + [
            "url",
            "exclusion_rules",
            "download_sitemap",
            "sitemap_url",
            "sitemap",
            "do_ocr",
            "do_link_check",
            "do_last_modified_check",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_url(self):
        url = self.cleaned_data["url"]
        if url and " " in url:
            raise ValidationError((_("Space is not allowed in the web-domain name.")))
        else: return url
