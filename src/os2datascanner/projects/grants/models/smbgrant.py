from django.db import models

from .grant import UsernamePasswordGrant


class SMBGrant(UsernamePasswordGrant):
    """A SMBGrant represents a service account with access to a Windows domain,
    and thereby an entitlement to access and scan that domain."""

    __match_args__ = ("domain", "username", "password",)

    domain = models.TextField(blank=True)

    def validate(self):
        return True

    def __str__(self):
        return (f"{self.domain}\\{self.username}"
                if self.domain else self.username)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                    fields=["organization", "domain", "username"],
                    name="%(app_label)s_%(class)s_unique")
        ]
