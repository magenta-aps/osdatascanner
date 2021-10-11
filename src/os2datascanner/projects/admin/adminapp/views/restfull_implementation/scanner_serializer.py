from rest_framework import serializers
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner_model import (
    Scanner,
)


class ScannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scanner
        fields = ['name']
