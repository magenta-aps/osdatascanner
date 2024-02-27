from django.views.generic import TemplateView


class ManualMainView(TemplateView):
    template_name = "manual.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categorization"] = (self.request.user.account.organization.
                                     has_categorize_permission())
        return context
