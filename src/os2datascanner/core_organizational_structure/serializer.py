from django.db import transaction
from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
    """ BaseSerializer is meant as a parent class.
    It can handle create and update operations on serialized models, but cannot do anything itself.

    Create operations require Meta model field to be set on child class. """

    def create(self, validated_data):
        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        interesting_keys = set(self.fields) & set(validated_data.keys())

        for k in interesting_keys:
            setattr(instance, k, validated_data[k])
        if interesting_keys:
            instance.save()

        return instance


class BaseBulkSerializer(serializers.ListSerializer):
    """ Parent class with support for bulk create & bulk update operations. """

    @transaction.atomic
    def create(self, validated_data):
        model = self.Meta.model
        objects = [model(**obj_attrs) for obj_attrs in validated_data]
        return model.objects.bulk_create(objects)

    @transaction.atomic
    def update(self, instances, validated_data):
        # TODO: Perhaps "fields" can be build smarter, in a way where we only look at fields
        # present in the received JSON object.
        model = self.Meta.model
        fields = [field.name for field in model._meta.fields if not field.primary_key]

        for instance, new_data in zip(instances, validated_data):
            for field, value in new_data.items():
                setattr(instance, field, value)

        model.objects.bulk_update(instances, fields)
        return instances


class SelfRelatingField(serializers.RelatedField):
    """ Usable for serializers for models which contain a self-relating foreign key.
    I.e. Account-Manager, or OrganizationalUnit-Parent"""

    def display_value(self, instance):
        return instance

    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        model = self.queryset.model
        return model(pk=data)
