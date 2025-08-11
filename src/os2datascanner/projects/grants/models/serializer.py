from django.db import transaction

from os2datascanner.core_organizational_structure.serializer import BaseBulkSerializer


class BaseGrantBulkSerializer(BaseBulkSerializer):
    """ A list serializer that'll iterate objects and run create() on objects
     one at a time and return created objects instances.
     Sounds counterintuitive, but for Grants, that use multi-table inheritance, bulk_create
     cannot be used. """

    @transaction.atomic
    def create(self, validated_data):
        model = self.child.Meta.model
        instances = []
        for attrs in validated_data:
            instance = model.objects.create(**attrs)
            instances.append(instance)
        return instances
