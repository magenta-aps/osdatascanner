from django.views.generic import TemplateView

from ..models.roles.dpo import DataProtectionOfficer
from ..utils import convert_context_to_email_body


class ManualMainView(TemplateView):
    template_name = "manual.html"
