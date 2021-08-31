from rest_framework import serializers
from ..organizations.models import OrganizationalUnit

class OrganizationalUnitSerializer(serializers.ModelSerializer):
	class Meta:
		model = OrganizationalUnit
		fields = ('uuid', 'name', 'lft', 'rght', 'tree_id', 'level', 'parent',
				  'organization')
		# Maybe lft and rght not needed?

		# Reasoning behind not trying to serialize mptt model.
		# https://stackoverflow.com/questions/30817031/in-django-how-to-serialize-mptt-tree
