from django.db import models


class CoveredAccount(models.Model):
    scanner = models.ForeignKey(
            'os2datascanner.Scanner', null=False, on_delete=models.CASCADE)
    account = models.ForeignKey(
            'organizations.Account', null=False, on_delete=models.CASCADE)
