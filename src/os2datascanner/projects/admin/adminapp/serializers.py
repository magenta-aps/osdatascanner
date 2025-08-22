from .models.MSGraphSharePointSite import MSGraphSharePointSite
from rest_framework import serializers
from ..organizations.models import OrganizationalUnit


class OrganizationalUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationalUnit
        fields = (
            'uuid',
            'name',
            'tree_id',
            'level',
            'parent',
            'organization',
            'scanners')


class SharePointSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MSGraphSharePointSite
        fields = (
                'id',
                'uuid',
                'name',
                'graph_grant')
