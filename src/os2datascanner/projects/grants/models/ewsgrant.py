from rest_framework import serializers
from .grant import UsernamePasswordGrant, LazyOrganizationRelatedField
from os2datascanner.core_organizational_structure.serializer import BaseSerializer
from rest_framework.fields import UUIDField
from .serializer import BaseGrantBulkSerializer


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


class EWSGrantBulkSerializer(BaseGrantBulkSerializer):

    class Meta:
        model = EWSGrant


class EWSGrantSerializer(BaseSerializer):
    # This is a bit confusing, but there's some difference in UUID and PK interpretations and
    # when what is available. Here we're just explicitly setting "pk" to be the value of UUID.
    pk = serializers.UUIDField(read_only=False, format="hex_verbose", source="uuid")
    organization = LazyOrganizationRelatedField(
        required=True,
        allow_null=False,
        pk_field=UUIDField(format='hex_verbose')
    )

    class Meta:
        model = EWSGrant
        fields = ["pk", "organization", "username", "_password"]
        list_serializer_class = EWSGrantBulkSerializer


EWSGrant.serializer_class = EWSGrantSerializer
