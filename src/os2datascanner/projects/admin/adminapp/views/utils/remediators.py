from django.db import IntegrityError
from os2datascanner.projects.admin.organizations.models import (
        Alias, Account, AliasType)
from ...models.scannerjobs.scanner import Scanner


def reconcile_remediators(rl: list[Account], scanner: Scanner):
    """Creates and deletes remediator Aliases as necessary to bring the
    given scanner's remediators in sync with the given list of Accounts."""
    scanner_pk = str(scanner.pk)
    existing_aliases = Alias.objects.filter(
            account__organization=scanner.organization,
            _alias_type=AliasType.REMEDIATOR.value,
            _value=scanner.pk)

    # XXX: this is not an efficient implementation of this, but a) does that
    # matter? and b) we want the extra sanity checks of AliasManager.create
    for e in existing_aliases:
        if e.account not in rl:
            e.delete()
    for acct in rl:
        try:
            Alias.objects.create(
                    account=acct,
                    _alias_type=AliasType.REMEDIATOR.value,
                    _value=scanner_pk)
        except IntegrityError:
            pass
