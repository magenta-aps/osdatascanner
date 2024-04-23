# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# OS2datascanner is developed by Magenta in collaboration with the OS2 public
# sector open source network <https://os2.eu/>.
#

from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.managers import InheritanceManager

from .sensitivity_level import Sensitivity

from os2datascanner.engine2.rules.rule import Rule as E2Rule
from os2datascanner.engine2.rules.rule import Sensitivity as E2Sensitivity


_sensitivity_mapping = {
    Sensitivity.OK: E2Sensitivity.NOTICE,
    Sensitivity.LOW: E2Sensitivity.WARNING,
    Sensitivity.HIGH: E2Sensitivity.PROBLEM,
    Sensitivity.CRITICAL: E2Sensitivity.CRITICAL
}


class Rule(models.Model):
    objects = InheritanceManager()

    name = models.CharField(
        max_length=256,
        unique=True,
        null=False,
        verbose_name=_('name'),
    )

    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='rule',
        verbose_name=_('organization'),
        default=None,
        null=True,
    )

    description = models.TextField(
        verbose_name=_('description')
    )

    sensitivity = models.IntegerField(
        choices=Sensitivity.choices,
        default=Sensitivity.HIGH,
        verbose_name=_('sensitivity'),
    )

    @property
    def display_name(self):
        """The name used when displaying the regexrule on the web page."""
        return "Regel '%s'" % self.name

    def get_absolute_url(self):
        """Get the absolute URL for rules."""
        return '/rules/'

    def __str__(self):
        """Return the name of the rule."""
        return self.name

    def make_engine2_rule(self) -> E2Rule:
        """Construct an engine2 Rule corresponding to this Rule."""
        # (this can't use the @abstractmethod decorator because of metaclass
        # conflicts with Django, but subclasses should override this method!)
        raise NotImplementedError("Rule.make_engine2_rule")

    def make_engine2_sensitivity(self) -> E2Sensitivity:
        return _sensitivity_mapping[self.sensitivity]


class RuleCategory(models.Model):
    """Category for categorizing rules. For sorting purposes."""

    class CategoryNames(models.TextChoices):
        # Properties of the target scanned for
        NUMBER_ID = "number_id", _("number ID")
        NAMES = "names", _("names")
        ADDRESSES = "addresses", _("addresses")
        SICK_LEAVE = "sick_leave", _("sick leave")

        # Language
        DANISH = "danish", _("Danish")

    name = models.CharField(
        max_length=256,
        choices=CategoryNames.choices,
        verbose_name=_("name"),
        unique=True)

    @classmethod
    def populate(cls):
        existing = cls.objects.values_list("name", flat=True)
        for category in cls.CategoryNames.choices:
            if category not in existing:
                cls.objects.create(name=category)

    def __str__(self):
        return self.get_name_display()


class CustomRule(Rule):
    """CustomRule is an escape hatch that allows for the JSON representation of
    an arbitrary engine2 rule to be stored in the administration system's
    database."""

    _rule = models.JSONField(verbose_name=_('Rule'))

    categories = models.ManyToManyField(
        RuleCategory,
        verbose_name=_("categories"),
        related_name="rules")

    @property
    def rule(self):
        r = E2Rule.from_json_object(self._rule)
        if not r._name:
            r._name = self.name
        r._sensitivity = E2Sensitivity(max(
                # Technically speaking Sensitivity.INFORMATION is the lowest
                # value, but it's not possible to specify that in the UI
                r._sensitivity.value
                if r._sensitivity else E2Sensitivity.NOTICE.value,
                self.make_engine2_sensitivity().value))
        return r

    @rule.setter
    def set_rule(self, r: E2Rule):
        self._rule = r.to_json_object()

    def make_engine2_rule(self) -> E2Rule:
        return self.rule
