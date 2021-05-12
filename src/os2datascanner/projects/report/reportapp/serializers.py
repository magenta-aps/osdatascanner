from rest_framework import serializers
from .models.documentreport_model import DocumentReport

class DocumentReportSerializers(serializers.ModelSerializer):
	class Meta:
	    model = DocumentReport
	    fields = '__all__'