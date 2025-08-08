from .grant import UsernamePasswordGrant, LazyOrganizationRelatedField
from os2datascanner.core_organizational_structure.serializer import BaseSerializer
from rest_framework.fields import UUIDField


class EWSGrant(UsernamePasswordGrant):
    """An EWSGrant represents a service account with impersonation access to a
    traditional on-premises Microsoft Exchange instance.

    Note that EWSGrants can no longer be used to authenticate against Office
    365, but an appropriately configured GraphGrant can."""

    @property
    def verbose_name(self):
        return self._meta.verbose_name

    def __str__(self):
        return self.username

    class Meta(UsernamePasswordGrant.Meta):
        verbose_name = "EWS Service Account"


class EWSGrantSerializer(BaseSerializer):
    organization = LazyOrganizationRelatedField(
        required=True,
        allow_null=False,
        pk_field=UUIDField(format='hex_verbose')
    )

    class Meta:
        model = EWSGrant
        fields = ["pk", "organization", "username", "_password"]


EWSGrant.serializer_class = EWSGrantSerializer
