from django.db import models
from .aliases.alias_model import Alias
from .documentreport_model import DocumentReport


class AliasMatchRelation(models.Model):
    alias = models.ForeignKey(Alias, on_delete=models.CASCADE)
    match = models.ForeignKey(DocumentReport, on_delete=models.CASCADE)

    @classmethod
    def create_relation(cls, alias, report):
        cls(alias=alias, match=report).save()

    class Meta:
        unique_together = ['alias', 'match']

    def __str__(self):
        return f'{self.alias} - {self.match}'
