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

import structlog

from django.db import models
from django.db.models.signals import pre_save
from django.utils.translation import gettext as _
from django.dispatch import receiver
from model_utils.managers import InheritanceManager

from .sensitivity_level import Sensitivity

from os2datascanner.engine2.rules.rule import Rule as E2Rule
from os2datascanner.engine2.rules.rule import Sensitivity as E2Sensitivity


logger = structlog.get_logger("adminapp")


class RuleCategory(models.Model):

    name_desc_map = {
        # Properties of the target scanned for
        "number_id": {
            "name": _("number ID"),
            "description": _("Bla bla bla")
        },
        "names": {
            "name": _("names"),
            "description": _("Names names names")
        },
        "addresses": {
            "name": _("addresses"),
            "description": _("Where are you from??")
        },
        "sick_leave": {
            "name": _("sick leave"),
            "description": _("Messages about sick leave")
        },
        # Languages
        "danish": {
            "name": _("Danish"),
            "description": _("Sources in Danish")
        }
    }

    identifier = models.CharField(
        max_length=256,
        verbose_name=_("identifier"),
        primary_key=True,
        choices=[(k, v["name"]) for k, v in name_desc_map.items()]
    )

    @property
    def name(self):
        return self.name_desc_map[self.identifier]["name"]

    @property
    def description(self):
        return self.name_desc_map[self.identifier]["description"]

    def __str__(self):
        return self.name


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
        related_name='rules',
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

    raw_rule = models.JSONField(
        verbose_name=_("Rule"),
        null=True, blank=True)

    categories = models.ManyToManyField(
        RuleCategory,
        verbose_name=_("categories"),
        related_name="rules"
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
        r = E2Rule.from_json_object(self.raw_rule)
        if not r._name:
            r._name = self.name
        r._sensitivity = E2Sensitivity(max(
                # Technically speaking Sensitivity.INFORMATION is the lowest
                # value, but it's not possible to specify that in the UI
                r._sensitivity.value
                if r._sensitivity else E2Sensitivity.NOTICE.value,
                self.make_engine2_sensitivity().value))
        return r

    def make_engine2_sensitivity(self) -> E2Sensitivity:
        return _sensitivity_mapping[self.sensitivity]

    @receiver(pre_save)
    def patch_references(sender, instance, *args, **kwargs):
        """Resolves any references present in the JSON representation of this
        Rule before it is saved.

        A reference is a dictionary containing a {"!ref": ?pk} key-value pair,
        where ?pk is an integer primary key of another Rule object. This pair
        will be deleted and replaced with the JSON representation of the Rule
        identified by ?pk.

        (Note that other keys in the reference dictionary will be preserved,
        and will overwrite keys in the other Rule's JSON representation.)

        A reference dictionary referring to a Rule not present in the database
        will cause a Django Rule.DoesNotExist exception to be raised."""
        if not isinstance(instance, Rule):
            return

        def do_patch_refs(o):
            match o:
                case {"!ref": identifier, **rest}:
                    logger.info(
                            "resolving Rule cross-reference",
                            instance=instance,
                            referenced_pk=identifier)
                    return Rule.objects.get(pk=identifier).raw_rule | rest
                case list():
                    return [do_patch_refs(el) for el in o]
                case dict():
                    return {key: do_patch_refs(val) for key, val in o.items()}
                case _:
                    return o

        instance.raw_rule = do_patch_refs(instance.raw_rule)
