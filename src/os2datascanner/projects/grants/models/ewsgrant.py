from .grant import UsernamePasswordGrant


class EWSGrant(UsernamePasswordGrant):
    """An EWSGrant represents a service account with impersonation access to a
    traditional on-premises Microsoft Exchange instance.

    Note that EWSGrants can no longer be used to authenticate against Office
    365, but an appropriately configured GraphGrant can."""

    @property
    def verbose_name(self):
        return self._meta.verbose_name

    def __str__(self):
        return self.username

    class Meta(UsernamePasswordGrant.Meta):
        verbose_name = "EWS Service Account Grant"
