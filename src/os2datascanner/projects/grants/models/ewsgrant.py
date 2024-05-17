from .grant import UsernamePasswordGrant


class EWSGrant(UsernamePasswordGrant):
    """An EWSGrant represents a service account with impersonation access to a
    traditional on-premises Microsoft Exchange instance.

    Note that EWSGrants can no longer be used to authenticate against Office
    365, but an appropriately configured GraphGrant can."""
