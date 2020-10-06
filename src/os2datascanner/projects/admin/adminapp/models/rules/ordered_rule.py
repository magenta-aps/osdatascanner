from django.db import models
from .rule_model import Rule
from ..scannerjobs.scanner_model import Scanner


class OrderedRule(models.Model):
    position = models.IntegerField(default=1)
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE)
    scanner_job = models.ForeignKey(Scanner, on_delete=models.CASCADE)

    class Meta:
        ordering = ['scanner_job']
        unique_together = ['scanner_job', 'position']

    def __repr__(self):
        return f"pk: {self.pk}, scannerjob: {self.scanner_job}, position: {self.position}"