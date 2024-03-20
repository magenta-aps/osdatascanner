from django.views.generic import TemplateView


class ManualMainView(TemplateView):
    template_name = "manual.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization = self.request.user.account.organization
        context["categorization"] = organization.has_categorize_permission()
        context["file_delete"] = organization.has_file_delete_permission()
        return context
