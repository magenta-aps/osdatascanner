from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model


UserModel = get_user_model()


class CustomPasswordResetForm(PasswordResetForm):
    def get_users(self, email):
        filters = Q(email__iexact=email)
        # Workaround to make it function in both admin and report.
        # Admin module has no such relation.
        if 'account' in [f.name for f in UserModel._meta.get_fields()]:
            filters |= Q(account__email__iexact=email)

        return UserModel.objects.filter(filters, is_active=True).distinct()

    def save(
        self,
        domain_override=None,
        subject_template_name="registration/password_reset_subject.txt",
        email_template_name="registration/password_reset_email.html",
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        email = self.cleaned_data["email"]
        if not domain_override:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain
        else:
            site_name = domain = domain_override
        for user in self.get_users(email):
            # Again, admin has no User.account - but report does.
            user_email = getattr(getattr(user, 'account', None), 'email', user.email)
            context = {
                "email": user_email,
                "domain": domain,
                "site_name": site_name,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "user": user,
                "token": token_generator.make_token(user),
                "protocol": "https" if use_https else "http",
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name,
                email_template_name,
                context,
                from_email,
                user_email,
                html_email_template_name=html_email_template_name,
            )


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    email_template_name = "registration/password_reset_email.html"
    html_email_template_name = "components/feedback/password_reset_email.html"
    subject_template_name = "registration/password_reset_subject.txt"
