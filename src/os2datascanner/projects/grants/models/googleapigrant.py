import json
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from .grant import Grant, wrap_encrypted_field, LazyOrganizationRelatedField
from os2datascanner.core_organizational_structure.serializer import BaseSerializer
from rest_framework.fields import UUIDField


class GoogleApiGrant(Grant):
    """"
    A GoogleApiGrant represents credentials for a service account with
    authorization to access the Google API.
    """

    __match_args__ = ("service_account",)

    _service_account = models.JSONField(null=True, verbose_name=_("Service account json"))

    service_account = wrap_encrypted_field("_service_account")

    class Meta:
        verbose_name = _("Google Api Grant")

    def __str__(self):
        return self.account_name

    def clean(self):
        super().clean()
        if self._service_account:
            self.validate_service_account()
            google_api_grant_names = [
                google_api_grant.account_name for google_api_grant in GoogleApiGrant.objects.filter(
                    organization=self.organization) if google_api_grant.pk != self.pk]
            if self.account_name in google_api_grant_names:
                raise ValidationError(_("A grant using this service account already exists."))
        else:
            raise ValidationError(_("Service account is required"))

    @property
    def verbose_name(self):
        return self._meta.verbose_name

    @property
    def account_name(self):
        return json.loads(self.service_account).get("client_email").split("@")[0]

    def validate_service_account(self):
        try:
            service_account = json.loads(self.service_account)
        except json.JSONDecodeError:
            raise ValidationError(_("Service account must be in JSON format"))

        for key in [
            "type",
            "project_id",
            "private_key_id",
            "private_key",
            "client_email",
            "client_id",
            "auth_uri",
            "token_uri"
        ]:
            if key not in service_account:
                raise ValidationError(_("Invalid service account"))


class GoogleApiGrantSerializer(BaseSerializer):
    organization = LazyOrganizationRelatedField(
        required=True,
        allow_null=False,
        pk_field=UUIDField(format='hex_verbose')
    )

    class Meta:
        model = GoogleApiGrant
        fields = ["pk", "organization", "service_account"]


GoogleApiGrant.serializer_class = GoogleApiGrantSerializer
