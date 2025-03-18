from django.forms import ModelChoiceField
from django.http import HttpResponse
from django.template.loader import render_to_string
from utilities import UserWrapper


class GrantMixin:
    """Mixin for dynamic grant form support."""

    def get_grant_form_classes(self) -> dict:
        """Override this method to return a dictionary of grant
         form classes and their corresponding field."""
        raise NotImplementedError("Subclasses should implement this method.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.is_htmx = self.request.headers.get('HX-Request')

        if self.is_htmx == "true":
            field_name = self.request.GET.get("grant_type")
            GrantFormClass = self.get_grant_form_classes().get(field_name)

            if GrantFormClass:
                context["grant_form"] = GrantFormClass(
                    prefix=field_name,
                    initial={"organization": self.request.GET.get("organization")}
                    )

        return context

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()

        form = super().get_form(form_class)
        user = UserWrapper(self.request.user)

        for field_name, GrantFormClass in self.get_grant_form_classes().items():
            grant_qs = GrantFormClass.Meta.model.objects.filter(user.make_org_Q())
            # Conditionally required. Should be required when there's only one option, but can't
            # be, when there's two or more. (F.e. ExchangeScanner)
            form.fields[field_name] = ModelChoiceField(grant_qs, empty_label=None,
                                                       label=form.fields[field_name].label,
                                                       required=False if
                                                       len(self.get_grant_form_classes()) >= 2
                                                       else True)

        return form

    def post(self, request, *args, **kwargs):
        self.is_htmx = request.headers.get('HX-Request')

        if self.is_htmx == "true":
            context = {}
            response = HttpResponse()
            scanner_form = self.get_form()

            field_name = request.POST.get("grant_type")
            GrantFormClass = self.get_grant_form_classes().get(field_name)

            grant_form = GrantFormClass(request.POST, prefix=field_name)

            if request.FILES:
                grant_form.files = request.FILES

            if grant_form.is_valid():
                grant = grant_form.save()
                scanner_form.data = scanner_form.data.copy()
                scanner_form.data[field_name] = grant.id

                grant_field = scanner_form[field_name]
                response.write(
                    render_to_string(
                        "components/scanner/scanner_form_select_option_field.html",
                        {
                            "field": grant_field,
                            "selected_value": grant.id,
                        },
                        request=request
                    )
                )
                return response

            context["grant_form"] = grant_form
            context["form"] = scanner_form
            return self.render_to_response(context)

        return super().post(request, *args, **kwargs)
