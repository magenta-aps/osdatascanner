from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from .grant import UsernamePasswordGrant


class SMBGrant(UsernamePasswordGrant):
    """A SMBGrant represents a service account with access to a Windows domain,
    and thereby an entitlement to access and scan that domain."""

    __match_args__ = ("domain", "username", "password",)

    domain = models.TextField(blank=True, verbose_name=_("Domain"))

    def validate(self):
        return True

    def __str__(self):
        return self.traditional_name

    @property
    def modern_name(self):
        """Returns the name of the service account as a modern Windows user
        principal name (of the form "person@example.org")."""
        return (f"{self.username}@{self.domain}"
                if self.domain else self.username)

    @property
    def traditional_name(self):
        """Returns the name of the service account as a traditional Windows
        down-level logon name (of the form "example.org\\person")."""
        # (that should be "example.org\person" with one backslash, but doc
        # comments are just strings and need to follow string rules)
        return (f"{self.domain}\\{self.username}"
                if self.domain else self.username)

    @property
    def verbose_name(self):
        return self._meta.verbose_name

    def clean(self):
        # We explicitly don't call the super class here, as that enforces a stricter clean method
        # than what we want here: Same username in different Windows domains are allowed.
        # Since we're using multi table inheritance, it is not possible to use database level
        # constraints on f.e. domain+username+organization (they reside in different tables).
        if self.domain and self.username:
            if SMBGrant.objects.filter(domain=self.domain,
                                       username=self.username,
                                       organization=self.organization,
                                       ).exclude(pk=self.pk).exists():
                raise ValidationError(_("A grant using this username and domain already exists."))

    class Meta:
        verbose_name = "SMB Service Account"
