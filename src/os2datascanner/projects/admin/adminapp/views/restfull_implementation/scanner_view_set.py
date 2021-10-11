from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from os2datascanner.projects.admin.adminapp.models.scannerjobs.scanner_model import (
    Scanner,
)
from os2datascanner.projects.admin.adminapp.views.restfull_implementation.forms import (
    ScannerForm,
)
from os2datascanner.projects.admin.adminapp.views.restfull_implementation.scanner_serializer import (
    ScannerSerializer,
)
from os2datascanner.projects.admin.tests.test_scanner import User


class ScannerViewSet(AccessMixin ,viewsets.GenericViewSet):
    """
    A base implementation of a view set.
    """

    renderer_classes = [TemplateHTMLRenderer]
    form_class = ScannerForm
    serializer = ScannerSerializer
    model = Scanner
    template_name = None
    list_template_name = None
    type = "scan"


    def dispatch(self, request, *args, **kwargs):
        """ Validates the User
        As login mixin conflicts with GenericViewSet, and only contains this method, 
        the method have been implemented here
         """
        print('entering')
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    @property
    def queryset(self):
        return self.model.objects.all()

    def list(self, request):
        template_name = self.list_template_name
        response = Response(
            data=self.queryset,
            template_name=template_name,
        )
        response.data = {"scanner_list": response.data, "view": self}
        return response

    def retrieve(self, request, pk=None):
        queryset = self.model.objects.all()
        scan = get_object_or_404(queryset, pk=pk)
        response = Response(
            data=self.form_class( instance=scan, request=request ), template_name=self.template_name
        )
        response.data = {
            "form": response.data,
            "view": {"type": self.type},
        }
        return response

    def edit(self, request, pk=None):
        queryset = self.model.objects.all()
        scan = get_object_or_404(queryset, pk=pk)
        form = self.form_class(instance=scan, data=request.data, request=request)
        response = Response(template_name=self.template_name)
        # validate as form
        if form.is_valid():
            form.save()
            return self.list(request)
        else:
            response.status_code = status.HTTP_400_BAD_REQUEST
            response.data = {"form": form, "view": self}
        return response

    @action(methods=["post", "get"], detail=False)
    def add(self, request):
        response = Response(template_name=self.template_name)
        if request.method == "GET":
            response.data = {"form": self.form_class( request=request), "view": self}
            return response

        elif request.method == "POST":
            form = self.form_class(data=request.data, request=request)
            if form.is_valid():
                form.save()
                return self.list(request)
            else:
                response.status_code = status.HTTP_400_BAD_REQUEST
                response.data = {"form": form, "view": self}

            return response

    @action( methods=["get", "post"], detail=True)
    def delete(self, request, pk = None):
        scan = get_object_or_404(self.queryset, pk=pk)
        print('entering')
        scan.delete()
        return self.list(request)
