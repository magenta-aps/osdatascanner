from django.db import models


class CoveredAccount(models.Model):
    scanner = models.ForeignKey(
            'os2datascanner.Scanner', null=False, on_delete=models.CASCADE)
    account = models.ForeignKey(
            'organizations.Account', null=False, on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['scanner', 'account'],
            name='os2datascanner_scanner_c_scanner_id_account_id_ec9ff164_uniq')]
