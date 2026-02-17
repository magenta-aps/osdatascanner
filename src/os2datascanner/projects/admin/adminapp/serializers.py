# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

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
                'graph_grant',
                'organization')
