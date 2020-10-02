from django.db import models
from .rule_model import Rule
from ..scannerjobs.scanner_model import Scanner


class OrderedRule(models.Model):
    position = models.IntegerField(default=0)
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE)
    scanner_job = models.ForeignKey(Scanner, on_delete=models.CASCADE)

    class Meta:
        order_with_respect_to = 'scanner_job'
        unique_together = ['scanner_job', 'position']
